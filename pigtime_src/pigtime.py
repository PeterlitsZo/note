from .data import data
from .units import long_time, sha1_string, add_indent
import copy


class pigenv(object):
    def __init__(self, cwd:'Path', current_node:'hash_string'=None):
        self.cwd = cwd / 'pigtime' / 'object'
        self.current = self.get_pig(current_node) if current_node else None

    def __str__(self):
        return str(self.current)

    def _hash_set(self):
        hash_file_iter = []
        if self.cwd.exists(): # self.current need this function.
            for hashdir in self.cwd.iterdir():
                for file in hashdir.iterdir():
                    hash_file_iter.append(file)
        hashstr = lambda p: p.parent.name + p.name.rsplit('.', 1)[0]
        return set(hashstr(hash_file) for hash_file in hash_file_iter)

    def _full_hash(self, hash_str):
        result = [item for item in self._hash_set() if item.startswith(hash_str)]
        if len(result) == 1:
            return result[0]
        raise ValueError(hash_str)

    def get_pig_path(self, hash_str, existed=True):
        full_hash = self._full_hash(hash_str) if existed else hash_str
        return self.cwd / full_hash[:2] / (full_hash[2:] + '.yml')

    def get_pig(self, hash_str):
        return pig(self._full_hash(hash_str), self)
    
    def new_pig(self, type):
        init_time = long_time()
        hash_str = sha1_string(init_time)

        # config by type:
        with data(self.get_pig_path(hash_str, existed=False)) as pigdata:
            pigdata['type'] = type
            pigdata['init_time'] = init_time
            pigdata['parents'] = []
            if type == 'tree':
                pigdata['value'] = []
            if type == 'note':
                pigdata['title'] = ''
                pigdata['text'] = ''
        return pig(hash_str, self)

    def remove_pig(self, hash_str):
        pig = self.get_pig(hash_str)
        if self.current.hash == pig.hash:
            if len(pig['parents']) != 0:
                self.current = self.get_pig(pig['parents'][0])
            else:
                self.current = None
        for parent in pig['parents']:
            parent = self.get_pig(parent)
            with parent as parent_pig:
                parent_pig['value'].remove(pig.hash)
        pig.path.unlink()
        if sum(1 for __ in pig.path.parent.iterdir()) == 0:
            pig.path.parent.rmdir()


class pig(object):
    def __new__(cls, full_hash, env:'nodeobject_env'):
        hash_data = data(env.get_pig_path(full_hash))
        if hash_data['type'] == 'note':
            return object.__new__(note_pig)
        elif hash_data['type'] == 'tree':
            return object.__new__(tree_pig)
        else:
            raise ValueError('Unexcepection value {}'.format(hash_data['type']))
        
    def __init__(self, full_hash, env):
        self.data = data(env.get_pig_path(full_hash))
        self.env = env
        self.hash = full_hash
        self.path = self.env.get_pig_path(self.hash)

    def __enter__(self):
        return self.data

    def __exit__(self, *args):
        self.data.write()

    def __getitem__(self, key):
        return copy.deepcopy(self.data[key])

    def remove(self):
        self.env.remove_pig(self.hash)


class tree_pig(pig):
    def __str__(self):
        with self as pig:
            result_head = self.hash[:6] + f"...: (type: {pig['type']})\n"
            result = []
            childs= list(self.env.get_pig(obj_hash) for obj_hash in pig['value'])
            for child in childs:
                result.append(str(child))
            result = result_head + add_indent('\n'.join(result), 4)
            return result

    
class note_pig(pig):
    def __str__(self):
        with self as pig:
            return f"*{self.hash[:6]}...: title: {pig['title']}"