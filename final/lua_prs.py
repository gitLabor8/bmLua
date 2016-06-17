from prs import *

def flatten(l):
    if not isinstance(l, list):
        return l
    r = []
    for x in l:
        r.extend(flatten(x))
    return r

keywords = [
    'function',
    'while',
    'end',
    'if',
    'else',
    'then',
    'coroutine',
    'true',
    'false',
    'nil',
]

parsermap = {
    'nil': Lit('nil'),
    'bool': Opt(Lit('true'), Lit('false')),
    'digit': Range('0', '9'),
    'number': List('digit', minc=1),
    'letter': Opt(Range('a', 'z'), Range('A', 'Z'), Lit('_')),
    'var': ButNot(Seq('letter', List(Opt('letter', 'digit')), ws=False), *keywords),
    'add': Seq('tmp', Lit('+'), 'expr'),
    'sub': Seq('tmp', Lit('-'), 'expr'),
    'mul': Seq('tmp', Lit('*'), 'expr'),
    'and': Seq('tmp', Lit('and'), 'expr'),
    'or': Seq('tmp', Lit('or'), 'expr'),
    'neg': Seq(Lit('-'), 'expr'),
    'not': Seq(Lit('not'), 'expr'),
    'parens': Seq(Lit('('), 'expr', Lit(')')),
    'lambda': Seq(Lit('function'), Lit('('), 'var', Lit(')'), 'block',
        Lit('end')),
    'nexpr': Opt('add', 'sub', 'mul', 'neg'),
    'bexpr': Opt('and', 'or', 'not'),
    'const': Opt('nil', 'bool', 'number'),
    'expr': Opt('nexpr', 'bexpr', 'parens', 'lambda', 'var', 'const'),
    'block': Opt(Seq('stmt', 'block'), Seq(Lit('return'), 'expr'), Lit('')),
    'tmp': Opt('neg', 'not', 'parens', 'lambda', 'const', 'var'),
    'assign': Seq('var', Lit('='), 'expr'),
    'if': Seq(Lit('if'), 'expr', Lit('then'), 'block', Lit('else'), 'block',
        Lit('end')),
    'while': Seq(Lit('while'), 'expr', Lit('do'), 'block', Lit('end')),
    'cowrap': Seq('var', Lit('='), Lit('coroutine.wrap'), Lit('('), 'expr',
        Lit(')')),
    'coyield': Seq('var', Lit('='), Lit('coroutine.yield'), Lit('('), 'expr',
        Lit(')')),
    'call': Seq('var', Lit('='), 'var', Lit('('), 'expr', Lit(')')),
    'stmt': Opt('if', 'while', 'call', 'assign', 'coyield', 'cowrap'),
}

handlermap = {
    'var': lambda l: ''.join(flatten(l)),
    'number': lambda l: int(''.join(l)),
    'bool': lambda b: b == 'true',
    'nil': lambda _: None,
}

parser = Syntax(parsermap, 'block', handlermap)
