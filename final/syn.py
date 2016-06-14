from tex import *

class NonTerminal(Mex):
    def __init__(self, x):
        self.x = x

    def gentex(self):
        return r'\synt{' + self.x + r'\thinspace}'

class Sequence(Mex):
    def __init__(self, items):
        self.items = items

    def apply(self, args):
        return AppliedSyntax(self, args)

    def gentex(self):
        return r'\ '.join((mex(item) for item in self.items))

class AppliedSyntax(Mex):
    def __init__(self, seq, args):
        self.seq = seq
        self.args = args

    def gentex(self):
        l = []
        for x in self.seq.items:
            if isinstance(x, NonTerminal):
                l.append(self.args.pop(0))
            else:
                l.append(x)
        return r'\ '.join((mex(x) for x in l))
