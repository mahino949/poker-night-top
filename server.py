"""Poker Night multiplayer server - standard Python library only."""
import json, os, re, secrets, string, threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'salons.json'
LOCK = threading.RLock()
try:
    rooms = json.loads(DATA.read_text(encoding='utf-8'))
except (FileNotFoundError, ValueError):
    rooms = {}


def save():
    tmp = DATA.with_suffix('.tmp')
    tmp.write_text(json.dumps(rooms, ensure_ascii=False), encoding='utf-8')
    tmp.replace(DATA)


def valid(s):
    if not isinstance(s, dict): return False
    try:
        c = s['count']; f = s['flopCount']; ps = s['players']
        return (type(c) is int and 2 <= c <= 5 and f in (4, 5)
                and isinstance(ps, list) and len(ps) == 5
                and isinstance(s['history'], list) and len(s['history']) <= 3000
                and isinstance(s['finishedRounds'], list) and len(s['finishedRounds']) == 5
                and isinstance(s['flopWinners'], list) and len(s['flopWinners']) == 5
                and isinstance(s['handStartNets'], list) and len(s['handStartNets']) == 5
                and type(s['handNo']) is int and 1 <= s['handNo'] <= 1000000)
    except (KeyError, TypeError): return False


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ('/', '/index.html'):
            b = (ROOT / 'index.html').read_bytes()
            self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
            return
        match = re.fullmatch(r'/api/room/([A-Z2-9]{6})', path)
        if match:
            with LOCK:
                room = rooms.get(match.group(1))
                if room: return self.reply(200, {'revision':room['revision'], 'state':room['state']})
            return self.reply(404, {'error':'Salon introuvable'})
        self.reply(404, {'error':'Page introuvable'})

    def do_POST(self):
        if int(self.headers.get('Content-Length', '0')) > 150000:
            return self.reply(413, {'error':'Données trop volumineuses'})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get('Content-Length', '0'))))
        except (ValueError, TypeError):
            return self.reply(400, {'error':'Requête invalide'})
        path = urlsplit(self.path).path
        if path == '/api/create':
            if not valid(body.get('state')): return self.reply(400, {'error':'État de partie invalide'})
            with LOCK:
                alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
                code = ''.join(secrets.choice(alphabet) for _ in range(6))
                while code in rooms: code = ''.join(secrets.choice(alphabet) for _ in range(6))
                rooms[code] = {'revision':0, 'state':body['state']}
                save()
            return self.reply(201, {'code':code})
        match = re.fullmatch(r'/api/room/([A-Z2-9]{6})', path)
        if not match: return self.reply(404, {'error':'Route introuvable'})
        if not valid(body.get('state')): return self.reply(400, {'error':'État de partie invalide'})
        with LOCK:
            room = rooms.get(match.group(1))
            if not room: return self.reply(404, {'error':'Salon introuvable'})
            if type(body.get('revision')) is not int or body['revision'] != room['revision']:
                return self.reply(409, {'error':'Modification simultanée, synchronisation en cours'})
            room['state'] = body['state']; room['revision'] += 1; save()
            return self.reply(200, {'revision':room['revision']})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    print(f'Poker Night : http://localhost:{port}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', port), Handler).serve_forever()
