def add_indent(string, indent_int):
    indent = indent_int * ' '
    return indent + f"\n{indent}".join(string.split('\n'))

import datetime
def long_time():
    """ from year to microsenced """
    return str(datetime.datetime.now())

def short_time():
    """ from year to day """
    return str(datetime.date.today())

def sha1_string(string):
    import hashlib
    hashed_string = string.encode('utf-8')
    return hashlib.sha1(hashed_string).hexdigest()