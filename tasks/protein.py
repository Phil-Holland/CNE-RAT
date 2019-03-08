import sys, time
sys.path.append('..')
from app import celery 

@celery.task(name='protein')
def protein(shared_cfg, tool_cfg):
    time.sleep(5)
    return '# RNA-Protein Interactions'