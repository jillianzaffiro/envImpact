import os


def get_config():
    return Config()


class Config:
    def __init__(self):
        self.FILE_TAG = None
        self.config()

    def config(self):
        if 'FILE_TAG' in os.environ:
            self.FILE_TAG = os.environ["FILE_TAG"]
        else:
            self.FILE_TAG = "ajp"
