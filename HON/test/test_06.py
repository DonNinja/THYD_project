# Adapted from Programiz
# Program to add two matrices using nested loop
X = [[12,7,3],
    [4 ,5,6],
    [7 ,8,9]]

Y = [[5,8,1],
    [6,7,3],
    [4,5,9]]

result = [[0,0,0],
         [0,0,0],
         [0,0,0]]

# iterate through rows
i = 0
while i < len(X):
    # iterate through columns
    j = 0
    while j < len(X[0]):
        result[i][j] = X[i][j] + Y[i][j]
        j = j + 1
    i = i + 1

i = 0
while i < len(X):
    print(result[i])
    i = i + 1
