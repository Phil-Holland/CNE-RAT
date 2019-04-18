import pytest, requests, json, time

# this file contains a selection of pytest tests for the web tool

@pytest.mark.describe('Page/Request Codes')
class TestPageCodes():

    @pytest.mark.it('Returns HTTP code 200 when requesting the CNEAT configuration page')
    def test_cneat(self):
        assert requests.get('http://web:5000/cneat').status_code == 200

    @pytest.mark.it('Returns HTTP code 404 when requesting the analysis page with no analysis code')
    def test_analysis_blank(self):
        assert requests.get('http://web:5000/analysis/').status_code == 404

    @pytest.mark.it('Returns HTTP code 404 when requesting the analysis page with an invalid code')
    def test_analysis_invalid(self):
        assert requests.get('http://web:5000/analysis/test').status_code == 404

    @pytest.mark.it('Returns HTTP code 405 when requesting the status of an analysis without providing its id')
    def test_analysis_status_blank(self):
        assert requests.post('http://web:5000/get_analysis_status/').status_code == 405

    @pytest.mark.it('Returns HTTP code 404 when requesting the status of an invalid analysis')
    def test_analysis_status_invalid(self):
        assert requests.post('http://web:5000/get_analysis_status/test').status_code == 404

    @pytest.mark.it('Returns HTTP code 405 when requesting the data of a task without providing its id')
    def test_task_data_blank(self):
        assert requests.post('http://web:5000/get_task_data/').status_code == 405

    @pytest.mark.it('Returns HTTP code 404 when requesting the data of an invalid task')
    def test_task_data_invalid(self):
        assert requests.post('http://web:5000/get_task_data/test').status_code == 404

@pytest.mark.describe('CNEAT: Invalid Analysis Requests')
class TestCneatInvalidAnalysis():

    @pytest.mark.it('Returns a HTTP code 400 when requesting a new analysis with no configuration')
    def test_none(self):
        request = requests.post('http://web:5000/new_analysis')

        assert request.status_code == 400

    @pytest.mark.it('Returns a HTTP code 400 when requesting a new analysis with an empty configuration')
    def test_blank(self):
        config = {}
        request = requests.post('http://web:5000/new_analysis', json=config)

        assert request.status_code == 400

    @pytest.mark.it('Returns a HTTP code 400 when requesting a new analysis without one of the RNA-RNA or RNA-protein tasks')
    def test_no_tasks(self):
        config = {
            'cne': '>test\nACGT',
            'rna_protein': False,
            'rna_rna': False
        }
        request = requests.post('http://web:5000/new_analysis', json=config)

        assert request.status_code == 400

    @pytest.mark.it('Returns a HTTP code 400 when requesting a new analysis without a corresponding task config')
    def test_no_task_config(self):
        config = {
            'cne': '>test\nACGT',
            'rna_protein': True,
            'rna_rna': False
        }
        request = requests.post('http://web:5000/new_analysis', json=config)
        code1 = request.status_code

        config = {
            'cne': '>test\nACGT',
            'rna_protein': False,
            'rna_rna': True
        }
        request = requests.post('http://web:5000/new_analysis', json=config)
        code2 = request.status_code

        assert (code1 == 400 and code2 == 400)

    @pytest.mark.it('Returns a HTTP code 400 when requesting a new analysis with an empty task config')
    def test_empty_task_config(self):
        config = {
            'cne': '>test\nACGT',
            'rna_protein': True,
            'rna_rna': False,
            'rna_protein_config': {}
        }
        request = requests.post('http://web:5000/new_analysis', json=config)
        code1 = request.status_code

        config = {
            'cne': '>test\nACGT',
            'rna_protein': False,
            'rna_rna': True,
            'rna_rna_config': {}
        }
        request = requests.post('http://web:5000/new_analysis', json=config)
        code2 = request.status_code

        assert (code1 == 400 and code2 == 400)

@pytest.mark.describe('CNEAT: Analysis Output')
class TestCneatAnalysis():

    def create_config(self, cne='ACGT', protein=True, rnarna=True, dros=True, homo=True, 
        mus=True, qseq='ACGT', inta=True, minpu=0.5, mode='H', vienna=True, rnacofold=True, 
        rnaduplex=True, deltaenergy=5):
        '''Helper function to create a CNEAT config object'''

        config = {}
        config['cne'] = '>cne\n' + cne
        config['rna_protein'] = protein
        config['rna_rna'] = rnarna
        
        if protein:
            config['rna_protein_config'] = {
                'drosophila_melanogaster': dros,
                'homo_sapiens': homo,
                'mus_musculus': mus
            }
        
        if rnarna:
            config['rna_rna_config'] = {
                'query_sequences': '>query\n' + qseq,
                'inta': inta,
                'vienna': vienna
            }

            if inta:
                config['rna_rna_config']['inta_config'] = {
                    'minpu': minpu,
                    'prediction_mode': mode
                }

            if vienna:
                config['rna_rna_config']['vienna_config'] = {
                    'rnacofold': rnacofold,
                    'rnaduplex': rnaduplex
                }

                if rnacofold:
                    config['rna_rna_config']['vienna_config']['rnacofold_config'] = {}

                if rnaduplex:
                    config['rna_rna_config']['vienna_config']['rnaduplex_config'] = {
                        'deltaenergy': deltaenergy
                    }

        return config

    @pytest.mark.it('Successfully creates an analysis')
    def test_analysis(self):
        config1 = self.create_config(rnarna=False)
        request = requests.post('http://web:5000/new_analysis', json=config1)
        code1 = request.status_code

        config2 = self.create_config(protein=False)
        request = requests.post('http://web:5000/new_analysis', json=config2)
        code2 = request.status_code

        config3 = self.create_config()
        request = requests.post('http://web:5000/new_analysis', json=config3)
        code3 = request.status_code

        assert (code1 == 200 and code2 == 200 and code3 == 200)

    @pytest.mark.it('Successfully reports the status of a newly created analysis')
    def test_analysis_status(self):
        # create analysis
        config = self.create_config(rnarna=False)
        request = requests.post('http://web:5000/new_analysis', json=config)
        content = json.loads(request.content.decode("utf-8"))

        # request analysis status
        request = requests.post('http://web:5000/get_analysis_status/%s' % content['uid'])
        assert request.status_code == 200

        content = json.loads(request.content.decode("utf-8"))
        assert content['success'] == True

    @pytest.mark.it('Successfully creates a protein report')
    def test_analysis_protein(self):
        # create analysis
        config = self.create_config(rnarna=False)
        request = requests.post('http://web:5000/new_analysis', json=config)
        content = json.loads(request.content.decode("utf-8"))
        uid = content['uid']

        # poll analysis status - do this 30 times (i.e. wait 60s)
        i = 0
        while True:
            request = requests.post('http://web:5000/get_analysis_status/%s' % uid)
            assert request.status_code == 200

            content = json.loads(request.content.decode("utf-8"))

            # make sure all of the required fields are present
            assert 'statuses' in content
            assert isinstance(content['statuses'], list)
            assert len(content['statuses']) > 0
            assert 'status' in content['statuses'][0]

            # keep polling until the task is complete
            if content['statuses'][0]['status'] == 'SUCCESS':
                break

            i += 1
            if i >= 30:
                pytest.fail('Task did not complete quickly enough (waited 60s)')

            time.sleep(2)

        # get contents of protein task
        tid = content['statuses'][0]['id']
        request = requests.post('http://web:5000/get_task_data/%s' % tid)
        content = json.loads(request.content.decode("utf-8"))

        assert content['success'] == True
        assert 'result' in content

        # check that the output is present
        assert '<h1>RNA-Protein Toolchain Output</h1>' in content['result']

    @pytest.mark.it('Successfully creates an IntaRNA report')
    def test_analysis_inta(self):
        # create analysis
        config = self.create_config(protein=False, vienna=False)
        request = requests.post('http://web:5000/new_analysis', json=config)
        content = json.loads(request.content.decode("utf-8"))
        uid = content['uid']

        # poll analysis status - do this 30 times (i.e. wait 60s)
        i = 0
        while True:
            request = requests.post('http://web:5000/get_analysis_status/%s' % uid)
            assert request.status_code == 200

            content = json.loads(request.content.decode("utf-8"))

            # make sure all of the required fields are present
            assert 'statuses' in content
            assert isinstance(content['statuses'], list)
            assert len(content['statuses']) > 0
            assert 'status' in content['statuses'][0]

            # keep polling until the task is complete
            if content['statuses'][0]['status'] == 'SUCCESS':
                break

            i += 1
            if i >= 30:
                pytest.fail('Task did not complete quickly enough (waited 60s)')

            time.sleep(2)

        # get contents of protein task
        tid = content['statuses'][0]['id']
        request = requests.post('http://web:5000/get_task_data/%s' % tid)
        content = json.loads(request.content.decode("utf-8"))

        assert content['success'] == True
        assert 'result' in content

        # check that the output is present
        assert '<h1>IntaRNA Toolchain Output</h1>' in content['result']

    @pytest.mark.it('Successfully creates a ViennaRNA report')
    def test_analysis_vienna(self):
        # create analysis
        config = self.create_config(protein=False, inta=False, rnacofold=False)
        request = requests.post('http://web:5000/new_analysis', json=config)
        content = json.loads(request.content.decode("utf-8"))
        uid = content['uid']

        # poll analysis status - do this 30 times (i.e. wait 60s)
        i = 0
        while True:
            request = requests.post('http://web:5000/get_analysis_status/%s' % uid)
            assert request.status_code == 200

            content = json.loads(request.content.decode("utf-8"))

            # make sure all of the required fields are present
            assert 'statuses' in content
            assert isinstance(content['statuses'], list)
            assert len(content['statuses']) > 0
            assert 'status' in content['statuses'][0]

            # keep polling until the task is complete
            if content['statuses'][0]['status'] == 'SUCCESS':
                break

            i += 1
            if i >= 30:
                pytest.fail('Task did not complete quickly enough (waited 60s)')

            time.sleep(2)

        # get contents of protein task
        tid = content['statuses'][0]['id']
        request = requests.post('http://web:5000/get_task_data/%s' % tid)
        content = json.loads(request.content.decode("utf-8"))

        assert content['success'] == True
        assert 'result' in content

        # check that the output is present
        assert '<h1>ViennaRNA Toolchain Output</h1>' in content['result']