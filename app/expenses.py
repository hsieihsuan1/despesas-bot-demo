"""Synthetic local ledger. Integer cent amounts, no network or financial advice."""
import re
import sqlite3
import uuid
from calendar import monthrange
from datetime import date
from decimal import Decimal, InvalidOperation
from .rules import apply_rules_from_sheet

OPTIONS = {"tipo_keywords": {"mercado": "Alimentação", "cafe": "Alimentação", "onibus": "Transporte", "livro": "Educação"}}

def amount_cents(value):
    if not isinstance(value, str) or not re.fullmatch(r"(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d{1,2})?", value):
        raise ValueError("Use um valor em reais, como 45 ou 1.234,56.")
    try:
        amount = Decimal(value.replace(".", "").replace(",", "."))
    except InvalidOperation:
        raise ValueError("Valor inválido.")
    cents = int(amount * 100)
    if not 0 < cents <= 100_000_000:
        raise ValueError("Valor fora do limite demonstrativo.")
    return cents

def parse_expense(text, ref_date):
    if not isinstance(text, str) or len(text) > 1000:
        raise ValueError("Mensagem deve ter até 1000 caracteres.")
    # Deliberately restricted grammar: no guessing among several amounts/dates.
    m = re.fullmatch(r"\s*gastei\s+(?:R\$\s*)?([\d.,]+)\s+(?:no|na|em)\s+(.+?)(?:\s+em\s+(\d{1,2})x)?\s*", text, re.I)
    if not m:
        raise ValueError("Use: gastei 45 no mercado (opcional: em 3x).")
    cents = amount_cents(m[1]); description = m[2].strip()
    if re.search(r"\d", description) or not description or len(description) > 160:
        raise ValueError("Descrição curta sem números; use só um valor na mensagem.")
    installments = int(m[3] or 1)
    if not 1 <= installments <= 12 or cents < installments:
        raise ValueError("Parcelas devem ficar entre 1 e 12, com pelo menos um centavo cada.")
    category = apply_rules_from_sheet(description, OPTIONS).get("tipo", "Outros")
    quotient, remainder = divmod(cents, installments)
    rows=[]
    for i in range(installments):
        offset=ref_date.month-1+i; year=ref_date.year+offset//12; month=offset%12+1
        day=min(ref_date.day,monthrange(year,month)[1])
        rows.append({"date":date(year,month,day).isoformat(),"description":description,"category":category,"cents":quotient+(i<remainder),"installment":f"{i+1}/{installments}"})
    return rows

def month_bounds(period):
    if not isinstance(period, str) or not re.fullmatch(r"\d{4}-\d{2}",period):
        raise ValueError("Período deve ser AAAA-MM.")
    year,month=map(int,period.split("-"));date(year,month,1)
    return date(year,month,1).isoformat(), date(year,month,monthrange(year,month)[1]).isoformat()

def brl(cents):
    return f"R$ {cents//100:,}".replace(",", ".")+f",{cents%100:02d}"

class Ledger:
    def __init__(self,path=":memory:"):
        self.db=sqlite3.connect(path,check_same_thread=False)
        self.db.row_factory=sqlite3.Row
        self.db.executescript("CREATE TABLE IF NOT EXISTS expenses(id TEXT, request_id TEXT, date TEXT, description TEXT, category TEXT, cents INTEGER CHECK(cents>0), installment TEXT); CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY);")
    def record(self,rows,request_id):
        if not isinstance(request_id,str) or not re.fullmatch(r"[a-zA-Z0-9-]{1,80}",request_id):raise ValueError("Identificador inválido.")
        with self.db:
            if self.db.execute("SELECT 1 FROM requests WHERE id=?",(request_id,)).fetchone():return False
            self.db.execute("INSERT INTO requests VALUES (?)",(request_id,))
            for row in rows:
                self.db.execute("INSERT INTO expenses VALUES (?,?,?,?,?,?,?)",(uuid.uuid4().hex,request_id,row['date'],row['description'],row['category'],row['cents'],row['installment']))
        return True
    def consult(self,period):
        start,end=month_bounds(period)
        rows=[dict(r) for r in self.db.execute("SELECT date,description,category,cents,installment FROM expenses WHERE date BETWEEN ? AND ? ORDER BY date,id",(start,end))]
        categories={}
        for row in rows: categories[row['category']]=categories.get(row['category'],0)+row['cents']
        return {"rows":rows,"total_cents":sum(r['cents'] for r in rows),"categories":categories}
    def seed(self):
        self.record(parse_expense("gastei 45 no mercado",date(2026,10,8)),"synthetic-market")
        self.record(parse_expense("gastei 12,50 no ônibus",date(2026,10,8)),"synthetic-bus")
