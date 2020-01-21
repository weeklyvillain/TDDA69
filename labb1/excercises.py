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
