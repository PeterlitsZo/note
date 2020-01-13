from .yamldata import data
from .timelib import long_time
from .hashlib_p import sha1_string
from .printlib import add_indent


class nodeobject_env(object):
    def __init__(self, cwd:'Path', current_node:'hash_string'=None):
        """
        get a nodeobject env,

        if there is not a current root node, let self.current to be None.
        """
        self.cwd = cwd / 'pigtime' / 'object'
        self.current = self.get_nodeobject(current_node) if current_node else None
        self.hash_set = set()
        self._reload_hash_set()

    def __str__(self):
        """
        show the string of self.current
        """
        return str(self.current)

    def _reload_hash_set(self):
        """
        reset the hash set, if you add or remove the file under this env, reload it
        """
        self.hash_set.clear()
        if self.cwd.exists():
            hash_file_iter = \
                (file for hashdir in self.cwd.iterdir() for file in hashdir.iterdir())
        else:
            hash_file_iter = []
        for hash_file in hash_file_iter:
            self.hash_set.add(hash_file.parent.name + hash_file.name.rsplit('.', 1)[0])

    def _get_full_hash(self, hash_str):
        """
        if find the full hash, then return will the hash's full string,
        else print what happen and then return None
        """
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
        """
        need a full or non-full hash string, then return the path of it.
        if use existed=False, then will return then path to build a new file
        --- you should make sure that why you use this 'existed' choose is to touch it.
        """
        full_hash = self._get_full_hash(hash_str) if existed else hash_str
        return self.cwd / full_hash[:2] / (full_hash[2:] + '.yml')

    def get_nodeobject(self, hash_str):
        """
        need a full or non-full hash string, then return the obj.
        you need to get a nodeobject by this way.
        """
        return nodeobject(self._get_full_hash(hash_str), self)
    
    def new(self, type):
        """
        get a new envobject, touch its file and write some important info
        """
        init_time = long_time()
        hash_str = sha1_string(init_time)
        new_node_data = data(self.get_path(hash_str, existed=False))
        new_node_data['type'] = type
        new_node_data['init_time'] = init_time
        new_node_data.write()
        return nodeobject(hash_str, self)


class nodeobject(data):
    def __new__(cls, full_hash, hash_data:'hash\'s data obj', env:'nodeobject_env'):
        """
        will return a nodeobject by the file of hash.
        """
        hash_data = data(env.get_path(full_hash))
        if hash_data['type'] == 'note':
            cls = nodeobject_note
        elif hash_data['type'] == 'tree':
            cls = nodeobject_tree
        else:
            raise ValueError('Unexcepection value {}'.format(hash_data['type']))
        return cls._init(full_hash, env)

    @classmethod
    def _init(cls, full_hash, env):
        self = object.__new__(cls)
        super(nodeobject, self).__init__(env.get_path(full_hash))
        self.env = env
        self.hash = full_hash
        return self

    def __init__(self, *args):
        pass

    def rm(self):
        """
        remove the nodeobject
        """
        if 'parents' in self:
            for parent in self['parents']:
                parent_node = self.env.get_nodeobject(parent)
                parent_node['value'].remove(self.hash)
                parent_node.write()
        self.del_file()
        if sum(1 for __ in self.path.parent.iterdir()) == 0:
            self.path.parent.rmdir()
        print('[rm]', self.hash)


class nodeobject_tree(nodeobject):
    """
    the tree nodeobject:
    func:
      - rm: remove itself.
      - list: print str of itself.
    data:
      - path: its file's path
      - env: its env's object. can get obj like it.
      - hash: its hash.
    """
    def __init__(self, *arg):
        self['value'] = self['value'] if 'value' in self else []
        self.childs= list(self.env.get_nodeobject(obj_hash) for obj_hash in self['value'])
        self.write()

    def __str__(self):
        result_head = self.hash[:6] + f"...: (type: {self['type']})\n"
        result = []
        for child in self.childs:
            result.append(str(child))
        result = result_head + add_indent('\n'.join(result), 4)
        return result

    def list(self):
        print(str(self))
    
    
class nodeobject_note(nodeobject):
    """
    the note nodeobject
    func:
      - rm: remove itself.
    data:
      - path: its file's path
      - env: its env's object. can get obj like it.
      - hash: its hash.
    """
    def str_with_command(self, command):
        if command == 'short':
            result = f"*{self.hash[:6]}...: title: {self['title']}"
        if command == 'long':
            result = f"*{self.hash[:6]}...: (type: {self['type']})"
            result_connect = '\n'.join(f"{c}: {self[c]}" for c in self if c in 'title init_time tags'.split())
            result += add_indent(result_connect, 4)
        return result

    def __str__(self):
        return self.str_with_command('short')