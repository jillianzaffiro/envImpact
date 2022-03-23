from flask import jsonify
import functools

from DescriptionProcessing.CBERT.BertPreprocessing import BertPreprocessor
from ImpactPredictor import get_impact_predictor, ImpactPredictor
from ProjectPredictor import get_project_predictor, ProjectPredictor
from Projects.ProjectBuilder import get_project_builder, ProjectBuilder
from Projects.ProjectTypes import ProjectType


def get_controller(logger):
    bpp = BertPreprocessor(max_len=64)
    pb = get_project_builder(logger, bpp)
    ip = get_impact_predictor(logger)
    pp = get_project_predictor(logger, bpp, pb)
    controller = PredictorController(logger, pb, pp, ip)
    return controller


def verify_json_request(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pc_self = args[0]
        request = args[1]
        req_body = request.get_json()
        if req_body is None:
            response_body = {
                'ErrorMsg': 'Request body invalid JSON object.'
            }
            response_status = 400
        else:
            response_body, response_status = func(pc_self, req_body, **kwargs)
        return response_body, response_status
    return wrapper


class PredictorController:
    def __init__(self, logger, project_builder: ProjectBuilder, project_predictor: ProjectPredictor, impact_predictor: ImpactPredictor):
        self.logger = logger
        self.pb = project_builder
        self.pp = project_predictor
        self.ip = impact_predictor

    def get_sector_list(self):
        self.logger.info("get_sector_list:")
        return jsonify(ProjectType.sector_list()), 200

    @verify_json_request
    def get_project_from_description(self, json_request):
        self.logger.info("get_project_from_description:")
        response_status = 200
        if 'description' not in json_request:
            response_body = {
                    'ErrorMsg': 'description is required'
                }
            response_status = 500
        else:
            description = json_request['description']
            sector_name = json_request.get('sector', None)
            project = self.pp.find_project_from_description(description, sector_name)
            response_body = {
                'Sector': project
            }
        return jsonify(response_body), response_status

    @verify_json_request
    def get_impact_from_project(self, json_request):
        self.logger.info("get_impact_from_project:")
        ok, project = self.pb.from_json(json_request)
        if ok:
            ok_a, ok_b, co2_a, co2_b = self.ip.get_co2(project)
            response_status = 200
            response_body = {
                'Project': project.to_json(),
                'CO2 Method 1': co2_a,
                'CO2 Method 2': co2_b
            }
        else:
            response_status = 400
            response_body = project
        return jsonify(response_body), response_status
