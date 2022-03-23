import csv
import json
import re
from os import path

from DescriptionProcessing.ProjectDescription import ProjectDescription

# Data from CG-LA regarding the American Jobs Plan (ajp)
DATA_DIR = "../service-ajp-environment-predictor"
RAW_FILE = f"{DATA_DIR}/exp_projects.csv"
DATA_FILE = f"{DATA_DIR}/project_clean.csv"


class ProjectDataset:
    def __init__(self, logger, ajp_data_src=None):
        if ajp_data_src is None:
            ajp_data_src = DATA_FILE
        self._lgr = logger
        self.__projects = self._get_project_data(ajp_data_src)

    def get_training_data(self):
        sentences = []
        labels = []
        for p in self.__projects:
            sentences.append(p.description)
            category, lbl = p.get_label()
            labels.append(lbl)
        return sentences, labels

    def save_csv_training(self):
        data_file = "datasets/AJP_TrainingText.csv"
        with open(data_file, 'w') as out_file:
            for p in self.__projects:
                desc = p.description.replace('\n', ' ').replace('\r', ' ')
                category, lbl = p.get_label()
                out_file.write(f'{category},"{desc}"\n')

    def _get_project_data(self, ajp_data_src):
        data_file = "datasets/AJP_TrainingText.json"
        if path.exists(data_file):
            self._lgr.info("Getting cached AJP data")
            projects = []
            with open(data_file, 'r') as in_file:
                for line in in_file:
                    json_data = json.loads(line)
                    p = ProjectDescription.from_json(json_data)
                    projects.append(p)
            return projects
        else:
            projects = self._get_project_descriptions(ajp_data_src)
            self._lgr.info(f"Found {len(projects)} projects in AJP file")
            with open(data_file, 'w') as out_file:
                for p in projects:
                    p = p.to_json()
                    out_file.write(json.dumps(p) + "\n")
            return projects

    def _get_project_descriptions(self, data_file):
        self._lgr.info(f"Reading AJP data from {data_file}")
        projects = []
        with open(data_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                p = self.project_from_json(row, len(projects))
                projects.append(p)
        return projects

    @staticmethod
    def project_from_json(row, line_num):
        p = ProjectDescription()
        p.project_id = row['pid']
        p.name = row['projectname']
        p.description = row['description']
        p.keywords = row['keywords']
        p.country = row['country']
        p.location = row['location']
        p.sector = row['sector']
        p.subsector = row['subsector']
        p.budget = row['totalbudget']
        p.lat = row['lat']
        p.long = row['lng']
        g = row['geocode']
        if g is not None:
            g = g.replace("'", '"')
            g = re.sub(r'([a-zA-Z ])""([a-zA-Z ])', r'\1\2', g)
            if g != "":
                try:
                    p.geocode = json.loads(g)
                except Exception:
                    print(f"OOPS: {line_num}")
        return p

    def show_data_metrics(self, bpp):
        max_len = 0
        total_count = 0
        project_count = 0
        exceed = [0, 0, 0, 0, 0]
        sectors = {}
        subsectors = {}
        labels = {}

        for p in self.__projects:
            # Tokenize the text with all special tokens.
            tokens, input_ids = bpp.tokenize_one_sentence(p.description)
            char_count = len(input_ids)
            for hundred in [1, 2, 3, 4, 5]:
                if char_count > hundred * 100:
                    exceed[hundred - 1] += 1

            project_count += 1
            total_count += char_count
            max_len = max(max_len, len(input_ids))

            if p.sector in sectors:
                sectors[p.sector] += 1
            else:
                sectors[p.sector] = 1

            if p.subsector in subsectors:
                subsectors[p.subsector] += 1
            else:
                subsectors[p.subsector] = 1

            label, val = p.get_label()
            if label in labels:
                labels[label] += 1
            else:
                labels[label] = 1

        ave = total_count // project_count
        print(f'Num projects: {project_count}')
        print(f'Max sentence length: {max_len},  ave={ave}')
        for hundred in [1, 2, 3, 4, 5]:
            print(f"{exceed[hundred - 1]} are > {hundred * 100}.")

        """
        Num projects: 4409
        Max sentence length: 1170,  ave=131
        2213 are > 100.
        944 are > 200.
        390 are > 300.
        183 are > 400.
        84 are > 500.
        """

        print(sectors)
        """
        {'Transport': 2054, 
         '': 443, 
         'Retail': 1, 
         'Water': 606, 
         'Social': 142, 
         'Energy': 720, 
         'Information & Communication Technologies': 48, 
         'Urban Planning & Design': 77, 
         'Mining & Related': 35, 
         'Logistics': 66, 
         'Oil & Gas': 132, 
         'Other': 22, 
         'Industrial': 22, 
         'Real Estate': 9, 
         'Tourism & Related': 31, 
         'Energy Efficiency/ Electric Equipment': 1}
        """

        print(subsectors)
        """{
            'Transit': 582, 
            'Urban Highways': 219, 
            '': 443, 
            'Airports & Logistics': 225, 
            'Supermarkets': 1, 
            'Waste Water': 166, 
            'Other': 611, 
            'Highways': 388, 
            'Hospitals': 54, 
            'Bridges': 111, 
            'Multimodal': 56, 
            'Generation — Renewables': 305, 
            'Ports & Logistics': 252, 
            'Generation — Coal': 11, 
            'Generation — Hydro': 128, 
            'Broadband': 6, 
            'Jails': 6, 
            'Industrial Water (Treatment/Re-use)': 26, 
            'Transmission': 119, 
            'Generation — Natural Gas': 53, 
            'Distribution': 27, 
            'Pipelines —\xa0Gas': 56, 
            'Tunnels': 40, 
            'Freight Rail': 40, 
            'Potable': 37, 
            'Housing': 16, 
            'Water Supply': 295, 
            'Generation — Nuclear': 11, 
            'Water Resources': 25, 
            'Extraction': 25, 
            'Pipelines —\xa0Liquid': 13, 
            'Cable': 7, 
            'Led / power systems': 1, 
            'Electricity Generation': 4, 
            'Irrigation': 21, 
            'Compressor Stations': 9, 
            'Generation — Oil-Fired': 15, 
            'Fixed Line': 1, 
            'Wireless': 4}
        """
        print(labels)
        """
            'RAILWAYS': 622, 
            'ROADS': 607, 
            'OTHER': 731, 
            'TRANSPORT': 719, 
            'BUILDINGS': 54, 
            'WATERWORKS': 606, 
            'HOSPITALS': 54, 
            'BRIDGES': 111, 
            'ENERGY': 857, 
            'COMMUNICATIONS': 48}
        """


def make_clean():
    rows = []
    sectors = {}
    with open(RAW_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        line_num = 0
        for row in reader:
            line_num += 1
            p = ProjectDataset.project_from_json(row, line_num)
            if p.sector in sectors:
                sectors[p.sector] += 1
            else:
                sectors[p.sector] = 1

            category, label = p.get_label()
            print(f"PID:{p.project_id} sector:{category}")
            rows.append(p)
    print(sectors)
    print(f"found {len(rows)} records")
    "cat $RAW_FILE | sed 's/\\\\//g' |sed s/\'\"/\'/g > $DATA_FILE"
    return rows


if __name__ == "__main__":
    make_clean()
