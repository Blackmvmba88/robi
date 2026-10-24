"""Loopback-only static app and read-only Mac sensor bridge. No uploads or writes."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import glob, json, subprocess, sys, time, threading
ROOT=Path(__file__).resolve().parent.parent
CACHE={}
LOCK=threading.Lock()

def run(args):
    try:
        r=subprocess.run(args,capture_output=True,text=True,timeout=8)
        return r.stdout if r.returncode==0 else ''
    except (OSError,subprocess.TimeoutExpired):return ''

def inventory():
    if sys.platform!='darwin':return {'available':False,'reason':'El puente requiere macOS'}
    with LOCK:
        if time.monotonic()-CACHE.get('at',-100)>30:
            try:raw=json.loads(run(['system_profiler','SPCameraDataType','SPAudioDataType','SPUSBDataType','-json']) or '{}')
            except ValueError:raw={}
            def flatten(items):
                out=[]
                for item in items:
                    if '_name' in item:out.append({'name':item['_name'],'input':item.get('coreaudio_device_input',0),'transport':item.get('coreaudio_device_transport','')})
                    out.extend(flatten(item.get('_items',[])))
                return out
            CACHE.update(at=time.monotonic(),data={'cameras':flatten(raw.get('SPCameraDataType',[])),'audio':flatten(raw.get('SPAudioDataType',[])),'usb':flatten(raw.get('SPUSBDataType',[])),'serial':glob.glob('/dev/cu.*')})
        data=dict(CACHE['data'])
    try:thermal=json.loads(run([sys.executable,str(ROOT/'local/thermal.py')]) or '{}')
    except ValueError:thermal={}
    data.update(available=True,timestamp=time.time(),thermal=thermal.get('readings',[]),thermalExperimental=True,power=run(['pmset','-g','batt']).strip(),thermalStatus=run(['pmset','-g','therm']).strip())
    return data

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'dist'),**kwargs)
    def end_headers(self):
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        super().end_headers()
    def do_GET(self):
        host=self.headers.get('Host','')
        if host not in {'localhost:8080','127.0.0.1:8080'}:
            self.send_error(403);return
        origin=self.headers.get('Origin')
        if origin and origin not in {'http://localhost:8080','http://127.0.0.1:8080'}:
            self.send_error(403);return
        if self.headers.get('Sec-Fetch-Site')=='cross-site':
            self.send_error(403);return
        if urlsplit(self.path).path=='/api/external-sensors':
            try:
                target=ROOT/'local/runtime/sensors.json'
                samples=json.loads(target.read_text()) if target.exists() and target.stat().st_size<1000000 else []
                payload=json.dumps({'samples':samples,'timestamp':time.time()}).encode()
            except (OSError,ValueError):payload=b'{"samples":[],"error":"Invalid local adapter cache"}'
            self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload);return
        if urlsplit(self.path).path=='/api/mac-sensors':
            payload=json.dumps(inventory()).encode();self.send_response(200)
            self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload);return
        super().do_GET()

if __name__=='__main__':
    print('SENTINEL local: http://localhost:8080',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8080),Handler).serve_forever()
