class kl_exception(Exception):
  def __init__(self, value):
    self.value = value

class kl_return(Exception):
  def __init__(self, value):
    self.value = value
