def add_indent(string, indent_int):
    indent = indent_int * ' '
    return indent + f"\n{indent}".join(string.split('\n'))