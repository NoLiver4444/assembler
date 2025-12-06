#!/usr/bin/env python3
"""
Simple test for Stage 2
"""

import os

# Create test file with English comments
test_code = """# Test 1: Load constant 468
load 468

# Test 2: Read from memory offset 15
read 15

# Test 3: Write to memory address 224
write 224

# Test 4: Unary operation sgn
sgn
"""

# Write test file
with open('test_stage2.asm', 'w', encoding='utf-8') as f:
    f.write(test_code)

print("Created test_stage2.asm")
print("\nRunning assembler with test mode...")
print("-" * 50)

# Run assembler
os.system('python assembler.py test_stage2.asm test.bin --test')

print("\n" + "-" * 50)
print("Expected byte sequence from specification:")
print("0x4A, 0xD4, 0x01, 0x00, 0x00, 0x87, 0x0F, 0xD5, 0xE0, 0x00, 0x00, 0x00, 0x9A")

print("\nChecking binary file...")
with open('test.bin', 'rb') as f:
    data = f.read()
    hex_bytes = [f'0x{b:02X}' for b in data]
    print(f"Actual byte sequence: {', '.join(hex_bytes)}")

# Clean up
os.remove('test_stage2.asm')
os.remove('test.bin')