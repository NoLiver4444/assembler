# Simple UVM program
# Load constant 100 to stack
load 100

# Read value from memory at address 100+5=105
read 5

# Load value 42
load 42

# Write it to address 200
write 200

# Check sign of value at address 150
load 150
sgn
