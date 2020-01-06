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
_yamler = YAML()

class data(UserDict):
    def __init__(self, path):
        self.path = path
        super().__init__(_yamler.load(path))

    def _write(self):
        _yamler.dump(self.data, self.path)

    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self._write()

    def pop(self, key):
        self.data.pop(key)
        self._write()


# ===============================================
# about file: -----------------------------------
class commander(object):
    def __init__(self, cwd):
        self.cwd = cwd
        self.toc = data(cwd /'toc.yml')
        self.config = data(cwd / 'config.yml')
        self.file_name = self.config['file_name']
        self.file = lambda suffix: cwd / (self.file_name + '.' + suffix)

    def _run_ex(self, command, stdout=None):
        import subprocess
        subprocess.run(command, cwd=self.cwd, stdout=stdout)

    def _rm_by_suffix(self, suffix):
        for file in self.cwd.iterdir():
            if file.suffix in suffix.split('|'):
                print('rm:', file.name)
                file.unlink()

    def rm_useless(self):
        self._rm_by_suffix('.aux|.log|.cls|.tex|.txt')

    def touch_file(self, string, path):
        with open(self.cwd / path, 'wt', encoding='utf-8') as file:
            print('write:', file.name)
            file.write(string)

    def touch_tex_file(self):
        string = r'\documentclass{PeterlitsNote}\begin{document}'
        for key in self.toc:
            string += f'\\input{{parts/{key}}}'
        string += r'\end{document}'
        self.touch_file(string, self.file('tex'))

    def xelatex_it(self):
        print('xelatex it')
        print('enter X to end it, see out in stdout.txt file\n > ', end='')
        self._run_ex(['xelatex', self.file('tex')], open(self.file('output.txt'), 'w+'))
        print('end of latex')

    def new(self):
        input_ = input("enter the file's name > ")
        index = '{:0>3}'.format(max(int(key) for key in self.toc) + 1)
        path = self.cwd / 'parts' / '{}.tex'.format(index)
        
        self.toc[index] = {'name': input_}

        import datetime
        today = datetime.date.today()
        # touch with: '\section{input_}\n\timetx{today_}
        self.touch_file(f'\\section{{{input_}}}\n\\timetx{{{today}}}\n\n', path)
        
        self._run_ex(['vim', path])

    def list_toc(self):
        print(list_dict_obj(self.toc))

    def rm_note(self):
        self.list_toc()
        input_ = input('enter enter the index > ')

        self.toc.pop(input_)
        (self.cwd / 'parts' / f'{input_}.tex').unlink()

    def run_it(self, Test=False):
        self.touch_file(self.config['cls_file_str'], self.cwd / self.file('cls'))
        self.touch_tex_file()
        print('-'*50, end='\n\n')

        self.xelatex_it()
        print('-'*50, end='\n\n')
        
        if not Test:
            self.rm_useless()

    def look_it(self):
        self._run_ex(['chrome', self.file('pdf')])


# ===============================================
# about main runner: ----------------------------
def help():
    help_doc = (
        '-------------------------------------\n'
        'help: show this\n'
        'run : run it\n'
        '?q  : quit it\n'
        'new : edit a new note\n'
        'rm  : rm a note'
    )
    print(add_indent(help_doc, 4))

if __name__ == '__main__':
    from pathlib import Path
    Test = False
    com = commander(Path.cwd())

    while True:
        input_ = input('(enter help for help)> ')
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
            else:
                print(f'no command named {input_}')
            print()
        except Exception as e:
            print(e, '\n')