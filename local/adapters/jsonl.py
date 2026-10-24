import json
from .base import SensorAdapter, normalize
MAX_LINE=8192
class JsonLineAdapter(SensorAdapter):
    def decode(self,line):
        if len(line)>MAX_LINE:raise ValueError('Frame exceeds 8192 bytes')
        try:return normalize(json.loads(line))
        except (json.JSONDecodeError,UnicodeDecodeError) as e:raise ValueError('Invalid JSON frame') from e
    def read(self):return None
