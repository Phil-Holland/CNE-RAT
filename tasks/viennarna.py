import sys, time
sys.path.append('..')
from app import celery 

@celery.task(name='viennarna')
def viennarna(shared_cfg, tool_cfg):
    time.sleep(1)
    return '## viennarna - results!\nThis is markdown'