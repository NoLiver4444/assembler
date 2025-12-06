# Test 1: Load constant 468 (0x1D4)
# Expected: 0x4A, 0xD4, 0x01, 0x00, 0x00
load 468

# Test 2: Read from memory offset 15
# Expected: 0x87, 0x0F
read 15

# Test 3: Write to memory address 224
# Expected: 0xD5, 0xE0, 0x00, 0x00, 0x00
write 224

# Test 4: Unary operation sgn
# Expected: 0x9A
sgn