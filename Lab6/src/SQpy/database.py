from .ast import token, ast
from collections import namedtuple

class database(object):
  def __init__(self):
    self.db_tables = []
    #self.db_content = []

  def tables(self):
    tables = []
    for table in self.db_tables:
      tables.append(table.get_table_name())
    return tables


  def fields(self, name):
    for table in self.db_tables:
      if table.get_table_name() == name:
        return table.get_table_fields()

  def dump_table(self, name):
    table_obj = self.get_table_object(name)
    return table_obj.content

  def execute(self, query):
    # CREATE TABLE
    if query.token == token.create_table:
      self.db_tables.append(Table(query.name, query.columns))
    if query.token == token.insert_into:
      table_obj = self.get_table_object(query.table)
      if hasattr(query, 'columns'):
        table_obj.insert_with_columns(query.values, query.columns)
      else:
        table_obj.insert(query.values)

    if query.token == token.delete_from:
      where = []
      if query.where.token == token.op_and:
        for operand in query.where.operands:
          where.append(self.get_operand_values(operand))
      else:
        where.append(self.get_operand_values(query.where))

      table = self.get_table_object(query.table)
      table.remove(where)

    if query.token == token.update:
      where = []
      if query.where.token == token.op_and:
        for operand in query.where.operands:
          where.append(self.get_operand_values(operand))
      else:
        where.append(self.get_operand_values(query.where))

      table = self.get_table_object(query.table)
      table.update(where, query.set)

    if query.token == token.select:
      table_obj = self.get_table_object(query.from_table)

      # If it is a list, check if there is any operations in the select statement.
      # If there is a select statement, get the operand values
      if type(query.columns) is list:
        for idx, column in enumerate(query.columns):
          if type(column) is tuple:
            query.columns[idx] = (self.get_operand_values(column[0]), column[1])

      # TODO: DO STUFF WITH WHERE BEFORE THIS!!!!!!!!!!!!
      return table_obj.select(query.columns)

  def get_operand_values(self, operand):
    Query = namedtuple('Query', ['token', 'lh', 'rh'])
    if operand.token == token.op_and:
      to_return = []
      for op in operand.operands:
        to_return.append(self.get_operand_values(op))
      return to_return
    else:
      return Query(operand.token, operand.operands[0].identifier, operand.operands[1])

  def get_table_object(self, name):
    for table in self.db_tables:
      if table.get_table_name() == name:
        return table


class Table():
  def __init__(self, name, columns):
    self.content = []
    # None is standard value
    self.definition = namedtuple(name, columns, defaults=(None,) * len(columns))

  def insert(self, values):
    self.content.append(self.definition(*values))

  def insert_with_columns(self, values, columns):
    row = self.definition("a=hej")
    to_be_inserted = dict(zip(columns, values))
    self.content.append(self.definition(**to_be_inserted))

  def select(self, columns, where=None):

    # If we want to select specific columns
    if type(columns) is list:
      row_definition_names = []

      # Create a new namedtuple with the columns, if we get a tuple (AS), use the AS value
      for column in columns:
        if type(column) is tuple:
          row_definition_names.append(column[1])
        else:
          row_definition_names.append(column)
      row_definition = namedtuple('Row', row_definition_names)


      # Get the values from the table content
      return_list = []
      for row in self.content:
        d = {}
        for column in columns:
          # If the column if a tuple, we need to do the calculation accorind to the operand
          # and save it with the name of the AS value (column[1])
          if type(column) is tuple:
            if column[0].token == token.op_divide:
              d[column[1]] = getattr(row, column[0].lh[0]) / column[0].rh
          else:
            d[column] = getattr(row, column)

            # DO WHERE SHIT
        return_list.append(row_definition(**d))

      return return_list

    elif columns.token == token.star:
      return self.content

  def update(self, where, set_list):
    found_columns = {}

    # Go through all the querys
    for query in where:

      # Go through all the identifiers in lh
      for identifier in query.lh:
        # Go through all the saved values in this table
        for idx, column in enumerate(self.content):
          # Get the value for this identifier
          column_value = getattr(column, identifier)

          # Check if this condition matches
          matched_condition = False
          # IF EQUAL
          if query.token == token.op_equal:
            if column_value == query.rh:
              matched_condition = True
            
          # IF INFERIOR
          if query.token == token.op_inferior:
            if query.rh > column_value:
              matched_condition = True

          if matched_condition:
            if idx in found_columns:
              print("PLUS")
              found_columns[idx]["count"] += 1
            else:
              found_columns[idx] = {"count": 1}

    for key in found_columns:
      # SHOULD UPDATE
      if found_columns[key]["count"] == len(where):
        updated_row = self.content[key]._asdict()
        
        for t in set_list:
          updated_row[t[0]] = t[1]
        self.content[key] = self.definition(**updated_row)


  def remove(self, where):
    found_columns = {}

    # Go through all the querys
    for query in where:

      # Go through all the identifiers in lh
      for identifier in query.lh:
        # Go through all the saved values in this table
        for idx, column in enumerate(self.content):
          # Get the value for this identifier
          column_value = getattr(column, identifier)

          # Check if this condition matches
          matched_condition = False
          # IF EQUAL
          if query.token == token.op_equal:
            if column_value == query.rh:
              matched_condition = True
            
          # IF INFERIOR
          if query.token == token.op_inferior:
            if query.rh > column_value:
              matched_condition = True

          if matched_condition:
            if idx in found_columns:
              print("PLUS")
              found_columns[idx]["count"] += 1
            else:
              found_columns[idx] = {"count": 1}

    # Remove the columns that matched the conditions
    for key in found_columns:
      # SHOULD REMOVE
      if found_columns[key]["count"] == len(where):
        self.content.remove(self.content[key])

  def get_table_name(self):
    return self.definition.__name__

  def get_table_fields(self):
    return list(self.definition._fields)