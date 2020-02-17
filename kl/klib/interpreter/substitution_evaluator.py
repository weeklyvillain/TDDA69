import operator

from klib.ast import visitor as ast_visitor
from klib.parser.operators import binary_operator
from klib.parser import binary_operator, unary_operator
import klib.exception
import klib.vm
import klib.parser
import klib.ast
import klib.environment
import klib.environment.utils as ke_utils

from .kl_exception import kl_exception

class substitution_exception(klib.exception):
  def __init__(self, message, metadata):
    super().__init__(message, metadata = metadata)

unary_operator_functions = {
    unary_operator.AdditiveInverse: operator.neg,
    unary_operator.Identity:        lambda a: a,
    unary_operator.LogicalNegation: operator.not_,
    unary_operator.Tilde:           lambda a: ~int(a)
  }

binary_operator_functions = {
    binary_operator.Addition:       operator.add,
    binary_operator.Substraction:   operator.sub,
    binary_operator.Multiplication: operator.mul,
    binary_operator.Division:       operator.truediv,
    binary_operator.Remainder:      operator.mod,
    binary_operator.ShiftLeft:      lambda a, b: int(a) << int(b),
    binary_operator.ShiftRight:     lambda a, b: int(a) >> int(b),
    binary_operator.LogicalAnd:     operator.and_,
    binary_operator.LogicalOr:      operator.or_,
    binary_operator.Equal:          operator.eq,
    binary_operator.NotEqual:       operator.ne,
    binary_operator.Less:           operator.lt,
    binary_operator.Greater:        operator.gt,
    binary_operator.LessEqual:      operator.le,
    binary_operator.GreaterEqual:   operator.ge
  }

class substitution_evaluator(ast_visitor):
  def __init__(self, modules_manager, environment, developer_verbose = False):
    self.environment = environment
    self.modules_manager = modules_manager
    if not self.modules_manager:
      self.modules_manager = klib.interpreter.modules_manager()
    self.developer_verbose = developer_verbose

  def __get_value(self, value):
    #print(type(value))
    if isinstance(value, klib.environment.reference):
        return value.environment.get(value.name).get_value()
    return value

  def visit_ast(self, node):
    self.visit_statements(node.statements)

  def visit_value(self, node):
    return node.value

  def visit_identifier(self, node):
    return klib.environment.reference(self.environment, node.identifier)

  def visit_env_expression(self, node):
    return self.environment

  def visit_function_call(self, node):
    raise Exception("substitution_evaluator: unimplemented")

  def visit_native_call(self, node):
    module = klib.native.modules[node.type]
    native_function = module.get(node.name)
    if module:
      native_function = module.get(node.name)
    else:
      raise klib.exception.unknown_native_type(node.type)
    if not native_function:
      raise klib.exception .unknown_native_function(node.type, node.name)
    args = []
    for arg in node.arguments:
      args.append(self.__get_value(arg.accept(self)))
    native_function(*args)


  def lambda_declaration(self, node):
    return klib.environment.function(node.arguments, node.body, self.environment, **ke_utils.function_modifiers(node))

  def visit_import_statement(self, node):
    raise Exception("substitution_evaluator: unimplemented")

  def visit_return_expression(self, node):
    raise Exception("substitution_evaluator: unimplemented")

  def visit_named_block(self, node):
    if node.type is '___define___':
      for name in node.names:
        self.environment.define_value(name, init_value=node.body.accept(self))
    elif node.type is '___cell___':
      print(node.names)
      for name in node.names:
        initial = None
        if node.body is not None:
          print(self.__get_value(node.body.accept(self)))
          initial = self.__get_value(node.body.accept(self))
        self.environment.define_cell(name, init_value=initial)
    #print(node.names)
    #print(node.type)
    #print(node.arguments)
    #print(node.modifiers)
    #print(node.op)
    #print(node.body)
    #print(node.metadata)
    #raise Exception("substitution_evaluator: unimplemented")

  def __set_value(self, node):
    print(node.left.identifier)
    if not self.environment.get(node.left.identifier).is_writable():
        raise substitution_exception("Cant set value", node.metadata)
    return self.environment.get(node.left.identifier).set_value(self.__get_value(node.right.accept(self)))

  def visit_statements(self, statements):
    for statement in statements:
      statement.accept(self)
    #raise Exception("substitution_evaluator: unimplemented")

  def visit_binary_operation(self, node):
    if node.op is 5: # Assignment
      return self.__set_value(node)

    if node.op is 0: # Member
      outer_ref = node.left.accept(self)
      env = outer_ref.environment.get(outer_ref.name).get_value()

      inner_ref = node.right.accept(self)
      inner_ref.environment = env
      return inner_ref

      #print(env.get(node.right.identifier).get_value())
      #return klib.environment.reference(env, node.right.identifier)
      #return env.get(node.right.identifier).accept(self)


    return binary_operator_functions[node.op](self.__get_value(node.left.accept(self)), self.__get_value(node.right.accept(self)))
    #raise Exception("substitution_evaluator: unimplemented")

  def visit_unary_operation(self, node):
    return unary_operator_functions[node.op](node.right.accept(self))
    #raise Exception("substitution_evaluator: unimplemented")

  def visit_clear_expression(self, node):
    for value in node.values:
      ref = value.accept(self)
      ref.environment.clear(ref.name)
    #raise Exception("substitution_evaluator: unimplemented")

  def visit_cond_expression(self, node):
    raise Exception("substitution_evaluator: unimplemented")

  def visit_catch_expression(self, node):
    raise Exception("substitution_evaluator: unimplemented")

  def visit_raise_expression(self, node):
    raise Exception("substitution_evaluator: unimplemented")

  def visit_expression_statement(self, node):
    return node.expression.accept(self)
    raise Exception("substitution_evaluator: unimplemented")

  def visit_block_expression(self, node):
    new_env = klib.environment.environment(parent=self.environment)
    self.environment = new_env
    for statement in node.statements:
      statement.accept(self)
    self.environment = self.environment.parent
    return new_env
    #raise Exception("substitution_evaluator: unimplemented")

  def visit_group_expression(self, node):
    print(node)
    for statement in node.statements:
      statement.accept(self)
    #raise Exception("substitution_evaluator: unimplemented")

  def visit_call_trace_expression(self, node):
    return [node.metadata]
