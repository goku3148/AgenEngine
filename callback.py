import time
from typing import List, Dict

class CallbackHandler:
    anchore = time.time()
    def __init__(self,frame,event_t):
        self.frame = frame
        self.et = event_t
        self._pass = True 

    def timestamp(self,anchore=None):
        if anchore is None:
            anchore = self.anchore
        return int((time.time() - anchore)*10)/10

    def tool_response(self,tool,inputs,error) -> Dict:
        pas

    def package_response(self,tool,inputs,error) -> Dict:
        pass

    def time_anchore(self,):
        self.anchore = time.time()

    

