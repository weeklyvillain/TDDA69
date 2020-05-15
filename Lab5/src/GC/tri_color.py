from .header import * 
from .pointers_array import *

class tri_color(object):
  def __init__(self, heap):
    self.heap = heap
  # This function should collect the memory in the heap
  def collect(self):
    white_set = []
    # Skip the root object
    pointer = header_get_size(self.heap.data, 0)
    # Initialize the white set with all objects except the root
    while pointer < len(self.heap.data):
      white_set.append(pointer)
      pointer += header_get_size(self.heap.data, pointer) + 4

    # Initialize black set
    black_set = []
    # Initialize gray set
    gray_set = [0]
    
    # Go through all the objects in the gray_set
    while len(gray_set) > 0:
      # Move the first object in gray_set to black_set
      current_pointer = gray_set.pop()
      black_set.append(current_pointer)

      # Get all the indexes for this object
      indexes = int(header_get_size(self.heap.data, current_pointer) / 4)
      for i in range(0, indexes):
          # Get the pointer to the object at index i in the array
          nextPointer = pointer_array_get(self.heap.data, current_pointer, i)
          # If nextPointer is in the white_set, remove it and add it to the gray_set
          if nextPointer in white_set:
            white_set.remove(nextPointer)
            gray_set.append(nextPointer)

    # Everything that is in the white_set can be disallocated, so set it to not used.
    for pointer in white_set:
      header_set_used_flag(self.heap.data, pointer, False)

