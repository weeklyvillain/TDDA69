from .header import * 
from .pointers_array import *

class mark_sweep(object):
  def __init__(self, heap):
    self.heap = heap
  # This function should collect the memory in the heap
  def collect(self):
    pointer = 0
    # Set all flags to False (Step 1)
    while pointer < len(self.heap.data):
      header_set_used_flag(self.heap.data, pointer, False)
      pointer += header_get_size(self.heap.data, pointer) + 4

    #Start collect at root
    self.__rec_collect(0)

  def __rec_collect(self, pointer):
    # Set this object to used
    header_set_used_flag(self.heap.data, pointer, True)


    # Only loop through if this object is an pointer array
    if header_is_pointers_array(self.heap.data, pointer):
      # Get the indexes for this object (the size of the array)
      indexes = int(header_get_size(self.heap.data, pointer) / 4)
      for i in range(0, indexes):
          # Get the pointer to the object at index i in the array
          nextPointer = pointer_array_get(self.heap.data, pointer, i)
          # If we havn't marked this object yet, mark it (recursive)
          if not header_get_used_flag(self.heap.data, nextPointer):
            self.__rec_collect(nextPointer)
