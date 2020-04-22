from .header import * 

def pointer_array_count(heap, pointer):
  # Pointers are represented as integers, 10 integers = 40 bytes big. 40 / 4 = 10 integers = 10 pointers
  # 1 integer = 4 bytes big
  return header_get_size(heap, pointer) / 4

def pointer_array_get(heap, pointer, index):
  # Pointers are represented as integers, so to get it we have to get from the heap.
  # pointer + (index*4+4). *  4 because an integer is 4 bytes. + 4 because if we do index 0 we do not want to get the header
  # The header is at 0 - 4
  return int.from_bytes(heap[pointer+(index*4+4):pointer+(index*4+8)], byteorder='little')

def pointer_array_set(heap, pointer, index, value):
  originalValue = pointer_array_get(heap, pointer, index)

  # First set all where originalValue and value has a 1
  # Then set where (originalValue and value) or value has a 1
  newValue = originalValue & value  | value
  newValue = newValue.to_bytes(4, byteorder='little')

  heap[pointer+(index*4+4):pointer+(index*4+8)] = newValue

