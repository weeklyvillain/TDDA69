import klib.math

import klib.environment

from klib.bytecode import opcodes
from .stack   import stack
from klib.io import stdout
import klib.interpreter.kl_exception
import klib.exception

from klib.interpreter.kl_exception import kl_exception, kl_return
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
      executor.opmaps[opcodes.DEF_VALUE] = executor.execute_def_value
      executor.opmaps[opcodes.CLEAR] = executor.execute_clear
      executor.opmaps[opcodes.PUSH_CALL_TRACE] = executor.execute_push_call_trace
      executor.opmaps[opcodes.JMP] = executor.execute_jmp
      executor.opmaps[opcodes.IFJMP] = executor.execute_ifjmp
      executor.opmaps[opcodes.UNLESSJMP] = executor.execute_unlessjmp
      executor.opmaps[opcodes.RET] = executor.execute_ret
      executor.opmaps[opcodes.NATIVE_CALL] = executor.execute_native_call
      executor.opmaps[opcodes.CALL] = executor.execute_call
      executor.opmaps[opcodes.TRY_PUSH] = executor.execute_try_push
      executor.opmaps[opcodes.TRY_POP] = executor.execute_try_pop
      executor.opmaps[opcodes.THROW] = executor.execute_throw
      executor.opmaps[opcodes.MAKE_FUNC] = executor.execute_make_func
      executor.opmaps[opcodes.ADD] = executor.execute_add
      executor.opmaps[opcodes.SUB] = executor.execute_sub
      executor.opmaps[opcodes.DIV] = executor.execute_div
      executor.opmaps[opcodes.MUL] = executor.execute_mul
      executor.opmaps[opcodes.MOD] = executor.execute_mod
      executor.opmaps[opcodes.LEFT_SHIFT] = executor.execute_left_shift
      executor.opmaps[opcodes.RIGHT_SHIFT] = executor.execute_right_shift
      executor.opmaps[opcodes.UNSIGNED_RIGHT_SHIFT] = executor.execute_unsigned_right_shift
      executor.opmaps[opcodes.GREATER] = executor.execute_greater
      executor.opmaps[opcodes.GREATER_EQUAL] = executor.execute_greater_equal
      executor.opmaps[opcodes.LESS] = executor.execute_less
      executor.opmaps[opcodes.LESS_EQUAL] = executor.execute_less_equal
      executor.opmaps[opcodes.EQUAL] = executor.execute_equal
      executor.opmaps[opcodes.DIFFERENT] = executor.execute_different
      executor.opmaps[opcodes.AND] = executor.execute_and
      executor.opmaps[opcodes.OR] = executor.execute_or
      executor.opmaps[opcodes.NEG] = executor.execute_neg
      executor.opmaps[opcodes.TILDE] = executor.execute_tilde
      executor.opmaps[opcodes.NOT] = executor.execute_not



  def __pop_value(self):
    value = self.current_context.stack.pop()
    while isinstance(value, klib.environment.reference):
      value = value.environment.get(value.name)

    while isinstance(value, klib.environment.cell.cell) or isinstance(value, klib.environment.value.value):
      value = value.get_value()
    return value

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
    #self.current_context.environment.define_cell(name, self.current_context.stack.pop())
    self.current_context.stack.pop().define_cell(name)

  def execute_def_value(self, name):
    value = self.current_context.stack.pop()
    env = self.current_context.stack.pop()
    env.define_value(name, value)

  def execute_clear(self, name=None):
    # Ifall vi inte gett ett namn cleara referencens namn i referencens environment.
    if name == None:
      ref = self.current_context.stack.pop()
      name = ref.name
      env = ref.environment
    else:
      env = self.current_context.stack.pop()
    env.clear(name)
    self.execute_push(None)

  def execute_push_call_trace(self):
    metadata = klib.parser.metadata(self.current_context.current_index, 0, None, None, self.current_context.environment.parent)
    self.execute_push([metadata])

  def execute_jmp(self, index):
    self.current_context.current_index = index-1

  def execute_ifjmp(self, index):
    if self.current_context.stack.pop():
      self.execute_jmp(index)

  def execute_unlessjmp(self, index):
    if not self.current_context.stack.pop():
      self.execute_jmp(index)

  def execute_ret(self):
    # Sätt current_index till slutet av programmet så inget mer exekveras.
    self.current_context.current_index = len(self.current_context.program.instructions)

  def execute_native_call(self, native_function, count):
    args = []
    for i in range(count):
      args.append(self.current_context.stack.pop())
    self.execute_push(native_function(*args))

  def execute_call(self, count):
    func = self.current_context.stack.pop()
    args = []
    for i in range(count):
      args.append(self.current_context.stack.pop())

    env, program = func.prepare_call(args)
    self.execute_push(*self.execute(program, env))

  def execute_try_push(self, index):
    self.current_context.exceptions_stack.push(index)

  def execute_try_pop(self):
    self.current_context.exceptions_stack.pop()

  def execute_throw(self):
    # Hoppa till första indexet i exceoptions_stack ifall det finns, annars throw kl_exception
    index = None
    try:
      index = self.current_context.exceptions_stack.stack[0]
      self.execute_jmp(index)
    except IndexError as e:
      raise kl_exception("No jmp index on the exception stack")

  def execute_make_func(self, body, argument_names, modifiers):
    self.execute_push(klib.environment.function(argument_names, body, self.current_context.environment))

  def execute_add(self):
    self.execute_push(self.current_context.stack.pop() + self.current_context.stack.pop())

  def execute_sub(self):
    v2 = self.current_context.stack.pop()
    v1 = self.current_context.stack.pop()
    self.execute_push(v1 - v2)

  def execute_div(self):
    v2 = self.current_context.stack.pop()
    v1 = self.current_context.stack.pop()
    self.execute_push(v1 / v2)

  def execute_mul(self):
    self.execute_push(self.current_context.stack.pop() * self.current_context.stack.pop())

  def execute_mod(self):
    v2 = self.current_context.stack.pop()
    v1 = self.current_context.stack.pop()
    self.execute_push(v1 % v2)

  def execute_left_shift(self):
    v2 = self.current_context.stack.pop()
    v1 = self.current_context.stack.pop()
    # v1 << v2 = v1 * pow(2,v2)
    self.execute_push(int(v1 * (2 ** v2)))

  def execute_right_shift(self):
    v2 = self.current_context.stack.pop()
    v1 = self.current_context.stack.pop()
    # v1 >> v2 = v1 / pow(2,v2)
    self.execute_push(int(v1 / (2 ** v2)))

  def execute_unsigned_right_shift(self):
    v2 = self.current_context.stack.pop()
    v1 = self.current_context.stack.pop()
    # Unsigned right shift = push 0 to the left of the binary representation of the number.
    self.execute_push(int(v1 % 0x100000000) >> int(v2))

  def execute_greater(self):
    v2 = self.current_context.stack.pop()
    v1 = self.current_context.stack.pop()
    self.execute_push(v1 > v2)

  def execute_greater_equal(self):
    v2 = self.current_context.stack.pop()
    v1 = self.current_context.stack.pop()
    self.execute_push(v1 >= v2)

  def execute_less(self):
    v2 = self.current_context.stack.pop()
    v1 = self.current_context.stack.pop()
    self.execute_push(v1 < v2)

  def execute_less_equal(self):
    v2 = self.current_context.stack.pop()
    v1 = self.current_context.stack.pop()
    self.execute_push(v1 <= v2)

  def execute_equal(self):
    self.execute_push(self.current_context.stack.pop() == self.current_context.stack.pop())

  def execute_different(self):
    self.execute_push(self.current_context.stack.pop() != self.current_context.stack.pop())

  def execute_and(self):
    v2 = self.current_context.stack.pop()
    v1 = self.current_context.stack.pop()
    self.execute_push(v2 and v1)

  def execute_or(self):
    v2 = self.current_context.stack.pop()
    v1 = self.current_context.stack.pop()
    self.execute_push(v2 or v1)

  def execute_neg(self):
    self.execute_push(self.current_context.stack.pop() * -1)

  def execute_tilde(self):
    self.execute_push(~int(self.current_context.stack.pop()))

  def execute_not(self):
    self.execute_push(not self.current_context.stack.pop())
