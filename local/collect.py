"""Opt-in JSONL sensor collector. Usage: python3 local/collect.py --stdin
or --port /dev/cu.usbmodem... --baud 115200. Does not send serial commands.
Opening a serial device may reset attached MCU boards.
"""
import argparse, json, os, select, sys, time
from pathlib import Path
from adapters.jsonl import JsonLineAdapter, MAX_LINE
ROOT=Path(__file__).resolve().parent.parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--stdin',action='store_true');group.add_argument('--port')
    p.add_argument('--baud',type=int,choices=[9600,19200,38400,57600,115200,230400],default=115200)
    args=p.parse_args();fd=None;old=None;stream=None
    if args.port:
        import termios, tty
        port=Path(args.port)
        if not str(port).startswith('/dev/cu.') or not port.exists():p.error('Expected an existing /dev/cu.* device')
        fd=os.open(str(port),os.O_RDONLY|os.O_NOCTTY|os.O_NONBLOCK)
        old=termios.tcgetattr(fd);tty.setraw(fd);config=termios.tcgetattr(fd);config[4]=config[5]=getattr(termios,'B'+str(args.baud));termios.tcsetattr(fd,termios.TCSANOW,config)
    else:fd=sys.stdin.fileno()
    adapter=JsonLineAdapter('serial-jsonl' if args.port else 'stdin-jsonl');samples={};buffer=b'';discard=False
    runtime=ROOT/'local/runtime';runtime.mkdir(mode=0o700,exist_ok=True)
    try:
        while True:
            ready,_,_=select.select([fd],[],[],1)
            if not ready:continue
            chunk=os.read(fd,4096)
            if not chunk:
                if args.port:time.sleep(.1);continue
                break
            for byte in chunk:
                if byte==10:
                    if buffer and not discard:
                        try:
                            sample=adapter.decode(buffer);sample['transport']='serial-jsonl' if args.port else 'stdin-jsonl';samples[sample['sensor_id']]=sample
                            if len(samples)>64:samples.pop(next(iter(samples)))
                            target=runtime/'sensors.json';tmp=runtime/'sensors.tmp';tmp.write_text(json.dumps(list(samples.values())));tmp.chmod(0o600);tmp.replace(target)
                            print('Sample accepted: '+sample['sensor_id'],flush=True)
                        except ValueError as e:print('Frame rejected: '+str(e),file=sys.stderr)
                    buffer=b'';discard=False
                elif not discard:
                    buffer+=bytes([byte])
                    if len(buffer)>MAX_LINE:buffer=b'';discard=True;print('Oversized frame dropped',file=sys.stderr)
    finally:
        if args.port:
            termios.tcsetattr(fd,termios.TCSANOW,old);os.close(fd)
if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:pass
