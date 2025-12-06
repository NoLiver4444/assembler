# Test 3: all negatives
# Values: [-1, -2, -3, -4, -5, -6]
# Bytes: [255, 254, 253, 252, 251, 250]
# Expected sgn: [-1, -1, -1, -1, -1, -1]

# Initialize
load 255
write 50
load 254
write 51
load 253
write 52
load 252
write 53
load 251
write 54
load 250
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