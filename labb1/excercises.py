def sum(term, lower, successor, upper):
    if lower > upper:
        return 0
    else:
        return term(lower) + \
               sum(term, successor(lower), successor, upper)


print(sum(lambda n: n, 1, lambda n: n+1, 10))

# 1.1 a)
def sum_iter(term, lower, successor, upper):
    def iter(lower, result):
        if lower > upper:
            return result
        else:
            result += term(lower)
            return iter(successor(lower), result)
    return iter(lower, 0)

print(sum_iter(lambda n: n*n, 1, lambda n: n+1, 10))

# 1.1 b)
# This is a tail recursive function since sum_iter doesn't do
# any calculations after its return statementself.
# iter is however not a tail-recursive function since it does
# calculations after its return statement.


# 1.2 a)
def product(term, lower, successor, upper):
    if lower > upper:
        return 1
    else:
        return term(lower) * \
               product(term, successor(lower), successor, upper)

print(product(lambda n: n, 1, lambda n: n+1, 10))


def product_iter(term, lower, successor, upper):
    def iter(lower, result):
        if lower > upper:
            return result
        else:
            result *= term(lower)
            return iter(successor(lower), result)
    return iter(lower, 1)

print(product_iter(lambda n: n, 1, lambda n: n+1, 10))


# 1.2 b)

def factorial(x):
    return product_iter(lambda n: n, 1, lambda n: n+1, x)

print(factorial(10))
print(factorial(5))


# 1.3 a)

def accumulate(combiner, null, term, lower, succ, upper):
    if lower > upper:
        return null
    else:
        return combiner(term(lower), \
               accumulate(combiner, null, term, succ(lower), succ, upper))

print(accumulate(lambda x,y: x+y, 0, lambda n: n, 1, lambda n: n+1, 10))
print(accumulate(lambda x,y: x*y, 1, lambda n: n, 1, lambda n: n+1, 10))

def accumulate_iter(combiner, null, term, lower, succ, upper):
    def iter(lower, result):
        if lower > upper:
            return result
        else:
            result = combiner(result, term(lower))
            return iter(succ(lower), result)
    return iter(lower, null)

print(accumulate_iter(lambda x,y: x+y, 0, lambda n: n, 1, lambda n: n+1, 10))
print(accumulate_iter(lambda x,y: x*y, 1, lambda n: n, 1, lambda n: n+1, 10))

# 1.3 b)

def product(term, lower, successor, upper):
    return accumulate_iter(lambda x,y: x*y, 1, term, lower, successor, upper)

print(product(lambda n: n, 1, lambda n: n+1, 10))


def sum(term, lower, successor, upper):
    return accumulate(lambda x,y: x+y, 0, term, lower, successor, upper)

print(sum(lambda n: n, 1, lambda n: n+1, 10))

# 1.3 c)
# For example it doesn't work with subtraction . This is because of the parenthesis that are created
# by the accumulate and accumulate_iter. In the case of the accumulate funciton the parenthesis are
# created incorrectly while in the accumulate_iter the parenthesis are created correctly.
# The problem with accumulate_iter is that it starts with the null value - the first value.
# For example 5-6-7 with a null value of 0 would look like this: 0-5-6-7.
#
# To fix the accumulate function the combiner must assure that the order of the subtraction is correct.
# To fix the accumulate_iter function we must assure that the starting value is double the value of the
# lower value. For example 5-6-7 with a null value of 10 would be like this: 10-5-6-7 wich is equal to
# 5-6-7.

# Komplettering: We want accumulate and accumulate_iter to have associative property and Commutative property.


# 1.4 a)
def foldl(f, null, array, counter=-1):
    if len(array) == counter*-1 - 1:
        return null
    else:
        value = array[counter]
        return f(foldl(f, null, array, counter - 1), value)




def foldr(f, null, array, counter=0):
    if len(array) is counter:
        return null
    else:
        value = array[counter]
        return f(value, foldr(f, null, array, counter + 1))

print(foldl(lambda x,y: x*y, 1, [1,2,3,4,5]))
print(foldr(lambda x,y: x*y, 1, [1,2,3,4,5]))


# 1.4 c)  Define the following functions as calls to foldr and foldl.
def my_map(f, seq):
    return foldl(lambda x, y: x + [f(y)], [], seq)

def reverse_r(seq):
    return foldr(lambda x,y: y + [x], [], seq)

def reverse_l(seq):
    return foldl(lambda x,y: [y] + x, [], seq)


print(my_map(lambda n: n*2, [1,2,3]))
print(reverse_r([1,2,3]))
print(reverse_l([1,2,3]))


# 1.5 a)


# repeat(f, 3)(20)
# f(f(f(20)))
def repeat(f, n):
    if n == 0:
        return lambda x: x
    else:
        return lambda x: f(repeat(f, n-1)(x))


sq = lambda x: x*x
sq_twice = repeat(sq, 2)

print(sq_twice(5))

# 1.5 b)
# Repeat needs to take in a function as first argument and an integer as second argument.
# The function (f) needs to take in one parameter.
# utdata måste vara en delmängd av indata
#

""""
    f1(x) = 1 om x udda, -1 om x jämnt.
    f1 : Z -> R  [heltal in, reella ut]
    f1(5), f1(f1(5))

    f2(x) = 1 om x udda, -1 om x jämnt.
    f2 : Z+ -> R  [positiva heltal in, reella ut]
    f2(5), f2(f2(5)), f2(4), inte f2(f2(4))=f2(-1)

    f3(x) = 1 om x udda, 2 om x jämnt.
    f3 : Z+ -> R  [positiva heltal in, reella ut]
    f3... ok!

""""

# 1.5 c)
def compose(f, g):
    return lambda x: f(g(x))

# should be 8 (2*2*2)
print(compose(lambda x: x*2, lambda x: x*2)(2))

# 1.5 d)
# def accumulate(combiner, null, term, lower, succ, upper):

def repeated_application(f, n):
    return lambda x: accumulate(lambda y,z: compose(f, f)(x), 0, lambda y: y, 0, lambda y: y+1, n)

sq = lambda x: x*x
sq_twice = repeated_application(sq, 2)
print(sq_twice(2))


# 1.6 a)
def smooth(f):
    dx = 0.01
    return lambda x: (f(x-dx) + f(x) + f(x+dx)) / 3

print(smooth(lambda x: x*x)(4))

# 1.6 b)
def n_fold_smooth(f, n):
    func = lambda x: smooth(x)
    return repeat(func, n)(f)

five_smoothed_square = n_fold_smooth(sq, 5)
print(five_smoothed_square(4))


# 2.1
# If we execute it with normal order evaluation it would
# crash with a maximum recursion depth error.
# This is because we send in f() instead of just the funciton f.

# Komplettering:
# The normal evaluation order will start from the left and evaluate the code.
#
# If we do the same in a lazy langauge it would not crash since
# the funciton f is pure it wont be executed until it is needed (in the else statement)
#
# It would also crash in a applicative-order evaluation
# since it would evaluate the parameters before the function
# is called.

# 2.2 a)
# --- x=10, value=Stored  // This is printed because value is a local variable so changing the global variable "value" wont change the output
# In g: 5000 // We call the function and it will use the local variable "x", not the global.
# In f: 10 // g() calls f() and it will use the global variable x.
# In g: 5000 // We call the function g() and it will print 5000 (the local x value)
# In f: 0 // The global x value has now been changed to 0 so the f() function will output 0.

# 2.2 b)
# Global state before the value of x is changed to 0
# -- Global State --
#   x: 10
#   f: function...
#   g: function...
#   keep_val: function...
#   print_mess: function...
#   value: "New and updated."

# -- keep_val State --
#   value: "Stored"
#   f: function...

# Global state after everything has executed
# -- Global State --
#   x: 0
#   f: function...
#   g: function...
#   keep_val: function...
#   print_mess: function...
#   value: "New and updated."



# 2.2 c)
# --- x=10, value=New and Updated.
# In g: 5000
# In f: 5000
# In g: 5000
# In f: 5000
