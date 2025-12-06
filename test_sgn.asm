# Запишем в память три значения:
#   data[10] = 0   → sgn = 0
#   data[11] = 50  → sgn = 1
#   data[12] = -10 → sgn = -1 (в байте: 246 = 0xF6)

# Запись 0
load 0
write 10

# Запись 50
load 50
write 11

# Запись -10 (в байте: 256 - 10 = 246)
load 246
write 12

# Теперь вычислим sgn для каждого и сохраним результаты в data[100], [101], [102]

# sgn(data[10]) → 0
load 10
sgn
write 100

# sgn(data[11]) → 1
load 11
sgn
write 101

# sgn(data[12]) → -1
load 12
sgn
write 102