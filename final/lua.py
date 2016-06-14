from tex import *
from sem import Sem, SS

class SemAssign(Sem):
    def bottom_right(self, bottom_left):
        v, e = bottom_left.stmt.fields
        s = bottom_left.state
        return s.let(v, s.evalexpr(e))

class SemComp(Sem):
    def tops_left(self, bottom_left):
        return [SS(bottom_left.stmt.fields[0], bottom_left.state)]

    def bottom_right(self, bottom_left, top_right):
        if isinstance(top_right, State):
            return SS(bottom_left.stmt.fields[1], top_right)
        else:
            return SS(AppliedSyntax('block', top_right.stmt,
                bottom_left.stmt.fields[1]), top_right.state)

class SemEmpty(Sem):
    def bottom_right(self, bottom_left):
        return bottom_left.state

class SemIf(Sem):
    def bottom_right(self, bottom_left):
        cond, ift, iff = bottom_left.stmt.fields
        s = bottom_left.state
        if s.evalexpr(cond) == true:
            return SS(ift, s)
        else:
            return SS(iff, s)

class SemResume(Sem):
    def tops_left(self, bottom_left):
        r, c, a = bottom_left.stmt.fields
        s = bottom_left.state
        co = s.get(c)
        return [SS(co.block, s.merge(co.state).let(co.var, s.evalexpr(a)))]

    def bottom_right(self, bottom_left, top_right):
        r, c, a = bottom_left.stmt.fields
        s = bottom_left.state
        if isinstance(top_right, State):
            sp = top_right
            res = nil
            newco = nil
        else:
            sp = top_right.state
            if top_right.stmt.name == 'block':
                rp, ap = top_right.stmt.fields[0].fields
                b = top_right.stmt.fields[1].fields[1]
                newco = Co(sp, rp, b)
            elif top_right.stmt.name == 'return':
                ap = top_right.stmt.fields[0]
                newco = nil
            res = sp.evalexpr(ap)
        return s.merge(sp).set(c, newco).let(r, res)

rules = {
    'block': {
        0: SemComp(),
        2: SemEmpty(),
    },
    'assign': SemAssign(),
    'if': SemIf(),
    'resume': SemResume(),
}

with open('document', 'r') as f:
    body = f.read()

doc = document(body, title='Semantics for Lua coroutines',
        author='Serena Rietbergen, Frank Gerlings, Lars Jellema')
