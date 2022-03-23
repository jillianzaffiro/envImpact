from app import PORT


def pytest_addoption(parser):
    parser.addoption('--loadbalancer', action='store', default=f'http://localhost:{PORT}')
