from sem import Sem, SS
from tex import *
import lua_syn as syn

import collections

true = syn.Bool(True)
false = syn.Bool(False)
nil = syn.Nil()

class Mapping(Mex):
    def __init__(self, mappings=collections.OrderedDict(), parent=None):
        self.mappings = mappings
        self.parent = parent

    def set(self, var, val):
        d = self.mappings.copy()
        d[var] = val
        return Mapping(d, self.parent)

    def get(self, var):
        if var in self.mappings:
            return self.mappings[var]
        else:
            return nil

    def gentex(self):
        if len(self.mappings) == 0 and self.parent is not None:
            return mex(self.parent)
        s = r'\langle '
        mappings = (mex(k) + r'\mapsto ' + mex(v)
                for k, v in self.mappings.items())
        s += ', '.join(mappings)
        if self.parent:
            s += ', ' + mex(self.parent)
        s += r'\rangle '
        return s


class Ref(Mex):
    def __init__(self, n):
        self.n = n
        self.x = str(n)

    def gentex(self):
        return r'\textrm{ref}_{' + self.x + r'}'


ref0 = Ref(0)
nilmapping = Mapping()

class Function(Mex):
    def __init__(self, state, var, block):
        self.state = state
        self.var = var
        self.block = block

    def gentex(self):
        return Mex.tuple(self.state, self.var, self.block) + r'_{\textrm{fn}}'


class State(Mex):
    def __init__(self, locs=nilmapping, globs=nilmapping, nxtref=ref0):
        self.locs = locs
        self.globs = globs
        self.nxtref = nxtref

    def gentex(self):
        return Tex.tuple(self.locs, self.globs, self.nxtref)

    def let(self, var, val):
        return State(self.locs.set(var, val), self.globs, self.nxtref)

    def set(self, var, val):
        return State(self.locs, self.globs.set(self.locs.get(var), val),
                self.nxtref)

    def get(self, var):
        return self.locs.get(var)

    def coget(self, var):
        return self.globs.get(self.locs.get(var))

    def merge(self, other):
        return State(self.locs, other.globs, Ref(max(self.nxtref.n,
            other.nxtref.n)))

    def def_(self, var, val):
        return State(self.locs.set(var, self.nxtref),
                self.globs.set(self.nxtref, val), Ref(self.nxtref.n + 1))

    def evalexpr(self, e):
        if isinstance(e, syn.Var):
            return self.get(e)
        elif isinstance(e, syn.UnOp):
            if e.op == '-':
                return syn.Number(-self.evalexpr(e.arg).value)
            elif e.op == 'not':
                return syn.Bool(not self.evalexpr(e.arg).value)
        elif isinstance(e, syn.BinOp):
            if e.op == '*':
                return syn.Number(self.evalexpr(e.left).value *
                        self.evalexpr(e.right).value)
            if e.op == '+':
                return syn.Number(self.evalexpr(e.left).value +
                        self.evalexpr(e.right).value)
        elif isinstance(e, syn.Const):
            return e
        elif isinstance(e, syn.Parens):
            return self.evalexpr(e.arg)
        elif isinstance(e, syn.Lambda):
            return Function(self, e.arg, e.block)
        else:
            raise Exception('No evalexpr for ' + repr(e))


class Coroutine(Mex):
    def __init__(self, state, var, block):
        self.state = state
        self.var = var
        self.block = block

    def gentex(self):
        return Mex.tuple(self.state, self.var, self.block) + r'_{\textrm{co}}'


class SemAssign(Sem):
    def bottom_right(self, bottom_left):
        s = bottom_left.state
        return s.let(bottom_left.stmt.var, s.evalexpr(bottom_left.stmt.val))

class SemComp(Sem):
    def tops_left(self, bottom_left):
        return [SS(bottom_left.stmt.stmt, bottom_left.state)]

    def bottom_right(self, bottom_left, top_right):
        if isinstance(top_right, State):
            return SS(bottom_left.stmt.block, top_right)
        else:
            return SS(syn.Block.merge(top_right.stmt, bottom_left.stmt.block),
                    top_right.state)

class SemEmpty(Sem):
    def bottom_right(self, bottom_left):
        return bottom_left.state

class SemIf(Sem):
    def bottom_right(self, bottom_left):
        s = bottom_left.state
        r = s.evalexpr(bottom_left.stmt.cond).value
        if r is True:
            return SS(bottom_left.stmt.ift, s)
        elif r is False:
            return SS(bottom_left.stmt.iff, s)
        else:
            raise Exception('If expected pointer, got: ' + repr(r))

class SemWrap(Sem):
    def bottom_right(self, bottom_left):
        s = bottom_left.state
        f = s.evalexpr(bottom_left.stmt.arg)
        return s.def_(bottom_left.stmt.var, Coroutine(f.state, f.var, f.block))

class SemResume(Sem):
    def tops_left(self, bottom_left):
        so = bottom_left.state
        rsm = bottom_left.stmt.stmt
        ro, c, ao = rsm.var, rsm.fn, rsm.arg
        co = so.coget(c)
        si, ri, bi = co.state, co.var, co.block
        return [SS(bi, si.merge(so.set(c, nil)).let(ri, so.evalexpr(ao)))]

    def bottom_right(self, bottom_left, top_right):
        so = bottom_left.state
        rsm = bottom_left.stmt.stmt
        blk = bottom_left.stmt.block
        ro, c, ao = rsm.var, rsm.fn, rsm.arg
        co = so.coget(c)
        si, ri, bi = co.state, co.var, co.block
        if isinstance(top_right, State):
            return SS(blk, so.set(c, nil).merge(top_right).let(ro, nil))
        elif isinstance(top_right.stmt, syn.Return):
            sip = top_right.state
            ai = top_right.stmt.arg
            return SS(blk, so.set(c, nil).merge(sip).let(ro, sip.evalexpr(ai)))
        elif isinstance(top_right.stmt, syn.Block) and \
                isinstance(top_right.stmt.stmt, syn.Yield):
            sip = top_right.state
            bip = top_right.stmt.block
            rip = top_right.stmt.stmt.var
            ai = top_right.stmt.stmt.arg
            return SS(blk, so.merge(sip).set(c, Coroutine(sip, rip, bip))
                    .let(ro, sip.evalexpr(ai)))
        raise Exception('No match')

class SemWhile(Sem):
    def bottom_right(self, bottom_left):
        s = bottom_left.state
        cond = bottom_left.stmt.cond
        block = bottom_left.stmt.block
        return SS(syn.If(cond, syn.Block.merge(block,
            syn.Block(bottom_left.stmt, syn.Empty())), syn.Empty()), s)

class SemCall(Sem):
    def tops_left(self, bottom_left):
        s = bottom_left.state
        if isinstance(s.evalexpr(bottom_left.stmt.fn), Ref):
            return SemResume().tops_left(bottom_left)
        return [top_left]
    
    def bottom_right(self, bottom_left, top_right):
        s = bottom_left.state
        if isinstance(s.evalexpr(bottom_left.stmt.fn), Ref):
            return SemResume().bottom_right(bottom_left, top_right)

rules = {
    'block': SemComp(),
    'empty': SemEmpty(),
    'assign': SemAssign(),
    'if': SemIf(),
    'resume': SemResume(),
    'wrap': SemWrap(),
    'call': SemCall(),
    'while': SemWhile(),
}

class Chain(Mex):
    def __init__(self, items, arrows):
        self.items = items
        self.arrows = arrows

    def gentex(self):
        s = r'\begin{array}{c}' + mex(self.items[0])
        for arrow, item in zip(self.arrows, self.items[1:]):
            s += r'\stackrel{' + arrow + r'}{\Rightarrow}\\' + mex(item)
        s += r'\end{array}'
        return s

class Justifies(Mex):
    def __init__(self, top, bottom):
        self.top = top
        self.bottom = bottom

    def gentex(self):
        return r'\begin{array}{c}' + mex(self.top) + r' \\ \hline' + \
                mex(self.bottom) + r'\end{array}'

class Analysis(Tex):
    def __init__(self, code):
        self.code = code
        self.figures = []

    def get_sem(self, bottom_left):
        if isinstance(bottom_left, State):
            return
        if isinstance(bottom_left.stmt, syn.Block) and \
                isinstance(bottom_left.stmt.stmt, syn.Yield):
            return
        if isinstance(bottom_left.stmt, syn.Block) and \
                isinstance(bottom_left.stmt.stmt, syn.Call):
            return rules['resume']
        #if isinstance(bottom_left, Return):
        #    return
        try:
            rulename = bottom_left.stmt.rulename
            if rulename in rules:
                return rules[rulename]
        except Exception:
            pass
        print("Couldn't find rule for: " + repr(bottom_left.stmt))
        return None

    def step(self, bottom_left):
        '''
        returns:
            index of the produced figure
        '''
        chain = [bottom_left]
        arrows = []
        sem = self.get_sem(bottom_left)
        while sem is not None:
            arrows.append([])
            tops_left = sem.tops_left(bottom_left)
            tops_right = []
            for top_left in tops_left:
                tops_right.append(self.step(top_left))
                arrows[-1].append(str(len(self.figures)))
            bottom_left = sem.bottom_right(bottom_left, *tops_right)
            chain.append(bottom_left)
            sem = self.get_sem(bottom_left)
        if len(arrows) == 1 and len(arrows[0]) > 0:
            top = self.figures[-1]
            self.figures = self.figures[:-1]
            self.figures.append(Justifies(top, Chain(chain, [''])))
        else:
            self.figures.append(Chain(chain, [','.join(x) for x in arrows]))
        return chain[-1]

    def gentex(self):
        l = []
        for i, fig in enumerate(self.figures):
            l.append(r'\lbrack ' + str(i + 1) + r'\rbrack ' + mex(fig) + '')
        return r'\(\begin{array}{c}' + r'\\\\'.join(l) + r'\end{array}\)'


