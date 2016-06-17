packages = ['amsmath', 'mathtools', 'dsfont', 'stmaryrd', 'listings',
        'amsfonts', 'syntax', 'standalone']

def where(body='', *wheres):
    wheres = ['&=&'.join(where.split('=', 1)) for where in wheres]
    return r'\begin{array}{c}' + body + r"\\\begin{array}{crcl}"\
            r'\textrm{\textbf{where}}&' \
            + r'\\&'.join(wheres) + r'\end{array}\end{array}'

def document(body):
    header = r'\documentclass{article}'
    header += ''.join((r'\usepackage{' + x + '}' for x in packages))
    return header + r'\begin{document}' + body + r'\end{document}' + '\n'

def tex(x):
    if x.ismath():
        return r'\(' + x.gentex() + r'\)'
    return x.gentex()

def mex(x):
    if not x.ismath():
        return r'\textrm{' + x.gentex() + '}'
    return x.gentex()

class Tex:
    def __init__(self, x=None):
        self.x = x

    def __str__(self):
        return self.gentex()

    def __repr__(self):
        return type(self).__name__ + '(' + repr(self.gentex()) + ')'

    def ismath(self):
        return False

    def gentex(self):
        return self.x

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.x == other.x

    def __hash__(self):
        return hash(self.x)

    @staticmethod
    def tuple(*args):
        return '(' + ', '.join((mex(arg) for arg in args)) + ')'

    @staticmethod
    def seq(*args):
        def fix(x):
            try:
                return mex(x)
            except:
                return mex(Code(x))
        return r'\ '.join((fix(arg) for arg in args))


class Mex(Tex):
    def ismath(self):
        return True


class Code(Mex):
    def __init__(self, x):
        self.x = x

    def gentex(self):
        return r'\lit*{' + self.x + '}'



