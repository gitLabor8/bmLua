from tex import *

nil = Code('nil')
true = Code('true')
false = Code('false')

class Mapping(MathTex):
    def __init__(self, mappings=dict(), parent=None):
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
            return tex(self.parent)
        s = r'\langle '
        mappings = (tex(k) + r'\mapsto ' + tex(v)
                for k, v in self.mappings.items())
        s += ', '.join(mappings)
        if self.parent:
            s += ', ' + tex(self.parent)
        s += r'\rangle '
        return s

class Ref(MathTex):
    def __init__(self, n):
        self.n = n
        self.x = str(n)

    def gentex(self):
        return r'\textrm{ref}_{' + self.x + r'}'

ref0 = Ref(0)
nilmapping = Mapping()

class State(MathTex):
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
        v = self.locs.get(var)
        if isinstance(v, Ref):
            return self.globs.get(v)
        else:
            return v

    def merge(self, other):
        return State(self.locs, other.globs, Ref(max(self.nxtref.n,
            other.nxtref.n)))

    def def_(self, var, val):
        return State(self.locs.set(var, self.nxtref),
                self.globs.set(self.nxtref, val), Ref(self.nxtref.n + 1))

    def evalexpr(self, e):
        pass

class SS(MathTex):
    def __init__(self, stmt, state):
        self.stmt = stmt
        self.state = state

    def gentex(self):
        return r'\langle ' + self.tex(self.stmt) + ', ' + \
                self.tex(self.state) + r'\rangle'

class Sem(MathTex):
    def tops_left(self, bottom_left):
        return []

class Justifies(Tex):
    def __init__(self, x, *tops_right_m):
        self.bottom_left = x
        rule = rules[x.stmt.name]
        if isinstance(rule, dict):
            rule = rule[x.stmt.num]
        self.tops_left = rule.tops_left(x)
        self.trees = []
        self.tops_right = []
        for top_left in self.tops_left:
            try:
                tree = Justifies(top_left, *tops_right_m)
                tops_right_m = tree.tops_right_m
                top_right = tree.bottom_right
            except Exception:
                tree = MathLit(top_left + r'\Rightarrow *' + tops_right_m[0])
                top_right = tops_right_m[0]
                tops_right_m = tops_right_m[1:]
            self.tops_right.append(top_right)
            self.trees.append(tree)
        self.tops_right_m = tops_right_m
        self.bottom_right = rule.bottom_right(x, *self.tops_right)

    def gentex(self):
        bottom = self.tex(self.bottom_left) + r'\Rightarrow' + \
                self.tex(self.bottom_right)
        top = r'\quad'.join((self.tex(tree) for tree in self.trees))
        return r'\begin{array}{c}' + top + r'\hline ' + bottom + r'\end{array}'
