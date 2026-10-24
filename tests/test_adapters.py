import json, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'local'))
from adapters.base import normalize
from adapters.jsonl import JsonLineAdapter
class Adapters(unittest.TestCase):
    def frame(self):return {'schema':'sentinel.sensor.v1','sensor_id':'imu-01','model':'test','metrics':[{'name':'pitch','value':.12,'unit':'rad'}]}
    def test_valid(self):
        s=normalize(self.frame(),10);self.assertEqual(s['received_at'],10);self.assertEqual(s['source'],'external-unverified')
    def test_invalid(self):
        for v in [float('nan'),float('inf'),True,'12']:
            f=self.frame();f['metrics'][0]['value']=v
            with self.assertRaises(ValueError):normalize(f)
    def test_schema_and_duplicate(self):
        f=self.frame();f['schema']='other'
        with self.assertRaises(ValueError):normalize(f)
        f=self.frame();f['metrics']*=2
        with self.assertRaises(ValueError):normalize(f)
    def test_frames(self):
        a=JsonLineAdapter('test');self.assertEqual(a.decode(json.dumps(self.frame()))['sensor_id'],'imu-01')
        for line in ['bad','x'*8193,'[]']:
            with self.assertRaises(ValueError):a.decode(line)
if __name__=='__main__':unittest.main()
