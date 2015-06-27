class MalformedInput(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message

def parse_file(f):
    word_defs = []
    for entry in f.read().strip().split('\n'):
        word_def = entry.split('\t')
        if len(word_def) < 2:
            raise MalformedInput('Entry format must be [Word] [Definition].')
        word_defs.append((str(word_def[0]), str(word_def[1])))
    return word_defs
