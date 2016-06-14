packages = ['prooftree', 'amsmath', 'mathtools', 'syntax', 'dsfont', 'stmaryrd',
        'listings', 'amsfonts']

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

def justifies(subs='', body=''):
    if isinstance(subs, str):
        subs = [subs]
    return r'\prooftree ' + '\quad '.join(subs) + r'\justifies ' + body + \
            r'\endprooftree '

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

def evalexpr(expr, env):
    return r'\mathds{E}\llbracket ' + expr + r'\rrbracket ' + env

def casesf(*cases):
    s = r'\begin{cases}'
    while len(cases) > 1:
        case, cond, cases = cases[0], cases[1], cases[2:]
        s += case + '&' + cond + r'\\'
    if len(cases) > 0:
        s += cases[0] + r'&\\'
    s = s[:-2] + r'\end{cases}'
    return s

def mathfn(var, *cases):
    s = var + r'\mapsto'
    if len(cases) == 1:
        s += cases[0]
        return s
    return s + casesf(*cases)

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

syntax = None

def syntax(rule=None, index=None):
    if rule is None:
        return makesyntax()
    if index is not None:
        return syntaxrules[rule][index]
    return syntaxrules[rule]

def compilesemantics(k, v, funcs):
    k = '_'.join([textrm(x) for x in k.split('_')])
    used = [False]
    def newwhere(body, *wheres):
        used[0] = True
        return where('[' + k + ']\quad ' + body, *wheres)
    funcs = funcs.copy()
    funcs['where'] = newwhere
    v = convert(v, funcs)
    if not used[0]:
        v = '[' + k + ']\quad ' + v
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
        semanticsrules[k] = compilesemantics(k, v.replace('\n', ''), funcs)

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
            if parts[0] == '' and len(parts) == 1:
                return i, ()
            return i, parts
        elif c == '(':
            if name == 'noscript':
                i, subs = convert(s, dict(), i + 1)
            else:
                i, subs = convert(s, d, i + 1)
            if name != '' and name not in d:
                print('####### Function not found: ' + name)
            if name in d:
                subs = d[name](*subs)
            elif name == 'noscript':
                subs = ','.join(subs)
            else:
                subs = name + '(' + ','.join(subs) + ')'
            if name != '':
                parts[-1] = parts[-1][:-len(name)]
            parts[-1] += subs.strip()
        else:
            parts[-1] += c
        if c.lower() <= 'z' and c.lower() >= 'a':
            name += c
        else:
            name = ''
        i += 1
    return ','.join(parts)

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

def linepass(text):
    lines = text.split('\n')
    lines2 = []
    for line in lines:
        if line.startswith('###'):
            lines2.append(r'\subsubsection{' + line[3:].strip() + '}')
        elif line.startswith('##'):
            lines2.append(r'\subsection{' + line[2:].strip() + '}')
        elif line.startswith('#'):
            lines2.append(r'\section{' + line[1:].strip() + '}')
        elif line.startswith('%'):
            lines2.append('')
        else:
            lines2.append(line)
    return '\n'.join(lines2)

def readdocument(filename, funcs):
    with open(filename, 'r') as f:
        contents = f.read()
    contents = linepass(contents)
    contents = convert(contents, funcs)
    contents = document(contents, title='Semantics for Lua coroutines',
            author='Serena Rietbergen, Frank Gerlings, Lars Jellema')
    return contents

def importfile(filename):
    with open(filename, 'r') as f:
        return f.read()

def semantics(x):
    return semanticsrules[x]

readsyntax('syntax')

funcs = syntaxrules.copy()
funcs.update({
    'where': where,
    'justifies': justifies,
    'eval': evalexpr,
    'import': importfile,
    'semantics': lambda x: semanticsrules[x],
    'syntax': syntax,
    'fn': mathfn,
    'n': text,
    'cases': casesf,
    'when': lambda a, b: a + '\quad [' + b + ']',
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
    'false': syntax('bool', 0),
    'true': syntax('bool', 1),
    'empty': lambda: r'\epsilon '
})

readsemantics('semantics', funcs)

doc = readdocument('document', funcs)

with open('test.tex', 'w') as f:
    f.write(doc)
