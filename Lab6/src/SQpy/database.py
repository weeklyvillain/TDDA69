from .ast import token, ast
from collections import namedtuple
import sys
Query = namedtuple('Query', ['token', 'lh', 'rh'])


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
      print(query.columns)
      if type(query.columns) is list:
        for idx, column in enumerate(query.columns):
          if type(column) is tuple:
            print(column[1])
            query.columns[idx] = (self.get_operand_values(column[0]), column[1])

      where = None
      if hasattr(query, "where"):
        where = self.get_operand_values(query.where)

      joinedColumns = []
      listOfJoins = []

      # If we should join
      if hasattr(query, "joins"):
        newTable = table_obj
        i = 0
        # Join all the tables from the query.join
        for join in query.joins:
          join_table = self.get_table_object(join.table)
          newTable = newTable.join((join_table, self.get_operand_values(join.on)), i == 0)
          i += 1
        table_obj = newTable
      
      return table_obj.select(query.columns, where)



  def get_operand_values(self, operand):
    if operand.token == token.op_and:
      to_return = []
      for op in operand.operands:
        to_return.append(self.get_operand_values(op))
      return to_return
    elif operand.token == token.fn_count or operand.token == token.fn_avg:
      return Query(operand.token, operand.field, None)
    
    elif operand.token == token.identifier:
      print(operand.identifier)
      if len(operand.identifier) > 1:
        return ['_'.join(operand.identifier)]
      return operand.identifier

    elif operand.token == token.op_divide or operand.token == token.op_equal:
      opLeft = operand.operands[0]
      opRight = operand.operands[1]
      if isinstance(operand.operands[0], ast):
        opLeft = self.get_operand_values(operand.operands[0])
      if isinstance(operand.operands[1], ast):
        opRight = self.get_operand_values(operand.operands[1])

      return Query(operand.token, opLeft, opRight)


    else:
      return Query(operand.token, operand.operands[0].identifier, operand.operands[1])

  def get_table_object(self, name):
    for table in self.db_tables:
      if table.get_table_name() == name:
        return table


class Table():
  def __init__(self, name, columns):
    print(sys.version)
    self.content = []
    self.name = name
    self.columns = columns
    # None is standard value
    self.definition = namedtuple(name, columns, defaults=(None,) * len(columns)) # Python 3.7
    #self.definition = namedtuple(name, columns) # Python 3.6
    #self.definition.__new__.__default__ = (None,) * len(self.definition._fields) #python 3.6

  def insert(self, values):
    self.content.append(self.definition(*values))

  def insert_with_columns(self, values, columns):
    to_be_inserted = dict(zip(columns, values))
    self.content.append(self.definition(**to_be_inserted))

  def join(self, table, shouldSplit=True):
    query = table[1]
    joinedTables = []
    fields = []
    # Make the new fields for the new joined table
    # This is for the other table (not self)
    for field in table[0].definition._fields:
      fields.append(table[0].name + "_" + field)
    # This is for this (self) table, if we shouldn't split (more than one join), we only append the field so we don't get multiple self.name in the field names.
    for field in self.definition._fields:
      if shouldSplit:
        fields.append(self.name + "_" + field)
      else:
        fields.append(field)


    # Create the new table
    newTable = Table("joinedTable", fields)

    # Go over all the rows in this (self) table and in the other table that we are joining with
    for row in self.content:
      for row2 in table[0].content:
        # If we should perform an equal
        if query.token == token.op_equal:
          # If we should split the table names (if we are running more then one join), split the names on the delimiter '_'
          if shouldSplit:
            lhColumns = query.lh[0].split('_')
            rhColumns = query.rh[0].split('_')
          else:
            lhColumns = [query.lh[0].split('_')[0]] + query.lh
            rhColumns = [''] + query.rh
          # Needed to know if the table name is at the left or at the right of the lhColumns array
          if lhColumns[0] == self.name:
            # Split the rh query since row2 (which rhColumns is only used on) is not joined on before, and won't include any '_'
            rhColumns = query.rh[0].split('_')
            # If the two attributes are equal, insert them to the new table
            if getattr(row, lhColumns[1]) == getattr(row2, rhColumns[1]):
              newTable.insert([*(row2 + row)])
          else:
            # Split the lh query since row2 (which lhColumns is only used on) is not joined on before, and won't include any '_'
            lhColumns = query.lh[0].split('_')
            # If the two attributes are equal, insert them to the new table
            if getattr(row, rhColumns[1]) == getattr(row2, lhColumns[1]):
              newTable.insert([*(row2 + row)])
    return newTable


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
      counts = {}
      avgs = {}
      for row in self.content:
        d = {}
        should_append = True

        # Do the where statement if it exist
        if where is not None:
          if where.token == token.op_superior:
            # If the where statement is false, skip this row
            if getattr(row, where.lh[0]) <= where.rh:
              continue

        for column in columns:
          # If the column if a tuple, we need to do the calculation accorind to the operand
          # and save it with the name of the AS value (column[1])
          if type(column) is tuple:
            # If it is AS without a Query object (without a token)
            if isinstance(column[0], list):
              d[column[1]] = getattr(row, column[0][0])

            elif isinstance(column[0], str):
              d[column[1]] = getattr(row, column[0])

            elif column[0].token == token.op_divide:
              if isinstance(column[0].rh, list):
                d[column[1]] = getattr(row, column[0].lh[0]) / getattr(row, column[0].rh[0])
              else:
                d[column[1]] = getattr(row, column[0].lh[0]) / column[0].rh
              # If it is a count expression
            elif column[0].token == token.fn_count:
              should_append = False
              # If the AS (column[1]) is already saved in the list containing all the counts, do a + 1 on it.
              if column[1] in counts:
                counts[column[1]] = counts[column[1]]+1
                # If the AS (column[1]) is not saved in it, initialize it with the value 1
              else:
                counts[column[1]] = 1
                # If it is a average expressiom
            elif column[0].token == token.fn_avg:
              should_append = False
              # If the AS (column[1]) is already saved in the avg, append this value to the avgs list
              if column[1] in avgs:
                avgs[column[1]].append(getattr(row, column[0].lh))
                # If the AS (column[1]) is not saved in it, initialize it with a list containing this value
              else:
                avgs[column[1]] = [getattr(row, column[0].lh)]
          else:
            d[column] = getattr(row, column)

        if should_append:
          return_list.append(row_definition(**d))



      # Create new rows for the count and/or the average values
      row = {}
      for key, value in counts.items():
        row[key] = value
      for key, valueList in avgs.items():
        row[key] = sum(valueList) / len(valueList)
      
      # Append the new row to the returnList
      if row:
        return_list.append(row_definition(**row))

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