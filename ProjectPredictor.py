from Common.Logger import Logger

from Projects.ProjectTypes import ProjectType
from Projects.ProjectBuilder import ProjectBuilder
from DescriptionProcessing.CBERT.BertPreprocessing import BertPreprocessor
from DescriptionProcessing.CBERT.CBertModel import CBert


def get_project_predictor(logger, bpp: BertPreprocessor, pb: ProjectBuilder):
    num_labels = ProjectType.num_sectors()
    cbert = CBert(logger, num_labels, "models", "CV0.1")
    pp = ProjectPredictor(logger, bpp, cbert, pb)
    return pp


class ProjectPredictor:
    def __init__(self, logger: Logger, bpp: BertPreprocessor, cbert: CBert, project_builder: ProjectBuilder):
        self._lgr = logger
        self._bpp = bpp
        self._cbert = cbert
        self._pb = project_builder

    def find_project_from_description(self, description, sector_name=None):
        if sector_name is None:
            in_text = [description, ]
            input_ids, attention_masks = self._bpp.preprocess_data(in_text)
            results = self._cbert.predict(input_ids, attention_masks)
            project_types = ProjectType.translate_prediction(results)
            project_types = self._get_top_2(project_types)
            results = {}
            for t, v in project_types:
                cur_project = self._get_project_for_type(t, v, description)
                results[t] = cur_project
        else:
            cur_project = self._get_project_for_type(sector_name, 1.00, description)
            results = {sector_name: cur_project}

        return results

    def _get_project_for_type(self, project_type, confidence, description):
        cur_project = {'confidence': confidence}
        ok, project = self._pb.from_project_type(project_type)
        if ok:
            parse_ok, errs = project.params_from_description(description)
            p_json = project.to_json()
            if not parse_ok:
                p_json['errors'] = errs
            cur_project['project'] = p_json
        else:
            cur_project['project'] = f"Cannot construct project of type {project_type}"
        return cur_project

    @staticmethod
    def _get_top_2(sectors):
        s_s = sorted(sectors.items(), key=lambda x: x[1], reverse=True)
        s_s_a = [(k, v) for k, v in s_s]
        return s_s_a[:2]
