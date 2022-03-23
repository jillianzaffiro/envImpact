import requests
import pytest


@pytest.fixture()
def base_url(pytestconfig):
    return pytestconfig.getoption('loadbalancer')


@pytest.mark.api
def test_health_endpoint_returns_correct_response_body_and_status_code(base_url):
    response = requests.get(base_url+'/internals/health', verify=False)
    assert response.status_code == 200
    assert response.json()["Status"] == 'Healthy'


@pytest.mark.api
def test_prediction_route_returns_400_with_empty_json(base_url):
    response = requests.post(base_url+'/api/project/create', verify=False)
    assert response.status_code == 400


@pytest.mark.api
def test_prediction_route_returns_500_with_invalid_json(base_url):
    req = {'foo': 'bar'}
    response = requests.post(base_url+'/api/project/create', verify=False, json=req)
    assert response.status_code == 500
    assert response.json()['ErrorMsg'] == 'description is required'


@pytest.mark.api
def test_prediction_route_returns_200_with_valid_json(base_url):
    req = {'description': 'some description of a bridge'}
    response = requests.post(base_url+'/api/project/create', verify=False, json=req)
    assert response.status_code == 200

    resp_json = response.json()
    assert resp_json.get('ErrorMsg') is None
    print(f"RESPONSE FROM CREATE: {resp_json}")
    assert 'Sector' in resp_json
    sector = resp_json['Sector']
    assert 'BRIDGES' in sector
    other = sector['BRIDGES']
    assert 'project' in other
    project = other['project']
    assert 'project_type' in project
    assert project['project_type'] == 'bridges'
