from .header import * 
from .pointers_array import *

# When we allocate something, it seems like it uses size + 4
# Should we set the size to size or size + 4? 
# Depending on what we set the size to we have to chane total_free_space and total_allocated_space
# to account for the 4 extra bytes.


class heap(object):
  # size: the size (in bytes) of the heap
  def __init__(self, size):
    self.data             = bytearray(size)
    # Set size of the heap
    header_set_size(self.data, 0, size-4)
    pass
  
  # return the index to the begining of a block with size (in bytes)
  def allocate(self, size):
    # The 4 first is the header
    pointer = 0
    best_fit = {
      'size': len(self.data),
      'pointer': -1
    }
    perfect_match = False


    while pointer < len(self.data) - 4:
      if header_get_used_flag(self.data, pointer) is False:
        currentSize = header_get_size(self.data, pointer)
        if currentSize < best_fit['size'] and size + 4 <= currentSize:
          best_fit['size'] = currentSize
          best_fit['pointer'] = pointer

        if currentSize == size:
          perfect_match = True
          best_fit['size'] = currentSize
          best_fit['pointer'] = pointer
          break

      pointer += header_get_size(self.data, pointer)+4

    if best_fit['pointer'] is not -1:
      # Set the size and used flag for the new block
      header_set_size(self.data, best_fit['pointer'], size)
      header_set_used_flag(self.data, best_fit['pointer'], True)

      # Set the size for the next block
      if perfect_match == False:
        # best_fit['size'] - size - 4
        header_set_size(self.data, best_fit['pointer']+size+4, best_fit['size'] - size - 4)



      #if header_get_used_flag(self.data, best_fit['pointer']+size+4) is not True and header_get_size(self.data, best_fit['pointer']+size+4) == 0:
      #  header_set_size(self.data, best_fit['pointer']+size+4, len(self.data)-4-best_fit['pointer']-size-4)


    return best_fit['pointer']
    """


    while True:
      if header_get_used_flag(self.data, pointer) is not True:
        print(header_get_size(self.data, pointer))
        # Set this block size and use
        header_set_size(self.data, pointer, size)
        header_set_used_flag(self.data, pointer, True)
        # Set the size for the next block
        if header_get_used_flag(self.data, pointer+size) is not True and header_get_size(self.data, pointer+size) == 0:
          header_set_size(self.data, pointer, len(self.data)-pointer-4)
        return pointer
      else:
        pointer += header_get_size(self.data, pointer)
        #print(pointer)
    """

  # 1 set_size(3)
  # 1
  # 1
  # 1
  # 1 size(2)
  # 1
  # 1
  #
  #
  # 1 size(2)
  # 1
  # 1
  
  # unallocate the memory at the given index
  def deallocate(self, pointer):
    size = header_get_size(self.data, pointer)
    header_set_used_flag(self.data, pointer, False)

    preBlock = {
      "pointer": 0,
      "size": -1,
      "used": True
    }

    # Get the previous block
    while preBlock['pointer'] != pointer and preBlock['pointer'] < len(self.data):
      preBlock['size'] = header_get_size(self.data, preBlock['pointer'])
      preBlock['used'] = header_get_used_flag(self.data, preBlock['pointer'])
      preBlock['pointer'] += header_get_size(self.data, preBlock['pointer']) + 4

    preBlock['pointer'] -= preBlock['size'] + 4


    # If the previous block is not used, change our pointer and size
    if preBlock["used"] == False:
      header_set_size(self.data, pointer, 0)
      pointer = preBlock['pointer']
      print("PREBLOOOOOOOOOOOOOOOOOOOOOOCK")
      size += preBlock['size'] + 4
      print(size)

      header_set_size(self.data, pointer, size)
    

    # If the next block is not used
    if header_get_used_flag(self.data, pointer+size+4) is False:
      nextBlockSize = header_get_size(self.data, pointer+size+4)
      header_set_size(self.data, pointer+size+4, 0)
      header_set_size(self.data, pointer, size+nextBlockSize+4)


  
  # Return the current total (allocatable) free space
  def total_free_space(self):
    # The 4 first is the header
    print("Hello, world")
    pointer = 0
    used_space = 0
    while pointer < len(self.data):
      if header_get_used_flag(self.data, pointer):
        used_space += header_get_size(self.data, pointer) + 4
      else:
        used_space += 4
      print("size:" + str(header_get_size(self.data, pointer)))
      pointer += header_get_size(self.data, pointer) + 4
      print(pointer)
    print("Free: " + str(len(self.data) - used_space))
    return len(self.data) - used_space

  # Return the current total allocated memory
  def total_allocated_space(self):
    pointer = 0
    allocated = 0
    while pointer < len(self.data):
      if header_get_used_flag(self.data, pointer):
        allocated += header_get_size(self.data, pointer)
      pointer += header_get_size(self.data, pointer) + 4

    print("Total_allocated space: " + str(allocated))
    return allocated

  def allocate_array(self, count):
    pointer = self.allocate(count * 4)
    header_mark_as_pointers_array(self.data, pointer)
    return pointer

  def allocate_bytes(self, count):
    pointer = self.allocate(count)
    header_mark_as_bytes_array(self.data, pointer)
    return pointer
