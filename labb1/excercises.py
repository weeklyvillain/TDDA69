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


# 1.4 a)
def foldl(f, null, array):
    if len(array) is 0:
        return null
    else:
        value = array.pop()
        return f(foldl(f, null, array), value)

# 1.4 b)
def foldr(f, null, array):
    if len(array) is 0:
        return null
    else:
        value = array.pop(0)
        return f(value, foldr(f, null, array))


print(foldl(lambda x,y: x*y, 1, [1,2,3,4,5]))
print(foldr(lambda x,y: x*y, 1, [1,2,3,4,5]))


# 1.4 c)  Define the following functions as calls to foldr and foldl.
def my_map(f, seq):
    new_list = []
    foldl(lambda x, y: new_list.append(f(y)), [], seq)
    return new_list

def reverse_r(seq):
    new_list = []
    foldr(lambda x,y: new_list.append(x), 0, seq)
    return new_list

def reverse_l(seq):
    new_list = []
    foldl(lambda x,y: new_list.insert(0,y), 0, seq)
    return new_list


print(my_map(lambda n: n*2, [1,2,3]))
print(reverse_r([1,2,3]))
print(reverse_l([1,2,3]))


# 1.5 a)
def repeat(f, n):
    #return lambda x: f(x)**n

    def inner(x):
        for i in range(n):
            x = f(x)
        return x
    return inner

sq = lambda x: x*x
sq_twice = repeat(sq, 2)
print(sq_twice(5))

# 1.5 b)
# Repeat needs to take in a function as first argument and an integer as second argument and it will always return an integer as answer.
# The function (f) needs to take in one parameter and needs to return an integer.

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
