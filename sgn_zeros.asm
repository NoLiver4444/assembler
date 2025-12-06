# Test 1: all zeros
# Source: data[50..55] = [0, 0, 0, 0, 0, 0]
# Expected result: [0, 0, 0, 0, 0, 0]

# Initialize source
load 0
write 50
load 0
write 51
load 0
write 52
load 0
write 53
load 0
write 54
load 0
write 55

# Apply sgn and store result
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