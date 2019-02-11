import sys, time
sys.path.append('..')
from app import celery 

@celery.task(name='intarna')
def intarna(shared_cfg, tool_cfg):
    time.sleep(10)
    return '# this is some test content\n[Google](http://google.com)'