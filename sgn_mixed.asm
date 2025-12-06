# Test 2: mixed values
# Source: [10, -5, 0, 100, -128, 255]
# Byte values: [10, 251, 0, 100, 128, 255]
# Expected sgn: [1, -1, 0, 1, -1, -1]

# Initialize source
load 10
write 50

load 251   # -5 as unsigned byte
write 51

load 0
write 52

load 100
write 53

load 128   # -128 as unsigned byte
write 54

load 255   # -1 as unsigned byte
write 55

# Apply sgn
load 50
sgn
write 100

load 51
sgn
write 101

load 52
sgn
write 102

load 53
sgn
write 103

load 54
sgn
write 104

load 55
sgn
write 105