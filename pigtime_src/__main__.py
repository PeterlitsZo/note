from .command import commander
from .printlib import add_indent

def help():
    help_doc = (
        '+------------------------------------\n'
        '| edit the book:\n'
        '|     init: init a root book\n'
        '|     new : edit a new note\n'
        '|     rm  : rm a note\n'
        '|     edit: edit a note\n|\n'
        '| show around:\n'
        '|     run : run it\n'
        '|     list: list the note\n'
        '|     look: look the pdf file\n|\n'
        '| others:\n'
        '|     help: show this\n'
        '|     ?q  : quit it\n'
        '+-------------------------------------'
    )
    print(add_indent(help_doc, 4))

def main():
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
            elif input_ == 'rm':
                com.rm_note()
            elif input_ == 'look':
                com.look_it()
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