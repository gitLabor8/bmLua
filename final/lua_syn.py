from tex import *
from lua_prs import parsermap

import prs

def flatten(l):
    if not isinstance(l, list):
        return l
    r = []
    for x in l:
        r.extend(flatten(x))
    return r

class Syn(Mex):
    def __repr__(self):
        return self.__class__.__name__ + repr(self.fields)

class BinOp(Syn):
    def __init__(self, op, left, right):
        self.fields = (op, left, right)
        self.op = op
        self.left = left
        self.right = right

    def gentex(self):
        return Mex.seq(self.left, self.op, self.right)

class UnOp(Syn):
    def __init__(self, op, arg):
        self.fields = (op, arg)
        self.op = op
        self.arg = arg

    def gentex(self):
        return Mex.seq(self.op, self.arg)

class Empty(Syn):
    def __init__(self):
        self.fields = ()
        self.rulename = 'empty'

    def gentex(self):
        return ''

class Return(Syn):
    def __init__(self, arg):
        self.fields = (arg,)
        self.rulename = 'return'
        self.arg = arg

    def gentex(self):
        return Mex.seq('return', self.arg)

class Block(Syn):
    def __init__(self, stmt, block):
        assert not isinstance(stmt, Block)
        assert isinstance(block, (Block, Empty, Return)) 
        
        self.fields = (stmt, block)
        self.rulename = 'block'
        self.stmt = stmt
        self.block = block

    @staticmethod
    def merge(b1, b2, p=True):
        if isinstance(b1, Empty):
            r = b2
        elif isinstance(b1, Return):
            r = b1
        elif isinstance(b1, Block):
            r = Block(b1.stmt, Block.merge(b1.block, b2, False))
        return r
        raise Exception('No match')

    def gentex(self):
        return Mex.seq(self.stmt, self.block)

class Assign(Syn):
    def __init__(self, var, val):
        self.fields = (var, val)
        self.rulename = 'assign'
        self.var = var
        self.val = val

    def gentex(self):
        return Mex.seq(self.var, '=', self.val)

class If(Syn):
    def __init__(self, cond, ift, iff):
        self.fields = (cond, ift, iff)
        self.rulename = 'if'
        self.cond = cond
        self.ift = ift
        self.iff = iff

    def gentex(self):
        return Mex.seq('if', self.cond, 'then', self.ift, 'else', self.iff, \
                'end')

class Parens(Syn):
    def __init__(self, arg):
        self.fields = (arg,)
        self.arg = arg

    def gentex(self):
        return '(' + mex(self.arg) + ')'

class Var(Syn):
    def __init__(self, name):
        self.fields = (name,)
        self.name = name
        self.x = name

    def gentex(self):
        return mex(Code(self.name))

class Const(Syn):
    pass

class Nil(Const):
    def __init__(self):
        self.fields = ()
        self.value = None
        self.x = None

    def gentex(self):
        return mex(Code('nil'))

class Bool(Const):
    def __init__(self, value):
        self.fields = (value,)
        self.value = value
    
    def gentex(self):
        return mex(Code('true' if self.value else 'false'))

class Number(Const):
    def __init__(self, text):
        self.fields = (text,)
        self.value = int(text)
        self.text = str(text)

    def gentex(self):
        return mex(Code(self.text))

class Call(Syn):
    def __init__(self, var, fn, arg):
        self.fields = (var, fn, arg)
        self.rulename = 'call'
        self.var = var
        self.fn = fn
        self.arg = arg

    def gentex(self):
        return Mex.seq(self.var, '=', self.fn, '(', self.arg, ')')

class Yield(Syn):
    def __init__(self, var, arg):
        self.fields = (var, arg)
        self.rulename = 'yield'
        self.var = var
        self.arg = arg

    def gentex(self):
        return Mex.seq(self.var, '=', 'coroutine.yield', '(', self.arg, ')')

class Wrap(Syn):
    def __init__(self, var, arg):
        self.fields = (var, arg)
        self.rulename = 'wrap'
        self.var = var
        self.arg = arg

    def gentex(self):
        return Mex.seq(self.var, '=', 'coroutine.wrap', '(', self.arg, ')')

class While(Syn):
    def __init__(self, cond, block):
        self.fields = (cond, block)
        self.rulename = 'while'
        self.cond = cond
        self.block = block

    def gentex(self):
        return Mex.seq('while', self.cond, 'do', self.block, 'end')

class Lambda(Syn):
    def __init__(self, arg, block):
        self.fields = (arg, block)
        self.rulename = 'lambda'
        self.arg = arg
        self.block = block

    def gentex(self):
        return Mex.seq('function', '(', self.arg, ')', self.block, 'end')

binop = lambda x: BinOp(x[1], x[0], x[2])
unop = lambda x: UnOp(x[0], x[1])

emptyblock = Empty()

def mkvar(x):
    if isinstance(x, list):
        return Var(x[0] + x[1].name)
    else:
        return Var(x)

def mkblock(x):
    if isinstance(x, list):
        if x[0] == 'return':
            return Return(x)
        return Block(x[0], x[1])
    else:
        return emptyblock

handlermap = {
    'var': lambda l: Var(l[0] + ''.join(l[1])),
    'number': lambda l: Number(''.join(l)),
    'bool': lambda b: Bool(b == 'true'),
    'nil': lambda _: Nil(),
    'add': binop,
    'sub': binop,
    'mul': binop,
    'and': binop,
    'or': binop,
    'not': unop,
    'neg': unop,
    'parens': lambda l: Parens(l[1]),
    'if': lambda l: If(l[1], l[3], l[5]),
    'assign': lambda l: Assign(l[0], l[2]),
    'block': mkblock,
    'call': lambda l: Call(l[0], l[2], l[4]),
    'coyield': lambda l: Yield(l[0], l[4]),
    'while': lambda l: While(l[1], l[3]),
    'lambda': lambda l: Lambda(l[2], l[4]),
    'cowrap': lambda l: Wrap(l[0], l[4]),
}

parser = prs.Syntax(parsermap, 'block', handlermap)
