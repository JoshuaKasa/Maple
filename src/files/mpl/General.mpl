lib @sugar

run 5

dec i16 x 10
dec ch i16 y 10
dec ch i16 z 5
back z
dec ch i16 a[] 5
dec i16 e[] 3 -> {1, 2, 3}
set z y 
set y 10
out a[1]
set a[1] e[1]

if z > x
    out z
    if z > y
    	out z
	around i 1 .. 5
	    around j 3
                out i
	    roll
	roll
    end
end

load z

out x
out y
out z

