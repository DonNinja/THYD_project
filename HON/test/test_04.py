# Adapted from Programiz
# Program to check if a number is prime or not

num = 29

# To take input from the user
#num = int(input("Enter a number: "))

# define a flag variable
flag = False

# prime numbers are greater than 1
if num > 1:
    # check for factors
    i = 2
    while i < num:
        if (num % i) == 0:
            # if factor is found, set flag to True
            flag = True
            # break out of loop
            break
        i = i + 1

# check if flag is True
if flag:
    print(num, "is not a prime number")
else:
    print(num, "is a prime number")
