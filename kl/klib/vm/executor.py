import klib.math

import klib.environment

from klib.bytecode import opcodes
from .stack   import stack
from klib.io import stdout
import klib.interpreter.kl_exception

from klib.environment.environment import unknown_cell


class executor_context:
  def __init__(self, program, environment):
    self.program          = program
    self.environment      = environment
    self.current_index    = 0
    self.stack            = stack()
    self.exceptions_stack = stack()

class exception_context:
  def __init__(self, index):
    self.index = index

class executor:

  opmaps = {}

  def __init__(self):
    self.current_context = None
    self.execution_stack = stack()

    if(len(executor.opmaps) == 0):
      # Stack
      executor.opmaps[opcodes.PUSH] = executor.execute_push
      executor.opmaps[opcodes.POP] = executor.execute_pop
      executor.opmaps[opcodes.DUP] = executor.execute_dup
      executor.opmaps[opcodes.SWAP] = executor.execute_swap
      executor.opmaps[opcodes.PUSH_ENV] = executor.execute_push_env
      executor.opmaps[opcodes.NEW_ENV] = executor.execute_new_env
      executor.opmaps[opcodes.DROP_ENV] = executor.execute_drop_env
      executor.opmaps[opcodes.MAKE_REF] = executor.execute_make_ref
      executor.opmaps[opcodes.STORE] = executor.execute_store
      executor.opmaps[opcodes.DCL_CELL] = executor.execute_dcl_cell




  def execute(self, program, environment = klib.environment.environment(), caller_metadata = None, verbose = False, return_stack = False):
    self.current_context = executor_context(program, environment)
    self.caller_metadata = caller_metadata

    if verbose:
      program.print()

    while(self.current_context.current_index < len(self.current_context.program.instructions)):

      inst = self.current_context.program.instructions[self.current_context.current_index]

      if verbose:
        stdout.writeln("===== In context level: {}", len(self.execution_stack))
        stdout.write("{}: {} ({})", self.current_context.current_index, inst.opcode.name, inst.opcode.index)
        for k in inst.params:
          stdout.write(" {}={}", k, inst.params[k])
        stdout.writeln("")

        self.current_context.stack.print()

      #print(inst.opcode.name)
      f = executor.opmaps[inst.opcode]

      r = f(self, **inst.params)

      self.current_context.current_index += 1

    if(len(self.execution_stack) != 0):
      raise Exception("execution stack is not empty")

    if return_stack:
      return self.current_context.stack.stack

    if(len(self.current_context.stack) > 0):
      return self.__pop_value()

  def execute_push(self, value):
    self.current_context.stack.push(value)

  def execute_dup(self):
    self.current_context.stack.dup()

  def execute_swap(self):
    self.current_context.stack.swap()

  def execute_pop(self, count = 1):
    for i in range(0, count):
      self.current_context.stack.pop()

     # reference.enviroment = self.current_context.enviroment
     #

  def execute_push_env(self):
    self.current_context.stack.push(self.current_context.environment)

  def execute_new_env(self):
    self.current_context.environment = klib.environment.environment(self.current_context.environment)

  def execute_drop_env(self):
    self.current_context.environment = self.current_context.environment.parent

  def execute_make_ref(self, name=None):
    if name == None:
      name = self.current_context.stack.pop()
    #  Pusha en ny reference till stacken, dens environment blir det längst upp på den nuvarande stacken.
    self.current_context.stack.push(klib.environment.reference(self.current_context.stack.pop(), name))


  def execute_store(self, name=None):
    value = self.current_context.stack.pop()

    # Hämta environmentet vi ska hantera, antingen från en referens ifall name = None, annars det som finns längst upp på stacken.
    environment = None
    if name == None:
      reference = self.current_context.stack.pop()
      environment = reference.environment
      name = reference.name
    else:
      environment = self.current_context.stack.pop()

    # Ifall value är en referense måste vi avreferera det och hämta dens riktiga värde.
    while isinstance(value, klib.environment.reference):
      value = value.environment.get(value.name)

    # Ifall value är en cell måste vi hämta dens numreriska värde.
    while isinstance(value, klib.environment.cell.cell):
      value = value.get_value()

    # Uppdatera värdet på cellen om den finns annars definiera en ny.
    try:
      cell = environment.get(name)
      cell.set_value(value)
    except unknown_cell as e:
      environment.define_cell(name, value)

    # Pusha det refererade värdet till stacken.
    self.execute_push(value)


  def execute_dcl_cell(self, name):
    self.current_context.environment.define_cell(name, self.current_context.stack.pop())
    #self.current_context.stack.pop().define_cell(name)
