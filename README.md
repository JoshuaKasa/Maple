# Maple
Maple is my personal transpiled language, written entirely in Python. A transpiled language is one which doesn't have a compiler of its own, but rather translates into another language, and then runs on that language's compiler. In this case, Maple translates into C++, and then runs using the C++ compiler. *This is a very early version of Maple, and it is not yet ready for use. I will update this README when it is ready for use.*

### Purpose
Maple is designed to be a simple, easy-to-use language, with a very unique syntax, inspired by old languages, like ASM. It doesn't really serve any purpose, other than to be a fun project for me to work on, to learn more about programming languages and proving making one isn't as hard as it seems.

## Documentation
### Syntax
As I said before, Maple has a very particular syntax, which is pretty different from most languages. It is inspired by ASM and Rust so it's not that easy to read at first sight. You don't need parenthesis for function calls, if statements and pretty much everything else. You don't need semicolons at the end of lines, and variables are constants by default. Here's an example of a simple program in Maple:
```maple
init @helloworld

fnc empty hello : :
    out "Hello, World!"
end

hello : :
```
Any keyword can't be used in combo with other keywords, here are a few examples which are not valid:
```maple
dec i8 my_var 10
dec i8 my_var2 5

dec i8 my_var3 add my_var my_var2 // This is not valid
set my_var3 add my_var my_var2 // This is not valid
```
*For now* you can't also use variables or array values as indexes, here are a few examples which are not valid:
```maple
dec i8 my_var 10
dec i8 my_var2 5

add my_var my_var2 => my_var[0] // This is not valid
add my_var my_var2 => my_var2[my_var] // This is not valid
```
### Variables
Variables are declared using the "dec" keyword, followed the "ch" keyword (if the variable can be changed), the [type](#Types) of the variable, the name of the variable and the value. For example:
```maple
dec ch i8 my_var 10
```
As in pretty much every other programming language, variable are accessible only in the scope they are declared in. So if you declare a variable inside a function, you can't access it outside of that function.
For declaring [array](#arrays) variables, you must use the "arrow" operator (which is just a "->") but the general syntax will change a bit. Here's an example:
```maple
dec i16 my_var[] 3 -> {1, 2, 3}
``` 
Right here, the value next to the variable name, isn't the value of the variable, but rather the size of the array. The values inside the curly brackets are the values of the array. You can also declare empty arrays, like this:
```maple
dec i16 my_var[] 3 -> {}
```
**Size is required**, even if you're declaring an empty array.
#### Declaration and Assignment
We've already seen how to declare variables, but how do we assign values to them? Well, it's pretty simple, you just use the "set" keyword, followed by the name of the variable and the value you want to assign to it. For example:
```maple
dec ch i8 my_var 10
set my_var 5
```

### Operators
Maple doesn't contain operators or operations, instead everything is done using keywords, these are:
| Keyword | Operation |
|---------|-----------|
| add     | Addition  |
| sub     | Subtraction |
| mul     | Multiplication |
| div     | Division |
| mod     | Modulo |

By default, the result is stored inside the first variable, but you can change that by using the "operational arrow" operator (which is just a "=>"):
```maple
dec i8 my_var 10
dec i8 my_var2 5
dec i8 my_var3 0

add my_var my_var2 // Result will be stored in my_var
sub my_var my_var2 => my_var3 // Result will be stored in my_var3
```
Remember you can't use these with arrays (will soon do) or as operators:
```maple
dec i8 my_var 10
dec i8 my_var2 5

add my_var my_var2 // This is valid
dec i8 my_var3 add my_var my_var2 // This is not valid
```

### Types
Here's a list of all the types in Maple, along with their corresponding C++ type and their size in bytes:
| Maple Type | C++ Type | Size |
|------------|----------|------|
| i8         | int8_t   | 1    |    
| i16        | int16_t  | 2    |
| i32        | int32_t  | 4    |
| i64        | int64_t  | 8    |
| str        | string   | 8    |
| bool       | bool     | 1    |
| f32        | float    | 4    |
| f64        | double   | 8    |
| ch         | char     | 1    |
| empty      | void     | 0    |

### Arrays
We already explained the basics of arrays in the [variables](#variables) section, but here's a more in-depth explanation. Arrays are declared using the "arrow" operator and start from 0, remember you can also declare them empty, like this:
```maple
dec i8 my_var[] 3 -> {}
```
or like this:
```maple
dec i8 my_var[] 3 -> {0, 0, 0}
```
For accessing the values of an array, you can just set the index of the value you want to access, like this:
```maple
dec i8 my_var[] 3 -> {1, 2, 3}
out my_var[0] // This will output 1
```
You can also set the value of an array, like this:
```maple
dec i8 my_var[] 3 -> {1, 2, 3}
set my_var[0] 5
out my_var[0] // This will output 5
```
You CAN'T use variables or array values as indexes, here are a few examples which are not valid:
```maple
dec i8 my_var 10
dec i8 my_var2 5

add my_var my_var2 => my_var[0] // This is not valid
add my_var my_var2 => my_var2[my_var] // This is not valid
```

### Functions
Everything inside Maple is, behind the scenes, a function. As everything is transpiled into C++, functions are the only way to do anything, therefore all of your code (except for the functions) are transpiled into the main function. This also means, that the function declaration order doesn't matter, so you can declare a function at the end of your code, and call it at the beginning. As I've said, functions are the only way to do anything, so you can't just write code outside them; for differentiating every program in the transpiled C++ we will use something called "namespaces", which are just a way to differentiate different programs. For example, if you have two programs, one called "helloworld" and one called "hello", the transpiled C++ will look like this:
```cpp
// First file (helloworld.cpp)
namespace helloworld {
    // Transpiled code
}

// Second file (hello.cpp)
namespace hello {
    // Transpiled code
}
```
But how do we do it in maple? Namespaces must be declared at the beginning of the file, using the "init" keyword, followed by "@" plus the name of the namespace. For example:
```maple
init @helloworld // This will be the namespace of the Maple program

out "Hello, World!"
```
Now, let's talk about *actual* functions. We already said parentheses are not used in Maple, so how do we declare functions? Well, it's pretty simple, you just use ":", take a look at this example:
```maple
init @helloworld

fnc empty hello : : // No return type, no arguments
    out "Hello, World!"
end

hello : :
```
First of all, let's give a bit of context. The "fnc" keyword is used to declare a function, followed by the return [type](#Types) of the function (if it doesn't return anything, you can use the "empty" keyword), the name of the function, the arguments (if any) and the return type (if any), remember that the space between the arguments and the 2 colons is required:
```maple
fnc i64 pow : i64 a, i64 b : // This function takes 2 i64 arguments and returns an i64
    dec ch i64 result 1
    
    loop i 1 .. b
        mul result result
    end

    rtn result
end // Closing the function declaration
```
The "end" keyword is used to end the function declaration (just like the curly brackets in C++), and the "rtn" keyword is used to return a value from the function.
