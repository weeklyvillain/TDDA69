import klib.lexer
import copy

from .rule import multi_variable_node

class rule_no_match(Exception):
  pass

class rule_matcher(klib.lexer.tokens_tree_visitor):
  def __init__(self):
    self.variables = {}
    
  def visit_token_group_node(self, rule_node, program_node):
    if not isinstance(program_node, klib.lexer.token_group_node) or len(rule_node.children) > len(program_node.children):
      #klib.io.stdout.writeln("token_group_node: not match {} {}", len(rule_node.children), len(program_node.children))
      raise rule_no_match()
    else:
      rule_index    = 0
      program_index = 0
      
      while rule_index < len(rule_node.children) and program_index < len(program_node.children):
        c_rn = rule_node.children[rule_index]
        p_rn = program_node.children[program_index]
        
        if type(c_rn) is multi_variable_node:
          matches = []
          rules_count = len(c_rn.children_node.children)
          while program_index + rules_count <= len(program_node.children):
            try:
              rm = rule_matcher()
              for i in range(0, rules_count):
                c_rn.children_node.children[i].accept(rm, program_node.children[program_index + i])
              program_index += rules_count
              matches.append(rm.variables)
            except rule_no_match:
              break
          self.variables[c_rn.variable] = matches
          rule_index    += 1
        else:
          c_rn.accept(self, p_rn)
          rule_index    += 1
          program_index += 1
      
      if rule_index != len(rule_node.children) or program_index != len(program_node.children):
        #klib.io.stdout.writeln("token_group_node: not match {} {}", rule_index, program_index)
        raise rule_no_match()
      
  def visit_statement_node(self, rule_node, program_node):
    if not isinstance(program_node, klib.lexer.statement_node):
      #klib.io.stdout.writeln("statement_node: not match")
      raise rule_no_match()
    self.visit_token_group_node(rule_node, program_node)
  
  def visit_block_node(self, rule_node, program_node):
    if not isinstance(program_node, klib.lexer.block_node) or rule_node.start_token.type != program_node.start_token.type or rule_node.end_token.type != program_node.end_token.type:
      #klib.io.stdout.writeln("block_node: not match")
      raise rule_no_match
    self.visit_token_group_node(rule_node, program_node)
  
  def visit_token_node(self, rule_node, program_node):
    if not isinstance(program_node, klib.lexer.token_node) or rule_node.token.type != program_node.token.type or rule_node.token.text != program_node.token.text:
      #if not isinstance(program_node, klib.lexer.token_node):
        #klib.io.stdout.writeln("token_node: not match {}", str(program_node))
      #else:
        #klib.io.stdout.writeln("token_node: not match text {} != {}", rule_node.token.text, program_node.token.text)
      raise rule_no_match()

  def visit_variable_node(self, rule_node, program_node):
    self.variables[rule_node.variable] = program_node

class rule_producer(klib.lexer.tokens_tree_visitor):
  def __init__(self, variables):
    self.variables = variables
  
  def __visit_chidlren(self, node):
    ncn = []
    for cn in node.children:
      nc = cn.accept(self)
      if nc:
        try:
          ncn += nc
        except TypeError:
          ncn.append(nc)


    return ncn
  
  def visit_token_group_node(self, node):
    return klib.lexer.token_group_node(self.__visit_chidlren(node))
  
  def visit_statement_node(self, node):
    return klib.lexer.statement_node(self.__visit_chidlren(node))

  def visit_block_node(self, node):
    return klib.lexer.block_node(copy.deepcopy(node.start_token), copy.deepcopy(node.end_token), self.__visit_chidlren(node))

  def visit_token_node(self, node):
    return copy.deepcopy(node)
  
  def visit_variable_node(self, node):
    return copy.deepcopy(self.variables[node.variable])
    
  def visit_multi_variable_node(self, node):
    nc = []
    
    for vars in self.variables[node.variable]:
      rp = rule_producer(vars)
      for c in node.children_node.children:
        nc.append(c.accept(rp))
    
    return nc
    

class engine(klib.lexer.tokens_tree_editor):
  '''
  '''
  def __init__(self):
    super().__init__()
    self.__rules = []
  
  def add_rule(self, rule):
    self.__rules.append(rule)

  def visit_token_group_node(self, node):
    for r in self.__rules:
      match_rules = r.get_match()
      #klib.io.stdout.writeln("///////////////////////////////////////////////////////")
      #klib.lexer.print_tokens_tree(node)
      
      if(len(match_rules) <= len(node.children)):
        i = 0
        while i <= (len(node.children) - len(match_rules)):
          rm = rule_matcher()
          try:
            while i <= len(node.children) - len(match_rules): # We might have to reapply the same rule
              for j in range(0, len(match_rules)):
                match_rules[j].accept(rm, node.children[i+j])
            
              # We have a match, apply production
              rp = rule_producer(rm.variables)
              produced_node = r.get_production().accept(rp)
              del node.children[i:len(match_rules)]
              node.children.insert(i, produced_node)
          except rule_no_match:
            pass
          node.children[i].accept(self)
          i += 1
          
    for c in node.children:
      c.accept(self)
    return node
    
  def visit_token_node(self, node):
    for r in self.__rules:
      try:
        rm = rule_matcher()
        match_rules = r.get_match()
        if len(match_rules) == 1:
          rm[0].accept(node)
          raise Exception("wip")
      except rule_no_match:
        pass

    return super().visit_token_node(node)
