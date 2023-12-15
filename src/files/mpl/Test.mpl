init @fibonacci
lib @sugar

fnc empty fibonacci : i32 n :
    dec ch i32 a 0
    dec ch i32 b 1
    dec ch i32 c 0

    loop i 1 .. n
        add a b => c // Hello world!
        set a b
        set b c
        out c
    end
end

fibonacci : 10 :
