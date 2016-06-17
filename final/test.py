from lua_sem import Analysis, State
from lua_syn import parser
from sem import SS
from tex import *

with open('code.lua', 'r') as f:
    code = f.read()

parsed, remaining = parser.parse(code, 'block')

functionbody = mex(parser.parse('''
	delta = 1
	pointer = 0
	while true do
		if x then
			delta = delta * (-1)
		else end
		pointer = pointer + delta
		x = coroutine.yield(pointer)	
	end
'''.strip())[0])

if remaining.strip() != '':
    raise Exception(remaining)

ana = Analysis(parsed)

ana.step(SS(parsed, State()))

body = mex(ana)
#body = body.replace(functionbody, 'B_f')
#body = where(body, r'B_f = ' + functionbody)
body = r'\(' + body + r'\)'

doc = document(body)

doc = doc.replace(r'\documentclass{article}', r'\documentclass{standalone}')

with open('test.tex', 'w') as f:
    f.write(doc)
