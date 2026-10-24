"""Best-effort, read-only IOHID temperature sampling. No root, no SMC writes.
Undocumented Apple interfaces may change; unavailable is a valid result.
"""
import ctypes as C
import math
import sys

def read_temperatures():
    if sys.platform != 'darwin':
        return []
    cf=C.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
    io=C.CDLL('/System/Library/Frameworks/IOKit.framework/IOKit')
    def bind(lib,name,result,args):
        f=getattr(lib,name);f.restype=result;f.argtypes=args;return f
    ptr=C.c_void_p
    create=bind(io,'IOHIDEventSystemClientCreate',ptr,[ptr])
    services=bind(io,'IOHIDEventSystemClientCopyServices',ptr,[ptr])
    prop=bind(io,'IOHIDServiceClientCopyProperty',ptr,[ptr,ptr])
    event=bind(io,'IOHIDServiceClientCopyEvent',ptr,[ptr,C.c_int,ptr,C.c_int])
    number=bind(io,'IOHIDEventGetFloatValue',C.c_double,[ptr,C.c_int])
    count=bind(cf,'CFArrayGetCount',C.c_long,[ptr])
    at=bind(cf,'CFArrayGetValueAtIndex',ptr,[ptr,C.c_long])
    string=bind(cf,'CFStringCreateWithCString',ptr,[ptr,C.c_char_p,C.c_uint32])
    text=bind(cf,'CFStringGetCString',C.c_bool,[ptr,C.c_char_p,C.c_long,C.c_uint32])
    release=bind(cf,'CFRelease',None,[ptr])
    client=create(None)
    if not client:return []
    array=services(client);key=string(None,b'Product',0x08000100);out=[]
    try:
        if not array:return []
        for i in range(count(array)):
            service=at(array,i);label=prop(service,key)
            if not label:continue
            buf=C.create_string_buffer(256)
            ok=text(label,buf,256,0x08000100);release(label)
            if not ok:continue
            name=buf.value.decode('utf-8','replace')
            ev=event(service,15,None,0)
            if not ev:continue
            try:
                value=number(ev,15<<16)
                if math.isfinite(value) and -20<value<150 and value!=0:
                    out.append({'name':name,'celsius':round(value,2),'source':'IOHID temperature event'})
            finally:release(ev)
    finally:
        if array:release(array)
        release(key);release(client)
    return out

if __name__=='__main__':
    import json
    try:print(json.dumps({'readings':read_temperatures(),'experimental':True}))
    except (OSError,AttributeError) as e:print(json.dumps({'readings':[],'error':type(e).__name__}))
