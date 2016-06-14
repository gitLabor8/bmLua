def tex(x):
    if x.ismath():
        return r'\(' + x.gentex() + r'\)'
    return x.gentex()

def mex(x):
    if not x.ismath():
        return r'\textrm{' + x.gentex() + '}'
    return x.gentex()

class Tex:
    def __init__(self, x):
        self.x = x

    def __str__(self):
        return self.gentex()

    def __repr__(self):
        return 'Tex(' + repr(self.gentex()) + ')'

    def ismath(self):
        return False

    def gentex(self):
        return self.x

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.x == other.x

    def __hash__(self, other):
        return hash(self.x)

    @staticmethod
    def tuple(*args):
        return '(' + ', '.join((mex(arg) for arg in args)) + ')'


class Mex(Tex):
    def ismath(self):
        return True


class Code(Mex):
    def __init__(self, x):
        self.x = x

    def gentex(self):
        return r'\lit*{' + self.x + '}'



