function indec(x)
	delta = 1
	pointer = 0
	while true do
		if x then
			delta = delta * (-1)
		end
		pointer = pointer + delta
		x = coroutine.yield(pointer)	
	end
end

co = coroutine.wrap(indec)
it0 = co(false)		-- it0 = 1 
it1 = co(false)		-- it1 = 2
it2 = co(true)		-- it2 = 1

