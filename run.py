#! /usr/env/python3

from ruamel.yaml import YAML
from collections import UserDict

# ===============================================
# about print: ----------------------------------
def add_indent(string, indent_int):
    indent = indent_int * ' '
    return indent + f"\n{indent}".join(string.split('\n'))

def list_dict_obj(dict_data:'dict or non-dict'):
    if isinstance(dict_data, (dict, UserDict)):
        flag = 'begin'
        for key, value in dict_data.items():
            result = result + '\n' if flag == 'non-begin' else ''
            flag = 'non-begin'
            if not isinstance(value, dict):
                result += f'{key}: {value}'
            else:
                result += f'{key}:\n' + add_indent(list_dict_obj(value), 4)
    else:
        result = str(dict_data)
    return result


# ===============================================
# about yaml: -----------------------------------
class data(UserDict):
    _yamler = YAML()
    def __init__(self, path):
        self.path = path
        super().__init__(data._yamler.load(path))

    def __getattribute__(self, name):
        if name in 'clear, pop, popitem, setdefault, update'.split(', '):
            super_ = super()
            self_ = self
            def result_func(*args, **kwargs):
                result = super_.__getattribute__(name)
                result = getattr(super_, name)(*args, **kwargs)
                self_._write()
                return result
            return result_func
        else:
            return super().__getattribute__(name)

    def _write(self):
        data._yamler.dump(self.data, self.path)

    def __delitem__(self, key):
        super().__delitem__(key)
        self._write()
    
    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self._write()


# ===============================================
# about file: -----------------------------------
class commander_base(object):
    def __init__(self, cwd):
        self.cwd = cwd
        self.toc = data(cwd /'toc.yml')
        self.config = data(cwd / 'config.yml')
        self.file_name = self.config['file_name']
        self.file = lambda suffix: cwd / (self.file_name + '.' + suffix)

    def run_ex(self, command, stdout = None):
        import subprocess
        subprocess.run(command, cwd=self.cwd, stdout=stdout)

    def rm(self, *file_paths):
        for file_path in file_paths:
            print('[rm]:', file_path.name)
            (self.cwd / file_path).unlink()

    def rm_by_suffix(self, suffix_without_dot):
        '''suffix_without_dot: look like 'pdf|tex|yml|' or else'''
        files = self.cwd.iterdir()
        suffixs = suffix_without_dot.split('|')
        for file in files:
            if file.suffix[1:] in suffixs:
                self.rm(file)

    def touch(self, string, path):
        with open(self.cwd / path, 'wt', encoding='utf-8') as file:
            print('[write]:', file.name)
            file.write(string)

    def list_toc(self):
        print(list_dict_obj(self.toc))

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
        self.toc = data(self.cwd /'toc.yml')
        self.config = data(self.cwd / 'config.yml')

    def xelatex_it(self):
        print('xelatex it')
        print('enter X to end it, see out in stdout.txt file\n > ', end='')
        self.run_ex(['xelatex', self.file('tex')], open(self.file('output.txt'), 'w+'))
        print('end of latex')

    def new(self):
        input_ = input("enter the file's name > ")
        index = '{:0>3}'.format(max(int(key) for key in self.toc) + 1)
        path = self.cwd / 'parts' / '{}.tex'.format(index)
        
        self.toc[index] = {'name': input_}

        import datetime
        today = datetime.date.today()
        # touch with: '\section{input_}\n\timetx{today_}
        self.touch(f'\\section{{{input_}}}\n\\timetx{{{today}}}\n\n', path)
        
        self.run_ex(['vim', path])

    def rm_note(self):
        self.list_toc()
        input_ = input('enter enter the index > ')

        self.toc.pop(input_)
        (self.cwd / 'parts' / f'{input_}.tex').unlink()

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
            print('need to add chrome in PATH, or change the run.py file\'s 138 line')


# ===============================================
# about main runner: ----------------------------
def help():
    help_doc = (
        '-------------------------------------\n'
        'help: show this\n'
        'run : run it\n'
        '?q  : quit it\n'
        'new : edit a new note\n'
        'rm  : rm a note\n'
        'list: list the note\n'
        'look: look the pdf file\n'
        'edit: edit a note'
    )
    print(add_indent(help_doc, 4))

if __name__ == '__main__':
    from pathlib import Path
    Test = False
    com = commander(Path.cwd())

    while True:
        input_ = input('(enter help for help)> ')
        com.reload()
        try:
            if input_ == 'run':
                com.run_it(Test=Test)
            elif input_ == 'help':
                help()
            elif input_ == 'new':
                com.new()
            elif input_ == '?q':
                break
            elif input_ == 'list':
                com.list_toc()
            elif input_ == 'rm':
                com.rm_note()
            elif input_ == 'look':
                com.look_it()
            elif input_ == 'edit':
                com.edit_file()
            else:
                print(f'no command named {input_}')
            print()
        except Exception as e:
            import traceback
            print(e, '\n')
            print('-' * 50)
            traceback.print_exc()
            print()