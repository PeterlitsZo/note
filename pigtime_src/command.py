from .data import data
from .pigtime import pigenv

class commander_base(object):
    def __init__(self, cwd):
        self.cwd = cwd
        self.config = data(cwd / 'pigtime' / 'config.yml')
        self.pigenv = pigenv(self.cwd, self.config['current'])
        self.file = lambda suffix: cwd / (self.config['file_name'] + '.' + suffix)

    def reload(self):
        self.config = data(self.cwd / 'pigtime' / 'config.yml')

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
        with open(path, 'wt', encoding='utf-8') as file:
            print('[write]:', file.name)
            file.write(string)
        return path

    def list(self):
        print(self.pigenv)
    

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
        root = self.pigenv.new_pig('tree')
        with self.config as config:
            config['current'] = root.hash
        self.pigenv.current = root

    def new(self):
        note_pig = self.pigenv.new_pig('note')

        title = input("enter the note's title > ")
        with note_pig as note, self.pigenv.current as current:
            note['title'] = title
            note['parents'] = [self.pigenv.current.hash]
            current['value'].append(note_pig.hash)
        
            self.run_ex(['vim', self.file('temp.tex')])
            if self.file('temp.tex').exists():
                note['text'] = self.file('temp.tex').read_text(encoding='utf-8')
                self.file('temp.tex').unlink()
                print('[rm]:', self.file('temp.tex'))

    def rm_note(self):
        self.list()
        input_ = input("enter the node's hash > ")
        self.pigenv.remove_pig(input_)
        with self.config as config:
            if self.pigenv.current == None:
                config.pop('current')

    def edit_data(self, data, suffix):
        temp_file = self.touch(data, self.file('temp.' + suffix))
        self.run_ex(['vim', temp_file])
        return temp_file.read_text(encoding='utf-8')

    def edit_raw_file(self):
        self.list()
        input_ = input('enter the hash > ')

        node = self.pigenv.get_pig(input_)
        edited_data = node.path.read_text(encoding = 'utf-8')
        node.path.write_text(self.edit_data(edited_data, 'yml'), encoding = 'utf-8')
        node = self.pigenv.get_pig(input_)

    def edit_file(self):
        self.list()
        input_ = input('enter the hash > ')

        with self.pigenv.get_pig(input_) as node:
            node['text'] = self.edit_data(node['text'], 'tex')

    def run_it(self, Test=False):
        self.touch(self.config['cls_file_str'], self.file('cls'))
        item_numberer = 0
        result = r'\documentclass{PeterlitsNote}\begin{document}'
        for part in self.pigenv.current['value']:
            part_node = self.pigenv.get_pig(part)
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


