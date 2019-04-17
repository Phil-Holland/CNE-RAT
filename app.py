from flask import Flask, render_template, redirect, request, app, abort, json
from redis import Redis
from celery import Celery
from forms import EnsemblForm
import markdown
import uuid
import datetime
import os
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__,
    template_folder='app/templates',
    static_url_path='',
    static_folder='app/static')
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/1'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/1'

celery = Celery(app.name,
    backend=app.config['CELERY_RESULT_BACKEND'],
    broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

from tasks import viennarna, intarna, protein
redis = Redis(host='redis', port=6379)

# load json schemas
schema_cneat = ''
schema_cnefinder = ''
with open("schemas/cneat.json") as f:
    schema_cneat = f.read()

with open("schemas/cnefinder.json") as g:
    schema_cnefinder = g.read()


cnefinder_metadata = dict(
        title='CNEFinder',
        subtitle='Finding Conserved Non-coding Elements in Genomes',
        footer='Built with <a target="_blank" href="http://flask.pocoo.org/">Flask</a>',
)

cneat_metadata = dict(
        title='CNEAT',
        subtitle='The CNE Analysis Tool',
        footer='Built with <a target="_blank" href="http://flask.pocoo.org/">Flask</a>'
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cneat')
def cneat():
    return render_template('cneat.html', schema=schema_cneat, **cneat_metadata)

@app.route('/cnefinder')
def cnefinder():
    return render_template('cnefinder.html', schema=schema_cnefinder, **cnefinder_metadata)

@app.route('/check_url', methods=['POST'])
def check_url():
    data = request.get_json(force=True) #json.loads(request.data)
    path = "/biomart/martservice"
    payload = {'type': 'registry', 'requestid': 'biomaRt'}

    flag = True
    content = {}
    urlstring = data.get('url')

    if urlstring:
        if urlstring[-1] == '/': # trim trailing forward slash if necessary
            urlstring = urlstring[:-1]

        r = requests.post(urlstring + path, data=payload)

        # if no valid marts, likely to return 404
        if r.status_code != 200:
            flag = False
        else:
            tree = ET.ElementTree(ET.fromstring(r.text))
            root = tree.getroot()

            # parse xml reponse as tree looking for `visible` biomarts
            for child in root:
                attributes = child.attrib
                if attributes.get('visible', "0") == "1":

                    content[attributes.get('name')] = {
                        'displayName': attributes.get('displayName'),
                        'database': attributes.get('database') }
    return json.dumps({'success': flag, 'content': content}), 200, {'ContentType':'application/json'}

@app.route('/find_datasets', methods=['POST'])
def find_datasets():
    data = request.get_json(force=True) #json.loads(request.data)
    path = "/biomart/martservice"

    mart = data.get('mart')
    payload = {'type': 'datasets', 'requestid': 'biomaRt', 'mart' : mart}

    flag = True
    content = {}
    urlstring = data.get('url')

    if urlstring:
        if urlstring[-1] == '/': # trim trailing forward slash if necessary
            urlstring = urlstring[:-1]

        r = requests.post(urlstring + path, data=payload)

        # if no valid marts, likely to return 404
        if r.status_code != 200:
            flag = False
        else:
            # request returns a tab and newline deliminated raw string for some reason
            dataset_lines = r.text.split('\n')
            datasets = [row.split('\t') for row in dataset_lines if row and not row.isspace()]

            for d in datasets:
                if d[3] == 1 or d[3] == '1': # check for `visibility` of dataset on site

                    # https://rdrr.io/github/grimbough/biomaRt/src/R/biomaRt.R#sym-listDatasets
                    # key names taken from this link (the biomaRt source)
                    content[d[1]] = {'description' : d[2], 'version' : d[4]}
    return json.dumps({'success': flag, 'content': content}), 200, {'ContentType':'application/json'}


@app.route('/analysis/<uid>')
def analysis(uid):
    # make sure the analysis exists
    if not redis.exists('analyses:' + uid):
        return abort(404)

    started = redis.get('analyses:' + uid + ':started').decode("utf-8")
    config = redis.get('analyses:' + uid + ':config').decode("utf-8")

    return render_template('analysis.html', uid=uid, config=config, started=started)

@app.route('/get_analysis_status/<uid>', methods=['POST'])
def get_analysis_status(uid):
    # make sure the analysis exists
    if not redis.exists('analyses:' + uid):
        return abort(404)

    tasks = redis.lrange('analyses:' + uid + ':tasks', 0, -1)

    statuses = []
    for t in tasks:
        t = json.loads(t.decode('UTF-8'))
        # get celery task status
        res = celery.AsyncResult(t['task_id'])
        status = res.state
        statuses.append({'name': t['task_name'], 'id': t['task_id'], 'status': status})
    return json.dumps({'success': True, 'statuses': statuses}), 200, {'ContentType':'application/json'}

@app.route('/get_task_data/<tid>', methods=['POST'])
def get_task_data(tid):
    res = celery.AsyncResult(tid)
    if res.state == 'SUCCESS':
        # render markdown
        content = markdown.markdown(res.result)
        return json.dumps({'success': True, 'result': content}), 200, {'ContentType':'application/json'}
    else:
        return abort(404)

@app.route('/new_analysis', methods=['POST'])
def new_analysis():
    # get analysis start time
    started = datetime.datetime.utcnow().strftime("%H:%M:%S %Y-%m-%d")

    config = request.get_json(force=True)

    if config is None:
        return json.dumps({'success': False}), 400, {'ContentType':'application/json'}

    # generate a unique ID (chance of collision is basically impossible)
    uid = ''
    while(True):
        uid = str(uuid.uuid4())[:8]
        if not redis.exists('analyses:' + uid):
            redis.set('analyses:' + uid, uid)
            redis.set('analyses:' + uid + ':started', started)
            redis.set('analyses:' + uid + ':config', json.dumps(config))
            break

    if config['rna_protein'] == True:
        t0 = protein.protein.delay(config, uid)
        redis.lpush('analyses:' + uid + ':tasks',
            json.dumps({
                'task_name': 'protein',
                'task_id': t0.task_id
            })
        )

    if config['rna_rna'] == True:
        if config['rna_rna_config']['vienna']:
            t1 = viennarna.viennarna.delay(config, uid)
            redis.lpush('analyses:' + uid + ':tasks',
                json.dumps({
                    'task_name': 'viennarna',
                    'task_id': t1.task_id
                })
            )

        if config['rna_rna_config']['inta']:
            t2 = intarna.intarna.delay(config, uid)
            redis.lpush('analyses:' + uid + ':tasks',
                json.dumps({
                    'task_name': 'intarna',
                    'task_id': t2.task_id
                })
            )

    return json.dumps({'success': True, 'uid': uid}), 200, {'ContentType':'application/json'}

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
