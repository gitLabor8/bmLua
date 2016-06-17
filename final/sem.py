from tex import *

class SS(Mex):
    def __init__(self, stmt, state):
        self.stmt = stmt
        self.state = state

    def gentex(self):
        stmt = mex(self.stmt)
        if stmt.strip() == '':
            stmt = r'\epsilon '
        return r'\langle ' + stmt + ', ' + mex(self.state) + r'\rangle'

class Sem(Mex):
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
