from ruamel.yaml import YAML
from collections import UserDict


class data(UserDict):
    _yamler = YAML()
    def __init__(self, path):
        self.path = path
        yaml_data = data._yamler.load(path) if path.exists() else {}
        self.file_data = self.path.read_text(encoding = 'utf-8')
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

    def write_file(self, string):
        self.path.write_text(string, encoding='utf-8')
        self = data(self.path)