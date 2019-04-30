import markdown
import uuid
import datetime
import os
import sys
import requests
from flask import Flask, render_template, redirect, request, app, abort, json
from redis import Redis
from celery import Celery
from jsonschema import validate, ValidationError
import xml.etree.ElementTree as ET

# get the redis password, which is set as a system environment variable through docker
redis_password = os.environ['REDIS_PASSWORD']

# instantiate the flask app object
app = Flask(__name__, 
    template_folder='app/templates',
    static_url_path='',
    static_folder='app/static')

# to fully integrate flask and celery, set celery's broker and result store information
# within the flask app config
app.config['CELERY_BROKER_URL'] = 'redis://:{}@redis:6379/1'.format(redis_password)
app.config['CELERY_RESULT_BACKEND'] = 'redis://:{}@redis:6379/1'.format(redis_password)

# instantiate the celery task queue instance - use the above broker/result store information
# also make sure task result data does not expire
sys.path.append('tasks')
celery = Celery(app.name, 
    backend=app.config['CELERY_RESULT_BACKEND'],
    broker=app.config['CELERY_BROKER_URL'],
    include=['protein', 'viennarna', 'intarna', 'cnefinder', 'shared'],
    result_expires=None)
celery.conf.update(app.config)

# connect to the redis instance
redis = Redis(host='redis', port=6379, password=redis_password)

# load json schemas (from external json file)
schema_cneat = ''
schema_cneat_json = None
schema_cnefinder = ''
schema_cnefinder_json = None

with open("schemas/cneat.schema.json") as f:
    schema_cneat = f.read()
    schema_cneat_json = json.loads(schema_cneat)

with open("schemas/cnefinder.schema.json") as g:
    schema_cnefinder = g.read()
    schema_cnefinder_json = json.loads(schema_cnefinder)

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
    """route for the site's homepage - render the simple index template"""
    return render_template('index.html')

@app.route('/cneat')
def cneat():
    """route for the CNEAT analysis configuration interface"""
    return render_template('cneat.html', schema=schema_cneat, **cneat_metadata)

@app.route('/cnefinder')
def cnefinder():
    """route for the CNEFinder job configuration interface"""
    return render_template('cnefinder.html', schema=schema_cnefinder, **cnefinder_metadata)

@app.route('/check_url', methods=['POST'])
def check_url():
    """simple POST request endpoint to check a CNEFinder biomart URL"""

    data = request.get_json(force=True)
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
    """POST request endpoint to find available datasets at a given biomart URL"""

    data = request.get_json(force=True)
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

@app.route('/output/<uid>')
def output(uid):
    """route for the CNEFinder results interface"""

    # make sure the cnefinder exists
    if not redis.exists('cnefinder:' + uid):
        return abort(404)

    started = redis.get('cnefinder:' + uid + ':started').decode("utf-8")
    config = redis.get('cnefinder:' + uid + ':config').decode("utf-8")

    return render_template('output.html', uid=uid, config=config, started=started, **cnefinder_metadata)

@app.route('/get_cnefinder_status/<uid>', methods=['POST'])
def get_cnefinder_status(uid):
    """simple POST request to check the status of an active/failed/finished CNEFinder job"""

    # make sure the analysis exists
    if not redis.exists('cnefinder:' + uid):
        return abort(404)

    tasks = redis.lrange('cnefinder:' + uid + ':tasks', 0, -1)

    statuses = []
    for t in tasks:
        t = json.loads(t.decode('UTF-8'))
        # get celery task status
        res = celery.AsyncResult(t['task_id'])
        status = res.state
        statuses.append({'name': t['task_name'], 'id': t['task_id'], 'status': status})
    return json.dumps({'success': True, 'statuses': statuses}), 200, {'ContentType':'application/json'}

@app.route('/new_cnefinder', methods=['POST'])
def new_cnefinder():
    """POST request endpoint to create a new CNEFinder job"""

    # get cnefinder run start time
    started = datetime.datetime.utcnow().strftime("%H:%M:%S %Y-%m-%d")
    config = request.get_json(force=True)

    if config is None:
        return json.dumps({'success': False}), 400, {'ContentType':'application/json'}

    # generate a unique ID (chance of collision is basically impossible)
    uid = ''
    while(True):
        uid = str(uuid.uuid4())[:8]
        if not redis.exists('cnefinder:' + uid):
            redis.set('cnefinder:' + uid, uid)
            redis.set('cnefinder:' + uid + ':started', started)
            redis.set('cnefinder:' + uid + ':config', json.dumps(config))
            break

        # no if-blocks needed for task type gene-name or index-position, as they
        # are handled by the same python task script.

    return json.dumps({'success': True, 'uid': uid}), 200, {'ContentType':'application/json'}


@app.route('/analysis/<uid>')
def analysis(uid):
    """returns the analysis page for the analysis specified by its unique identifier
    passes through the stored start time and full initial json config"""

    # make sure the analysis exists
    if not redis.exists('analyses:' + uid):
        return abort(404)

    # get required vars from the redis database
    started = redis.get('analyses:' + uid + ':started').decode("utf-8")
    config = redis.get('analyses:' + uid + ':config').decode("utf-8")

    return render_template('analysis.html', uid=uid, config=config, started=started, **cneat_metadata)

@app.route('/get_analysis_status/<uid>', methods=['POST'])
def get_analysis_status(uid):
    """POST request endpoint to poll for analysis status - returns the status of each
    component task involved in the analysis"""

    # make sure the analysis exists
    if not redis.exists('analyses:' + uid):
        return abort(404)

    tasks = redis.lrange('analyses:' + uid + ':tasks', 0, -1)

    # make sure the analysis' tasks exist
    if not redis.exists('analyses:' + uid + ':tasks'):
        return abort(404)

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
    """POST request endpoint to return the output data from a specific task, 
    identified by it's unique id"""

    res = celery.AsyncResult(tid)
    if res.state == 'SUCCESS':
        # convert the markdown from the task's output to HTML, and return it
        content = markdown.markdown(res.result, extensions=['tables'])
        return json.dumps({'success': True, 'result': content}), 200, {'ContentType':'application/json'} 
    else:
        # task has not yet completed
        return abort(404)

@app.route('/new_analysis', methods=['POST'])
def new_analysis():
    """POST request endpoint to create and start a new analysis"""

    # get analysis start time
    started = datetime.datetime.utcnow().strftime("%H:%M:%S %Y-%m-%d")

    # get the JSON configuration object from the request's content
    config = request.get_json(force=True, silent=True)

    # make sure the config exists after parsing (will be None otherwise)
    if config is None:
        return json.dumps({
            'success': False,
            'error': 'Config was not parsed successfully'
        }), 400, {'ContentType':'application/json'}

    # make sure config is valid (using schemas/cneat.json)
    try:
        validate(instance=config, schema=schema_cneat_json)
    except ValidationError as e:
        return json.dumps({
            'success': False,
            'error': str(e) 
        }), 400, {'ContentType':'application/json'}

    # generate a unique ID (chance of collision is basically impossible, but handled)
    uid = ''
    while(True):
        uid = str(uuid.uuid4())[:8]
        if not redis.exists('analyses:' + uid):
            redis.set('analyses:' + uid, uid)
            redis.set('analyses:' + uid + ':started', started)
            redis.set('analyses:' + uid + ':config', json.dumps(config))
            break

    # create and queue each desired task, and store tracking information in redis

    if config['rna_protein'] == True:
        t0 = celery.send_task('protein', (config, uid))
        redis.lpush('analyses:' + uid + ':tasks',
            json.dumps({
                'task_name': 'protein',
                'task_id': t0.task_id
            })
        )

    if config['rna_rna'] == True:
        if config['rna_rna_config']['vienna'] == True:
            t1 = celery.send_task('viennarna', (config, uid))
            redis.lpush('analyses:' + uid + ':tasks',
                json.dumps({
                    'task_name': 'viennarna',
                    'task_id': t1.task_id
                })
            )

        if config['rna_rna_config']['inta'] == True:
            t2 = celery.send_task('intarna', (config, uid))
            redis.lpush('analyses:' + uid + ':tasks',
                json.dumps({
                    'task_name': 'intarna',
                    'task_id': t2.task_id
                })
            )
    
    return json.dumps({
        'success': True,
        'uid': uid
    }), 200, {'ContentType':'application/json'} 

    return json.dumps({'success': True, 'uid': uid}), 200, {'ContentType':'application/json'}

if __name__ == "__main__":
    # script entry point - runs the debugger if the script is executed with python 
    # from the command line
    app.run(host="0.0.0.0", debug=True)
