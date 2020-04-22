def header_get_garbage_flag(heap, pointer):
  return 0x80000000 & int.from_bytes(heap[pointer:pointer+4], byteorder='little') != 0

def header_set_garbage_flag(heap, pointer, value):
  header = int.from_bytes(heap[pointer:pointer+4], byteorder='little')
  if value:
    # 100000000.....
    # | means OR, so either the bits in the header variable or in the right value (10000000....)
    header = header | 0x80000000
  else:
    #011111111111111......
    # & means AND, so both the bit in header and the right value (01111...) has to be set for it to be 1.
    header = header & ~0x80000000
  header = header.to_bytes(4, byteorder='little')
  heap[pointer:pointer+4] = header

def header_get_used_flag(heap, pointer):
  return 0x40000000 & int.from_bytes(heap[pointer:pointer+4], byteorder='little') != 0
  
def header_set_used_flag(heap, pointer, value):
  header = int.from_bytes(heap[pointer:pointer+4], byteorder='little')
  if value:
    # 100000000.....
    # | means OR, so either the bits in the header variable or in the right value (10000000....)
    header = header | 0x40000000
  else:
    #011111111111111......
    # & means AND, so both the bit in header and the right value (01111...) has to be set for it to be 1.
    header = header & ~0x40000000
  header = header.to_bytes(4, byteorder='little')
  heap[pointer:pointer+4] = header

def header_is_pointers_array(heap, pointer):
  return 0x20000000 & int.from_bytes(heap[pointer:pointer+4], byteorder='little') != 0

  
def header_mark_as_pointers_array(heap, pointer):
  header = int.from_bytes(heap[pointer:pointer+4], byteorder='little')
  header = header | 0x20000000
  header = header.to_bytes(4, byteorder='little')
  heap[pointer:pointer+4] = header

def header_mark_as_bytes_array(heap, pointer):
  header = int.from_bytes(heap[pointer:pointer+4], byteorder='little')
  header = header & ~0x20000000
  header = header.to_bytes(4, byteorder='little')
  heap[pointer:pointer+4] = header
  
def header_get_size(heap, pointer):
  header = int.from_bytes(heap[pointer:pointer+4], byteorder='little')
  return header & 0x1FFFFFFF


def header_set_size(heap, pointer, size):
  header = int.from_bytes(heap[pointer:pointer+4], byteorder='little')

  header = header & ~0x1FFFFFFF | (0x1FFFFFFF & size)
  header = header.to_bytes(4, byteorder='little')
  heap[pointer:pointer+4] = header
