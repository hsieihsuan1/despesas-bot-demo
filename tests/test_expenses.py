import unittest
from datetime import date
from app.expenses import amount_cents,parse_expense,month_bounds,Ledger
class ExpenseTests(unittest.TestCase):
    def test_brl(self):self.assertEqual(amount_cents('1.234,56'),123456)
    def test_integer(self):self.assertEqual(amount_cents('45'),4500)
    def test_decimal(self):self.assertEqual(amount_cents('7,5'),750)
    def test_invalid_amounts(self):
        for x in ['0','-5','1.23','nan','1e8','1000001','1,234',None]:
            with self.subTest(x=x),self.assertRaises(ValueError):amount_cents(x)
    def test_category(self):self.assertEqual(parse_expense('gastei 7,50 no café',date(2026,10,8))[0]['category'],'Alimentação')
    def test_unknown(self):self.assertEqual(parse_expense('gastei 10 no cinema',date(2026,10,8))[0]['category'],'Outros')
    def test_installment_sum(self):
        rows=parse_expense('gastei 10 no livro em 3x',date(2026,1,31));self.assertEqual(sum(r['cents'] for r in rows),1000);self.assertEqual(rows[1]['date'],'2026-02-28')
    def test_year_rollover(self):self.assertEqual(parse_expense('gastei 10 no livro em 2x',date(2026,12,31))[1]['date'],'2027-01-31')
    def test_ambiguous_rejected(self):
        for text in ['gastei 10 e 20 no mercado','gastei 10 no dia 12','recebi 20','gastei 1 no livro em 13x']:
            with self.subTest(text=text),self.assertRaises(ValueError):parse_expense(text,date(2026,10,8))
    def test_bounds(self):self.assertEqual(month_bounds('2024-02'),('2024-02-01','2024-02-29'))
    def test_bad_period(self):
        for period in ['2026-13',"2026-10' OR 1=1",None]:
            with self.subTest(period=period),self.assertRaises((ValueError,TypeError)):month_bounds(period)
    def test_idempotence(self):
        ledger=Ledger();rows=parse_expense('gastei 45 no mercado',date(2026,10,8));self.assertTrue(ledger.record(rows,'demo'));self.assertFalse(ledger.record(rows,'demo'));self.assertEqual(ledger.consult('2026-10')['total_cents'],4500)
    def test_period_filter(self):
        ledger=Ledger();ledger.seed();self.assertEqual(ledger.consult('2026-11')['total_cents'],0)
    def test_seed_total(self):
        ledger=Ledger();ledger.seed();self.assertEqual(ledger.consult('2026-10')['total_cents'],5750)
if __name__=='__main__':unittest.main()
