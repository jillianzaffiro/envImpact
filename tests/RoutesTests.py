import unittest
from app import create_app


class RouteTests(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        # with app.test_client() as client:
        #     yield client
        self.client = app.test_client()

    def test_health_endpoint_accepts_get_request(self):
        # Arrange

        # Act
        rv = self.client.get('/internals/health')

        # Assert
        assert rv.status_code == 200
        assert rv.json["Status"] == 'Healthy'

    def test_health_endpoint_does_not_accept_post_request(self):
        # Arrange

        # Act
        rv = self.client.post('/internals/health')

        # Assert
        assert rv.status_code == 405

    def test_cannot_get_create_route(self):
        # Arrange

        # Act
        rv = self.client.get("/api/project/create")

        # Assert
        assert 405 == rv.status_code

    def test_post_create_with_no_json_errors(self):
        # Arrange

        # Act
        rv = self.client.post("/api/project/create")

        # Assert
        assert 400 == rv.status_code
        self._validate_error_response(rv.json, "Request body invalid JSON object.")

    def test_post_create_with_empty_json_errors(self):
        # Arrange

        # Act
        rv = self.client.post("/api/project/create", json={})

        # Assert
        assert 500 == rv.status_code
        self._validate_error_response(rv.json, "description is required")

    def test_post_create_with_valid_json_OK(self):
        # Arrange
        json_dict = {'description': "some description"}

        # Act
        rv = self.client.post("/api/project/create", json=json_dict)

        # Assert
        assert 200 == rv.status_code
        json_res = rv.json
        assert "Sector" in json_res

    @staticmethod
    def _validate_error_response(json_resp, msg):
        assert 1 == len(json_resp)
        assert "ErrorMsg" in json_resp
        assert json_resp["ErrorMsg"].startswith(msg)
