from flask import jsonify, request
from flask_cors import cross_origin
from Controller import PredictorController


def add(log, app, ctl: PredictorController):
    """
    Adds routes to the flask app.
    :param ctl: Controller to translate json to internal objects
    :param log: The instantiated logger
    :param app: The flask app
    :return: The flask app
    """
    log.info('Adding routes.')

    @app.route('/', methods=['GET'])
    @cross_origin()
    def root():
        resp = 'Welcome to the Environmental Impact Predictor Service'
        return resp, 200

    @app.route('/internals/health', methods=['GET'])
    @cross_origin()
    def health():
        resp = {
            "Status": "Healthy"
        }
        return jsonify(resp), 200

    app = add_app_routes(app, ctl)

    return app


def add_app_routes(app, controller: PredictorController):
    @app.route("/api/project/sectors", methods=['GET'])
    def get_sector_list():
        return controller.get_sector_list()

    @app.route("/api/project/create", methods=['POST'])
    def get_project_from_description():
        return controller.get_project_from_description(request)

    @app.route("/api/project/co2", methods=['POST'])
    def get_co2_from_project():
        return controller.get_impact_from_project(request)

    return app
