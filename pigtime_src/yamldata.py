from ruamel.yaml import YAML
from collections import UserDict


class data(UserDict):
    _yamler = YAML()
    def __init__(self, path):
        self.path = path
        if path.exists():
            yaml_data = data._yamler.load(path)
        else:
            yaml_data = {}
        assert isinstance(yaml_data, dict)
        super().__init__(yaml_data)

    def del_file(self):
        self.path.unlink()

    def _touch_data_file(self):
        if not self.path.exists():
            for parent_path in reversed(self.path.parents):
                if not parent_path.exists():
                    parent_path.mkdir()
            else:
                self.path.touch()
        
    def write(self):
        self._touch_data_file()
        data._yamler.dump(self.data, self.path)