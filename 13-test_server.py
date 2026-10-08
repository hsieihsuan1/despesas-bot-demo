import json
import threading
import unittest
from http.server import HTTPServer
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from app.server import Handler
class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=HTTPServer(('127.0.0.1',0),Handler);cls.url=f'http://127.0.0.1:{cls.server.server_port}';cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def call(self,path,data,origin=None):
        headers={'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        req=Request(self.url+path,data=json.dumps(data).encode(),headers=headers)
        try:
            with urlopen(req) as r:return r.status,json.load(r)
        except HTTPError as r:return r.code,json.load(r)
    def test_preview_no_write(self):
        before=self.call('/consult',{'period':'2026-10'})[1]['total_cents'];status,data=self.call('/preview',{'text':'gastei 30 no café'});self.assertEqual(status,200);self.assertEqual(data['rows'][0]['cents'],3000);self.assertEqual(self.call('/consult',{'period':'2026-10'})[1]['total_cents'],before)
    def test_confirm_idempotent(self):
        data={'text':'gastei 5 no livro','request_id':'api-test'};self.assertTrue(self.call('/record',data)[1]['recorded']);self.assertFalse(self.call('/record',data)[1]['recorded'])
    def test_bad_origin(self):self.assertEqual(self.call('/record',{},'https://example.invalid')[0],403)
    def test_nonobject(self):self.assertEqual(self.call('/preview',[])[0],400)
    def test_invalid_input(self):self.assertEqual(self.call('/preview',{'text':'gastei 10 e 20'})[0],400)
    def test_invalid_month(self):self.assertEqual(self.call('/consult',{'period':'2026-13'})[0],400)
