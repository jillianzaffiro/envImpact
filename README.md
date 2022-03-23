# service-ajp-environment-predictor
Environmental Predictor Engine for the AJP project

### Running tests
#### unit tests
`pytest tests/AllTests.py`

#### integration tests
```
docker build -t ajp-service .
docker run -p 8080:80 --name ajp-service ajp-service
pytest tests/api_tests.py
```

Alternatively, you can run the service within the IDE instead of docker.
Then, just run the tests
```
pytest tests/api_tests.py
```

## Docker
Running in docker requires a few steps.  The Flask framework provides a simple development
server as a convenience, but it is not production ready.  

### With no static assets
supervisor --> gunicorn --> app

### With static assets
Supervisor --> nginx --> gunicorn --> app

