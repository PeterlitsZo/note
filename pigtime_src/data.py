from ruamel.yaml import YAML
from collections import UserDict


class data(UserDict):
    _yamler = YAML()
    def __init__(self, path):
        yaml_data = data._yamler.load(path) if path.exists() else {}
        super().__init__(yaml_data)
        self.path = path

    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        return None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.write()
        
    def _touch_data_file(self):
        if not self.path.exists():
            for parent_path in reversed(self.path.parents):
                if not parent_path.exists():
                    parent_path.mkdir()
            else:
                self.path.touch()
        
    def write(self, string = None):
        self._touch_data_file()
        if string:
            self.path.write_text(string, encoding='utf-8')
        else:
            data._yamler.dump(self.data, self.path)
        self = data(self.path)