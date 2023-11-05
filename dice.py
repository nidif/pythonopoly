import random

current = 0
die1 = die2 = total = 0
rolls = 0

print("Feeling lucky punk? ")
roll = input("Enter Y to roll the dice or X to end ")

while roll.upper() != "X":
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    total = die1 + die2
    rolls += 1
    current = (current + total) % 40
    print('\nFirst roll is {0} and second roll is {1} for a total of {2}.'.format(die1, die2, total))
    roll = input("Enter Y to roll the dice again or X to end")

print("Thanks for rolling! You rolled a total of ", rolls, " times.")
