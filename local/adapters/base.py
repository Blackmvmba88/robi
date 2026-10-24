from abc import ABC, abstractmethod
from dataclasses import dataclass
import math, re, time

@dataclass
class SensorAdapter(ABC):
    """Adapters emit normalized samples; hardware I/O belongs in implementations."""
    adapter_id: str
    @abstractmethod
    def read(self):
        """Return a validated sensor sample or None. Never synthesize real data."""
        raise NotImplementedError

def normalize(payload, received_at=None):
    if not isinstance(payload,dict) or payload.get('schema')!='sentinel.sensor.v1':
        raise ValueError('Expected sentinel.sensor.v1 object')
    sensor_id=payload.get('sensor_id')
    if not isinstance(sensor_id,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,64}',sensor_id):
        raise ValueError('Invalid sensor_id')
    metrics=payload.get('metrics')
    if not isinstance(metrics,list) or not 1<=len(metrics)<=32:raise ValueError('Expected 1–32 metrics')
    out=[];names=set()
    for metric in metrics:
        if not isinstance(metric,dict):raise ValueError('Invalid metric')
        name,value,unit=metric.get('name'),metric.get('value'),metric.get('unit')
        if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9_.-]{1,64}',name) or name in names:raise ValueError('Invalid or duplicate metric name')
        if type(value) not in (int,float) or not math.isfinite(value) or abs(value)>1e15:raise ValueError('Finite numeric metric required')
        if not isinstance(unit,str) or not 1<=len(unit)<=24:raise ValueError('Unit required')
        names.add(name);out.append({'name':name,'value':value,'unit':unit})
    model=payload.get('model','unknown')
    if not isinstance(model,str) or len(model)>120:raise ValueError('Invalid model')
    return {'schema':'sentinel.sensor.v1','sensor_id':sensor_id,'model':model,'source':'external-unverified','received_at':time.time() if received_at is None else received_at,'metrics':out}
