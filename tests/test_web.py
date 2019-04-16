import pytest, requests

# this file contains a selection of pytest tests for the web tool
@pytest.mark.describe('Page Codes')
class TestPageCodes():

    @pytest.mark.it('Returns HTTP code 200 when requesting the homepage')
    def test_homepage(self):
        assert requests.get('http://web:5000').status_code == 200

    @pytest.mark.it('Returns HTTP code 200 when requesting the CNEAT configuration page')
    def test_cneat(self):
        assert requests.get('http://web:5000/cneat').status_code == 200

    @pytest.mark.it('Returns HTTP code 404 when requesting the analysis page with no analysis code')
    def test_analysis_blank(self):
        assert requests.get('http://web:5000/analysis/').status_code == 404

    @pytest.mark.it('Returns HTTP code 404 when requesting the analysis page with an invalid code')
    def test_analysis_invalid(self):
        assert requests.get('http://web:5000/analysis/test').status_code == 404

    @pytest.mark.it('Returns HTTP code 404 when requesting the status of a blank analysis')
    def test_analysis_status_blank(self):
        assert requests.get('http://web:5000/get_analysis_status/').status_code == 404

    @pytest.mark.it('Returns HTTP code 404 when requesting the status of an invalid analysis')
    def test_analysis_status_invalid(self):
        assert requests.get('http://web:5000/get_analysis_status/test').status_code == 404

    @pytest.mark.it('Returns HTTP code 404 when requesting the data of a blank task')
    def test_task_data_blank(self):
        assert requests.get('http://web:5000/get_task_data/').status_code == 404

    @pytest.mark.it('Returns HTTP code 404 when requesting the data of an invalid task')
    def test_task_data_invalid(self):
        assert requests.get('http://web:5000/get_analysis_data/test').status_code == 404


@pytest.mark.describe('CNEAT: New Analysis')
class TestCneatNewAnalysis():

    @pytest.mark.it('Returns a HTTP code 400 when requesting a new analysis with no configuration')
    def test_none(self):
        request = requests.post('http://web:5000/new_analysis')

        assert request.status_code == 400

    @pytest.mark.it('Returns a HTTP code 400 when requesting a new analysis with an empty configuration')
    def test_blank(self):
        config = {}
        request = requests.post('http://web:5000/new_analysis', json=config)

        assert request.status_code == 400