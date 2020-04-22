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
    pointer = 4

    while True:
      if header_get_used_flag(self.data, pointer) is not True:
        print(header_get_size(self.data, pointer))
        header_set_size(self.data, pointer, size)
        header_set_used_flag(self.data, pointer, True)
        return pointer
      else:
        pointer += header_get_size(self.data, pointer)
        #print(pointer)
  
  # unallocate the memory at the given index
  def deallocate(self, pointer):
    pass
  
  # Return the current total (allocatable) free space
  def total_free_space(self):
    # The 4 first is the header
    pointer = 4
    used_space = 4
    while pointer < len(self.data) and header_get_size(self.data, pointer) != 0:
      if header_get_used_flag(self.data, pointer):
        used_space += header_get_size(self.data, pointer) + 4
      pointer += header_get_size(self.data, pointer)
      print(pointer)
    print("Free: " + str(len(self.data) - used_space))
    return len(self.data) - used_space

  # Return the current total allocated memory
  def total_allocated_space(self):
    print("Total_allocated space: " + str(len(self.data) - self.total_free_space() - 4))
    return len(self.data) - self.total_free_space() - 4

  def allocate_array(self, count):
    pointer = self.allocate(count * 4)
    header_mark_as_pointers_array(self.data, pointer)
    return pointer

  def allocate_bytes(self, count):
    pointer = self.allocate(count)
    header_mark_as_bytes_array(self.data, pointer)
    return pointer
