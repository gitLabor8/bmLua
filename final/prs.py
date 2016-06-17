def idf(x):
    return x

class ParseException(Exception):
    def __init__(self, x):
        self.x = x

    def __str__(self):
        return self.x

    def __repr__(self):
        return 'ParseException(' + self.x + ')'


class Parser:
    def parse(self, s):
        pass


class Lit(Parser):
    def __init__(self, literal):
        self.literal = literal

    def parse(self, s, syntax):
        if s.startswith(self.literal):
            return (self.literal, s[len(self.literal):])
        else:
            raise ParseException(s)


class Seq(Parser):
    def __init__(self, *parsers, ws=True):
        self.parsers = parsers
        self.ws = ws

    def parse(self, s, syntax):
        xs = []
        if self.ws: s = s.strip()
        for p in self.parsers:
            x, s = syntax.parse(s, p)
            if self.ws: s = s.strip()
            xs.append(x)
        return (xs, s)


class Opt(Parser):
    def __init__(self, *parsers):
        self.parsers = parsers

    def parse(self, s, syntax):
        for p in self.parsers:
            try:
                return syntax.parse(s, p)
            except ParseException:
                pass
        raise ParseException(s)


class List(Parser):
    def __init__(self, element, minc=0):
        self.element = element
        self.minc = minc

    def parse(self, s, syntax):
        xs = []
        while True:
            try:
                x, s = syntax.parse(s, self.element)
                xs.append(x)
            except ParseException:
                break
        if len(xs) < self.minc:
            raise ParseException(s)
        return (xs, s)


class Range(Parser):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def parse(self, s, syntax):
        if len(s) > 0 and s[0] >= self.start and s[0] <= self.end:
            return (s[0], s[1:])
        else:
            raise ParseException(s)


class ButNot(Parser):
    def __init__(self, parser, *nots):
        self.parser = parser
        self.nots = nots

    def parse(self, s, syntax):
        x, s2 = syntax.parse(s, self.parser)
        if s[:-len(s2)].strip() in self.nots:
            raise ParseException(s)
        return x, s2


class Whole(Parser):
    def __init__(self, parser):
        self.parser = parser

    def parse(self, s, syntax):
        x, s = syntax.parse(s, self.parser)
        if s.strip() != '':
            raise ParseException(s)
        return x


class Syntax:
    def __init__(self, parsermap, start=None, handlermap=dict(),
            defaulthandler=idf):
        self.parsermap = parsermap
        self.start = start
        self.handlermap = handlermap
        self.defaulthandler = defaulthandler

    def parse(self, s, start=None, handlermap=None):
        if start is None:
            start = self.start
        if handlermap is not None:
            self.handlermap = handlermap
        if isinstance(start, Parser):
            return start.parse(s, self)
        else:
            result, s = self.parsermap[start].parse(s, self)
            if start in self.handlermap:
                result = self.handlermap[start](result)
            else:
                result = self.defaulthandler(result)
            return result, s
