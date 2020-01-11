# ==============================================
# about time: ----------------------------------
import datetime
def long_time():
    """ from year to microsenced """
    return str(datetime.datetime.now())

def short_time():
    """ from year to day """
    return str(datetime.date.today())


# ===============================================
# about print: ----------------------------------
def add_indent(string, indent_int):
    indent = indent_int * ' '
    return indent + f"\n{indent}".join(string.split('\n'))


# ===============================================
# about yaml: -----------------------------------
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

    def __getattribute__(self, name):
        if name in 'clear, pop, popitem, setdefault, update'.split(', '):
            super_ = super()
            self_ = self
            def result_func(*args, **kwargs):
                result = getattr(super_, name)(*args, **kwargs)
                self_.write()
                return result
            return result_func
        else:
            return super().__getattribute__(name)

    def __delitem__(self, key):
        super().__delitem__(key)
        self.write()
    
    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self.write()

    def del_file(self):
        self.path.unlink()
        del self

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


# ===============================================
# about noteobject: -----------------------------
class nodeobject_env(object):
    def __init__(self, cwd, current_node=None):
        self.cwd = cwd / 'pigtime' / 'object'
        if current_node:
            self.current = self.get_nodeobject(current_node)
        else:
            self.current = None
        self._reload_hash_list()

    def __str__(self):
        return str(self.current)

    def _reload_hash_list(self):
        self.hash_list = []
        if self.cwd.exists():
            for hash_dir in self.cwd.iterdir():
                for hash_file in hash_dir.iterdir():
                    self.hash_list.append(hash_dir.name + hash_file.name.rsplit('.', 1)[0])

    def _get_full_hash(self, hash):
        result = []

        self._reload_hash_list()
        for item in self.hash_list:
            if item.startswith(hash):
                result.append(item)
        if len(result) > 1:
            print('the given hash is too short to get a full one')
            print('... or this is a wrong hash')
        elif len(result) == 0:
            print(f'there is no hash match {hash}')
        else:
            return result[0]

    def _sha1_string(self, string):
        import hashlib
        hashed_string = string.encode('utf-8')
        return hashlib.sha1(hashed_string).hexdigest()

    def get_path(self, hash, existed=True):
        full_hash = hash
        if existed:
            full_hash = self._get_full_hash(hash)
        path = self.cwd / full_hash[:2] / (full_hash[2:] + '.yml')
        return path

    def get_nodeobject(self, hash):
        return nodeobject(hash, self)
    
    def new(self, type):
        init_time = long_time()
        hash = self._sha1_string(init_time)
        
        new_node_data = data(self.get_path(hash, existed=False))
        new_node_data['type'] = type
        new_node_data['init_time'] = init_time
        return nodeobject(hash, self)


class nodeobject(data):
    def __new__(cls, hash, env:'nodeobject_env'):
        node_type = data(env.get_path(hash))['type']
        if node_type == 'note':
            cls = nodeobject_note
        elif node_type == 'tree':
            cls = nodeobject_tree
        else:
            raise ValueError('Unexcepection value {}'.format(node_data['type']))
        return cls._init(hash, env)

    @classmethod
    def _init(cls, hash, env):
        self = object.__new__(cls)
        super(nodeobject, self).__init__(env.get_path(hash))
        self.env = env
        self.hash = hash
        self.type = self['type']
        return self

    def __init__(self, *args):
        # do nothing
        pass

    def rm(self):
        for parent in self['parent']:
            nodeobject(parent, self.env)['value'].pop(self.hash)
        self.del_file()
        if len(list(self.path.parent.iterdir())) == 0:
            self.path.parent.unlink()


class nodeobject_tree(nodeobject):
    def list(self):
        print(str(self))

    def __str__(self):
        result_head = self.hash[:6] + f"...:(type: {self['type']})\n"
        result = []
        for nodeobject_hash in self['value']:
            node = nodeobject(nodeobject_hash, self.env)
            result.append(str(node))
        result = result_head + add_indent('\n'.join(result), 4)
        return result


class nodeobject_note(nodeobject):
    def __str__(self):
        result = '* {}...:\n'.format(self.hash[:6])
        result_connect = '\n'.join([f'{c}: {self[c]}' for c in self if c != 'text'])
        result += add_indent(result_connect, 4)
        return result


# ===============================================
# about file: -----------------------------------
class commander_base(object):
    def __init__(self, cwd):
        self.cwd = cwd
        self.config = data(cwd / 'config.yml')
        current = self.config['current'] if 'current' in self.config else None
        self.obj_env = nodeobject_env(self.cwd, current)
        self.file_name = self.config['file_name']
        self.file = lambda suffix: cwd / (self.file_name + '.' + suffix)

    def run_ex(self, command, stdout = None):
        import subprocess
        subprocess.run(command, cwd=self.cwd, stdout=stdout)

    def rm(self, file_paths:'iterable'):
        for file_path in file_paths:
            print('[rm]:', file_path.name)
            (self.cwd / file_path).unlink()

    def rm_by_suffix(self, suffix_without_dot):
        '''suffix_without_dot: look like 'pdf|tex|yml|' or else'''
        files = self.cwd.iterdir()
        suffixs = suffix_without_dot.split('|')
        self.rm(file for file in files if file.suffix[1:] in suffixs)

    def touch(self, string, path):
        with open(self.cwd / path, 'wt', encoding='utf-8') as file:
            print('[write]:', file.name)
            file.write(string)

    def list_toc(self):
        print(self.current)
    
    def list(self):
        print(self.obj_env)
    
    def rm_useless(self):
        self.rm_by_suffix('aux|log|cls|tex|txt')

    def touch_tex_file(self):
        string = r'\documentclass{PeterlitsNote}\begin{document}'
        for key in self.toc:
            string += f'\\input{{parts/{key}}}'
        string += r'\end{document}'
        self.touch(string, self.file('tex'))


class commander(commander_base):
    def __init__(self, cwd):
        super().__init__(cwd)

    def reload(self):
        self.config = data(self.cwd / 'config.yml')

    def xelatex_it(self):
        print('xelatex it')
        print('enter X to end it, see out in stdout.txt file\n > ', end='')
        self.run_ex(['xelatex', self.file('tex')], open(self.file('output.txt'), 'w+'))
        print('end of latex')

    def init(self):
        if 'current' in self.config:
            print('it is already inited')
            return
        root = self.obj_env.new('tree')
        root['value'] = []
        self.config['current'] = root.hash
        self.obj_env.current = root

    def new(self):
        note = self.obj_env.new('note')

        title = input("enter the note's title > ")
        note['title'] = title
        note['parent'] = self.obj_env.current.hash
        self.obj_env.current['value'].append(note.hash)
        self.obj_env.current.write()
        
        self.run_ex(['vim', self.file('temp.tex')])
        if self.file('temp.tex').exists():
            note['text'] = self.file('temp.tex').read_text(encoding='utf-8')
            self.file('temp.tex').unlink()
        else:
            # !
            self.rm_note()

    def rm_note(self):
        self.list_toc()
        input_ = input("enter the node's hash > ")
        node = nodeobject(input_, self.cwd)
        node.rm()

    def edit_file(self):
        self.list_toc()
        input_ = input('enter enter the index > ')

        path = self.cwd / 'parts' / '{}.tex'.format(input_)
        self.run_ex(['vim', path])

    def run_it(self, Test=False):
        self.touch(self.config['cls_file_str'], self.cwd / self.file('cls'))
        self.touch_tex_file()
        print('-'*50, end='\n\n')

        self.xelatex_it()
        print('-'*50, end='\n\n')
        
        if not Test:
            self.rm_useless()

    def look_it(self):
        try:
            self.run_ex(['chrome', self.file('pdf')])
        except:
            print('need to add chrome in PATH, or change the run.py file\'s 291 line')


# ===============================================
# about main runner: ----------------------------
def help():
    help_doc = (
        '-------------------------------------\n'
        'edit the book:\n'
        '    init: init a root book\n'
        '    new : edit a new note\n'
        '    rm  : rm a note\n'
        '    edit: edit a note\n\n'
        'show around:\n'
        '    run : run it\n'
        '    list: list the note\n'
        '    look: look the pdf file\n\n'
        'others:\n'
        '    help: show this\n'
        '    ?q  : quit it\n'
        '-------------------------------------'
    )
    print(add_indent(help_doc, 4))

if __name__ == '__main__':
    from pathlib import Path
    Test = False
    com = commander(Path.cwd())
    print('enter help for help')
    print('-'*50)
    while True:
        input_ = input('> ')
        com.reload()
        try:
            # !this
            if input_ == 'run':
                com.run_it(Test=Test)
            elif input_ == 'help':
                help()
            elif input_ == 'new':
                com.new()
            elif input_ == '?q':
                break
            elif input_ == 'list':
                com.list()
            # !this
            elif input_ == 'rm':
                com.rm_note()
            elif input_ == 'look':
                com.look_it()
            # !this
            elif input_ == 'edit':
                com.edit_file()
            elif input_ == 'init':
                com.init()
            elif input_ == '':
                continue
            else:
                print(f'no command named {input_}')
        except Exception as e:
            import traceback
            print(e, '\n')
            print('-' * 50)
            traceback.print_exc()
        print()