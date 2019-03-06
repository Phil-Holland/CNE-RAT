import sys, time
sys.path.append('..')
from app import celery 

@celery.task(name='intarna')
def intarna(shared_cfg, tool_cfg):
    time.sleep(1)
    return str(shared_cfg)