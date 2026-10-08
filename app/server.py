"""Loopback-only synthetic demo. No credentials, external services or pickle."""
import json
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from .expenses import Ledger, parse_expense

ROOT=Path(__file__).parent
ledger=Ledger();ledger.seed()
class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass # Do not log expense bodies or query strings.
    def respond(self,status,data):
        body=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("X-Content-Type-Options","nosniff");self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if self.path!="/":return self.respond(404,{"error":"Não encontrado"})
        body=(ROOT/'index.html').read_bytes();self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8");self.send_header("X-Content-Type-Options","nosniff");self.end_headers();self.wfile.write(body)
    def do_POST(self):
        # Browser controls plus loopback reduce demo exposure; they are not auth.
        if self.headers.get('Origin') not in (None,'http://127.0.0.1:8001'):return self.respond(403,{"error":"Origem não permitida"})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=4096:raise ValueError("Corpo inválido ou grande demais.")
            data=json.loads(self.rfile.read(size))
            if not isinstance(data,dict):raise ValueError("Esperado objeto JSON.")
            if self.path=='/preview':result={"rows":parse_expense(data.get('text'),date(2026,10,8))}
            elif self.path=='/record':
                rows=parse_expense(data.get('text'),date(2026,10,8))
                result={"recorded":ledger.record(rows,data.get('request_id')),"rows":rows}
            elif self.path=='/consult':result=ledger.consult(data.get('period'))
            else:return self.respond(404,{"error":"Não encontrado"})
            self.respond(200,result)
        except (ValueError,TypeError,KeyError):self.respond(400,{"error":"Entrada inválida. Use o formato demonstrativo indicado."})

if __name__=='__main__':
    print('Synthetic expense demo at http://127.0.0.1:8001. In-memory data resets on restart.')
    HTTPServer(('127.0.0.1',8001),Handler).serve_forever()
