from .yamldata import data
from .timelib import long_time
from .hashlib_p import sha1_string
from .printlib import add_indent


class nodeobject_env(object):
    def __init__(self, cwd:'Path', current_node:'hash_string'=None):
        """ get a nodeobject env,

        if there is not a current root node, let self.current to be None"""
        self.cwd = cwd / 'pigtime' / 'object'
        self.current = self.get_nodeobject(current_node) if current_node else None
        self.hash_set = set()
        self._reload_hash_set()

    def __str__(self):
        self.current = self.get_nodeobject(self.current.hash)
        return str(self.current)

    def _reload_hash_set(self):
        self.hash_set = set()
        if self.cwd.exists():
            hash_file_iter = \
                (file for hashdir in self.cwd.iterdir() for file in hashdir.iterdir())
        else:
            hash_file_iter = []
        for hash_file in hash_file_iter:
            self.hash_set.add(hash_file.parent.name + hash_file.name.rsplit('.', 1)[0])

    def _get_full_hash(self, hash_str):
        self._reload_hash_set()
        result = [item for item in self.hash_set if item.startswith(hash_str)]
        if len(result) > 1:
            print('the given hash is too short to get a full one')
            print('... or this is a wrong hash')
        elif len(result) == 0:
            print(f'there is no hash match {hash_str}')
        else:
            return result[0] 

    def get_path(self, hash_str, existed=True):
        full_hash = self._get_full_hash(hash_str) if existed else hash_str
        path = self.cwd / full_hash[:2] / (full_hash[2:] + '.yml')
        return path

    def get_nodeobject(self, hash_str):
        full_hash = self._get_full_hash(hash_str)
        return nodeobject(full_hash, data(self.get_path(hash_str)), self)
    
    def new(self, type):
        init_time = long_time()
        hash_str = sha1_string(init_time)
        new_node_data = data(self.get_path(hash_str, existed=False))
        new_node_data['type'] = type
        new_node_data['init_time'] = init_time
        new_node_data.write()
        return nodeobject(hash_str, new_node_data, self)


class nodeobject(data):
    def __new__(cls, full_hash, hash_data:'hash\'s data obj', env:'nodeobject_env'):
        if hash_data['type'] == 'note':
            cls = nodeobject_note
        elif hash_data['type'] == 'tree':
            cls = nodeobject_tree
        else:
            raise ValueError('Unexcepection value {}'.format(hash_data['type']))
        return cls._init(full_hash, hash_data, env)

    @classmethod
    def _init(cls, full_hash, hash_data, env):
        self = object.__new__(cls)
        super(nodeobject, self).__init__(hash_data.path)
        self.env = env
        self.hash = full_hash
        self.type = self['type']
        return self

    def __init__(self, *args):
        self._reload_counter()

    def _reload_counter(self):
        self._under_same_hash_dir_counter = sum(1 for __ in self.path.parent.iterdir())

        if self._under_same_hash_dir_counter == 0:
            self.path.parent.rmdir()

    def rm(self):
        for parent in self['parents']:
            parent_node = self.env.get_nodeobject(parent)
            parent_node['value'].remove(self.hash)
            parent_node.write()
        self.del_file()
        self._reload_counter()
        print('[rm]', self.hash)


class nodeobject_tree(nodeobject):
    def __init__(self, *arg):
        self['value'] = self['value'] if 'value' in self else []
        self.childs= list(self.env.get_nodeobject(obj_hash) for obj_hash in self['value'])

    def list(self):
        print(str(self))

    def __str__(self):
        result_head = self.hash[:6] + f"...: (type: {self['type']})\n"
        result = []
        for nodeobject_hash in self['value']:
            result.append(str(self.env.get_nodeobject(nodeobject_hash)))
        result = result_head + add_indent('\n'.join(result), 4)
        return result


class nodeobject_note(nodeobject):
    def __str__(self):
        result = '*{}...: (type: {})\n'.format(self.hash[:6], self['type'])
        result_connect = '\n'.join([f'{c}: {self[c]}' for c in self if c in 'title init_time'.split()])
        result += add_indent(result_connect, 4)
        return result