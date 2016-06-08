packages = ['prooftree', 'amsmath', 'mathtools', 'syntax', 'dsfont', 'stmaryrd']

def document(body, title='', author=''):
    start = r'\documentclass{article}' + \
            ''.join([r'\usepackage{' + x + '}' for x in packages]) + \
            r'\title{' + title + r'}\author{' + author + r'}\date{\today}' + \
            r'\begin{document}\maketitle\tableofcontents '
    end = r'\end{document}'
    return start + body + end + '\n'

def wrap(start='', end=''):
    def f(*ys):
        return start + ','.join(ys) + end
    return f

mathmode = wrap('\[', '\]')
mbox = wrap(r'\mbox{', '}')
code = wrap(r'\lit*{\mbox{', '}}')
synt = wrap(r'\synt{\mbox{', r'}\thinspace}')
text = wrap(r'\textrm{\mbox{', r'}}')

def justifies(subs='', body='', rule=''):
    if isinstance(subs, str):
        subs = [subs]
    r = r'\prooftree ' + '\quad '.join(subs) + r'\justifies ' + body
    if rule != '':
        r += r'\using{' + mbox('[' + rule + ']') + '}'
    r += r'\endprooftree '
    return r

def where(body='', *wheres):
    wheres = ['&=&'.join(where.split('=', 1)) for where in wheres]
    return r'\left.\begin{array}{c}' + body + r"\\\begin{array}{crcl}"\
            r'\textrm{\textbf{where}}&' \
            + r'\\&'.join(wheres) + r'\end{array}\end{array}\right.'

def ssiss(leftstmt, leftstate, rightstmt, rightstate, star=False):
    return r'\langle ' + leftstmt + ', ' + leftstate + \
            r'\rangle\Rightarrow' + ('^*' if star else '') + (rightstate if
            rightstmt is None else r'\langle ' + \
            rightstmt + ',' + rightstate + \
            r'\rangle ')

def ssirs(s, ls, rs):
    return ssiss(s, ls, None, rs, star=True)

def ssirss(*args):
    return ssiss(*args, star=True)

def ssis(leftstmt, leftstate, rightstate):
    return r'\langle ' + leftstmt + ',' + leftstate + r'\rangle\Rightarrow ' + \
            rightstate

def evalexpr(expr, env):
    return r'\mathds{E}\llbracket ' + expr + r'\rrbracket ' + env

syntaxrules = dict()
syntaxrules_order = []
syntaxrules_rhs = set()

def syntaxrule(s):
    def processitem(item, binds, i):
        if item == 'space':
            return r'\textvisiblespace'
        if item == '...':
            return r'\dots'
        if i in binds:
            return binds[i]
        elif item[0] in '`\'"' and item[-1] in '`\'"':
            if len(item) == 2:
                return '\epsilon'
            return code(item[1:-1])
        else:
            return synt(item)
    def processseq(seq):
        seq = seq.split(' ')
        nonterms = [i for i, x in enumerate(seq)
                if x[0] not in '`\'"' or x[-1] not in '`\'"']
        for i in nonterms:
            if seq[i] not in ['...', 'space']:
                syntaxrules_rhs.add(seq[i])
        def f(*args):
            binds = dict(zip(nonterms, args))
            return r'\ '.join([processitem(item, binds, i) for i, item in
                enumerate(seq)])
        return f
    def processopt(opt):
        opt = opt.split(' | ')
        if len(opt) == 1:
            return processseq(opt[0])
        else:
            return [processseq(o) for o in opt]

    s = ' '.join(s.strip().split())
    name, rhs = s.split(' = ', 1)
    syntaxrules[name] = processopt(rhs)
    syntaxrules_order.append(name)
    return syntaxrules[name]

def makesyntax():
    def processpair(k, v):
        if not callable(v):
            return synt(k) + '&=&' + r'\ |\ '.join([f() for f in v])
        return synt(k) + '&=&' + v()
    s = r'\begin{flalign*}\begin{array}{lcl}'
    s += r'\\'.join([processpair(k, syntaxrules[k]) for k in syntaxrules_order])
    undef = [x for x in syntaxrules_rhs if x not in syntaxrules]
    s += r'\\' + r'\\'.join([synt(k) + r'&=&\textrm{TODO}' for k in undef])
    s += r'\end{array}\end{flalign*}'
    return s

def readsyntax(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    lines2 = []
    for line in lines:
        if line != line.lstrip():
            lines2[-1] += line
        else:
            lines2.append(line)
    for line in lines2:
        syntaxrule(line)

def syntax(rule, index=None):
    if index is not None:
        return syntaxrules[rule][index]
    return syntaxrules[rule]

def compilesemantics(k, v, funcs):
    k = '_'.join([textrm(x) for x in k.split('_')])
    def newjustifies(a, b):
        return r'\begin{array}{rl}[' + k + ']&' + justifies(a, b) + \
            r'\end{array}'
    funcs = funcs.copy()
    funcs['justifies'] = newjustifies
    v = convert(v, funcs)
    return mathmode(v)

semanticsrules = dict()
semanticsrules_order = []
def readsemantics(filename, funcs):
    with open(filename, 'r') as f:
        contents = f.read()
    rules = [rule.strip().split(':\n', 1) for rule
        in contents.split('\n\n') if rule.strip()]
    for k, v in rules:
        semanticsrules_order.append(k)
        semanticsrules[k] = compilesemantics(k, v, funcs)

def makesemantics():
    s = r'\\'.join([semanticsrules[k] for k in semanticsrules_order])
    return s

def convert(s, d, i=0):
    name = ''
    result = ''
    parts = ['']
    while i < len(s):
        c = s[i]
        if c == ',':
            parts.append('')
        elif c == ')':
            return i, parts
        elif c == '(':
            i, subs = convert(s, d, i + 1)
            if name != '':
                subs = d[name](*subs)
            else:
                subs = '(' + ','.join(subs) + ')'
            parts[-1] = parts[-1][:-len(name)]
            parts[-1] += subs.strip()
        else:
            parts[-1] += c
        if c.lower() <= 'z' and c.lower() >= 'a':
            name += c
        else:
            name = ''
        i += 1
    return parts[0]

textrm = wrap(r'\textrm{\mbox{', '}}')
def envf(name, count):
    wrapper = wrap(textrm(name) + '(', ')')
    def f(*args):
        if len(args) != count:
            raise TypeError("Expected " + str(count) + " args, got " +
                    str(len(args)))
        if count == 0:
            return textrm(name)
        return wrapper(*args)
    return f

readsyntax('syntax')

funcs = syntaxrules.copy()
funcs.update({
    'where': where,
    'justifies': justifies,
    'eval': evalexpr,
    'ssirss': lambda a, b, c, d: ssiss(a, b, c, d, True),
    'ssirs': lambda a, b, c: ssiss(a, b, None, c, True),
    'ssiss': lambda a, b, c, d: ssiss(a, b, c, d, False),
    'ssis': lambda a, b, c: ssiss(a, b, None, c, False),
    'get': envf('get', 2),
    'let': envf('let', 3),
    'set': envf('set', 3),
    'merge': envf('merge', 2),
    'def': envf('def', 3),
    'new': envf('new', 0),
    'ret': syntax('block', 1),
    'block': syntax('block', 0),
    'epsilon': lambda: r'\epsilon '
})

readsemantics('semantics', funcs)

syntax = '\section{Syntax}' + makesyntax()
semantics = '\section{Semantics}' + makesemantics()

doc = document(syntax + semantics, title='Semantics for Lua coroutines',
        author='Serena Rietbergen, Frank Gerlings, Lars Jellema')

with open('test.tex', 'w') as f:
    f.write(doc)
