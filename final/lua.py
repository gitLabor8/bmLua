from tex import *
from sem import Sem, SS
from lua_prs import parser

def flatten(l):
    if not isinstance(l, list):
        return l
    r = []
    for x in l:
        r.extend(flatten(x))
    return r

class BinOp(Mex):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def gentex(self):
        return mex(self.left) + mex(Code(self.op)) + mex(self.right)

class UnOp(Mex):
    def __init__(self, op, arg):
        self.op = op
        self.arg = arg

    def gentex(self):
        return mex(Code(self.op)) + mex(self.arg)

class Block(Mex):
    def __init__(self, stmt, block):
        self.stmt = stmt
        self.block = block

    def gentex(self):
        return mex(self.stmt) + mex(self.block)

class Assign(Mex):
    def __init__(self, var, val):
        self.var = var
        self.val = val

    def gentex(self):
        return mex(self.var) + mex(Code('=')) + mex(self.val)

class If(Mex):
    def __init__(self, cond, ift, iff):
        self.cond = cond
        self.ift = ift
        self.iff = iff

    def gentex(self):
        return mex(Code('if')) + mex(self.cond) + mex(Code('then')) + \
                mex(self.ift) + mex(Code('else')) + mex(self.iff) + \
                mex(Code('end'))

class Parens(Mex):
    def __init__(self, arg):
        self.arg = arg

    def gentex(self):
        return '(' + mex(self.arg) + ')'

class Var(Mex):
    def __init__(self, name):
        self.name = name
        self.x = name

    def gentex(self):
        return mex(Code(self.name))

class Const(Mex):
    pass

class Nil(Const):
    def __init__(self):
        self.value = None

    def gentex(self):
        return mex(Code('nil'))

class Bool(Const):
    def __init__(self, value):
        self.value = value
    
    def gentex(self):
        return mex(Code('true' if self.value else 'false'))

class Number(Const):
    def __init__(self, text):
        self.value = int(text)
        self.text = text

    def gentex(self):
        return mex(Code(text))

class Call(Mex):
    def __init__(self, var, fn, arg):
        self.var = var
        self.fn = fn
        self.arg = arg

    def gentex(self):
        return mex(self.var) + mex(Code('=')) + mex(self.fn) + mex(Code('(')) \
                + mex(self.arg) + mex(Code(')'))

class Yield(Mex):
    def __init__(self, var, arg):
        self.var = var
        self.arg = arg

    def gentex(self):
        return mex(self.var) + mex(Code('=')) + mex(Code('coroutine.yield')) + \
                mex(Code('(')) + mex(self.arg) + mex(Code(')'))

class Wrap(Mex):
    def __init__(self, var, arg):
        self.var = var
        self.arg = arg

    def gentex(self):
        return mex(self.var) + mex(Code('=')) + mex(Code('coroutine.wrap')) + \
                mex(Code('(')) + mex(self.arg) + mex(Code(')'))

class While(Mex):
    def __init__(self, cond, block):
        self.cond = cond
        self.block = block

    def gentex(self):
        return mex(Code('while')) + mex(self.cond) + mex(Code('do')) + \
                mex(self.block) + mex(Code('end'))

class Lambda(Mex):
    def __init__(self, arg, block):
        self.arg = arg
        self.block = block

    def gentex(self):
        return mex(Code('function')) + mex(Code('(')) + mex(self.arg) + \
                mex(Code(')')) + mex(self.block) + mex(Code('end'))

binop = lambda x: BinOp(x[1], x[0], x[2])
unop = lambda x: UnOp(x[0], x[1])

emptyblock = Tex('')

def mkvar(x):
    if isinstance(x, list):
        return Var(x[0] + x[1].name)
    else:
        return Var(x)

def mkblock(x):
    if isinstance(x, list):
        if x[0] == 'return':
            return x
        return Block(x[0], x[1])
    else:
        return emptyblock

handlermap = {
    'var': mkvar,
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

with open('code.lua', 'r') as f:
    code = f.read()

x = parser.parse(code, 'block', handlermap)

print(repr(x))

with open('document', 'r') as f:
    body = f.read()

#doc = document(body, title='Semantics for Lua coroutines',
#        author='Serena Rietbergen, Frank Gerlings, Lars Jellema')
