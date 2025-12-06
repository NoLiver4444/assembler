# Initialize source array at addresses 50-54
load 10
write 50

load 20
write 51

load 30
write 52

load 40
write 53

load 50
write 54

# Copy to destination 100-104
load 50
read 0
write 100

load 51
read 0
write 101

load 52
read 0
write 102

load 53
read 0
write 103

load 54
read 0
write 104