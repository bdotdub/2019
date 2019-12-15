import os


class Settings:
    project_root: str

    def __init__(self) -> None:
        self.project_root = os.path.dirname(os.path.realpath(__file__))

    def config_path_for(self, scope: str, filename: str) -> str:
        return os.path.join(self.project_root, "config", scope, filename)

    def output_path_for(self, scope: str, filename: str) -> str:
        return os.path.join(self.project_root, "output", scope, filename)
