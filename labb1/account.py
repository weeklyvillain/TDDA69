class AccountError(Exception):
  def __init__(self, value):
    self.value = value
  def str(self):
    return repr(self.value)

def make_account(balance, rate):
  lastTime = 0
  def withdraw(amount, t):
    nonlocal balance
    nonlocal lastTime
    nonlocal rate
    if balance < amount:
      raise AccountError("Account balance too low")
    elif t < lastTime:
      raise AccountError("You can't go back in time")

    # calculate and add intrest
    intrest = (t - lastTime) * rate * balance
    balance += intrest
    lastTime = t
    # Remove amount from the balance
    balance -= amount

  def deposit(amount, t):
    nonlocal balance
    nonlocal lastTime
    nonlocal rate

    if t < lastTime:
        raise AccountError("You can't go back in time")

    intrest = (t - lastTime) * rate * balance
    balance += (intrest + amount)
    lastTime = t



  def get_value():
    nonlocal balance
    return balance

  public_methods = {'withdraw' : withdraw, 'deposit' : deposit, 'get_value' : get_value}
  return public_methods


a1 = make_account(10, 0.1)
a2 = make_account(10, 0.01)
a1['deposit'](100, 10)
a2['withdraw'](10, 10)
print("A1: ", a1['get_value']())
print("A2: ", a2['get_value']())



# 2.3 b)
# -- Global Scope --
#   a1: {'withdraw': function, 'deposit': function, 'get_value': function}
#   a2: {'withdraw': function, 'deposit': function, 'get_value': function}

# -- a1 Scope --
#   lastTime: 10
#   rate: 0.1
#   balance: 120
#   withdraw: function...
#   deposit: funciton...
#   get_value: function...

# -- a2 Scope --
#   lastTime: 10
#   rate: 0.01
#   balance: 1
#   withdraw: function...
#   deposit: funciton...
#   get_value: function...
