from .yamldata import data
from .nodeobj import nodeobject_env

class commander_base(object):
    def __init__(self, cwd):
        current = self.config['current'] if 'current' in self.config else None
        self.cwd = cwd
        self.config = data(cwd / 'config.yml')
        self.obj_env = nodeobject_env(self.cwd, current)
        self.file = lambda suffix: cwd / (self.config['file_name'] + '.' + suffix)

    def reload(self):
        self.config = data(self.cwd / 'config.yml')

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

    def rm_useless(self):
        self.rm_by_suffix('aux|log|cls|tex|txt')

    def touch(self, string, path):
        with open(self.cwd / path, 'wt', encoding='utf-8') as file:
            print('[write]:', file.name)
            file.write(string)
        return path

    def list(self):
        print(self.obj_env)
    

class commander(commander_base):
    def __init__(self, cwd):
        super().__init__(cwd)

    def xelatex_it(self):
        print('xelatex it')
        print('enter X to end it, see out in stdout.txt file')
        print('-' * 50)
        self.run_ex(['xelatex', self.file('tex')])
        print('-' * 50)
        print('end of latex')

    def init(self):
        if 'current' in self.config:
            print('it is already inited')
            return
        root = self.obj_env.new('tree')
        self.config['current'] = root.hash
        self.config.write()
        self.obj_env.current = root

    def new(self):
        note = self.obj_env.new('note')

        title = input("enter the note's title > ")
        note['title'] = title
        note['parents'] = [self.obj_env.current.hash]
        self.obj_env.current['value'].append(note.hash)
        self.obj_env.current.write()
        
        self.run_ex(['vim', self.file('temp.tex')])
        if self.file('temp.tex').exists():
            note['text'] = self.file('temp.tex').read_text(encoding='utf-8')
            self.file('temp.tex').unlink()
            print('[rm]:', self.file('temp.tex'))
        note.write()

    def rm_note(self):
        self.list()
        input_ = input("enter the node's hash > ")
        node = self.obj_env.get_nodeobject(input_)
        node.rm()

    def edit_data(self, data, suffix):
        temp_file = self.touch(data, self.file('temp' + suffix))
        self.run_ex(['vim', temp_file])
        return temp_file.read_text(encoding='utf-8')

    def edit_raw_file(self):
        self.list()
        input_ = input('enter the hash > ')

        node = self.obj_env.get_nodeobject(input_)
        node.write_file(self.edit_data(node.file_data, 'yml'))

    def edit_file(self):
        self.list()
        input_ = input('enter the hash > ')

        node = self.obj_env.get_nodeobject(input_)
        node['text'] = self.edit_data(node['text'], 'tex')
        node.write()

    def run_it(self, Test=False):
        self.touch(self.config['cls_file_str'], self.file('cls'))
        item_numberer = 0
        result = r'\documentclass{PeterlitsNote}\begin{document}'
        for part in self.obj_env.current['value']:
            part_node = self.obj_env.get_nodeobject(part)
            result += f"\\section{{{part_node['title']}}}" + f"\\timetx{{{part_node['init_time']}}}\n\n"
            result += part_node['text'] + '\n\n'
        result += r'\end{document}'
        self.touch(result, self.file('tex'))
        print('-'*50, end='\n\n')
        self.xelatex_it()
        print('-'*50, end='\n\n')
        if not Test:
            self.rm_useless()

    def look_it(self):
        try:
            self.run_ex(['chrome', self.file('pdf')])
        except:
            print('need to add chrome in PATH, or change the command.py file\'s 128 line')


