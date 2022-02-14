'''
Code by Garrett Fosdick
Runs the wordle bot with user input.  This python script helps the user solve the daily wordle.  Enter the guess given to you by our wordle bot and then enter the corresponding key given to you by wordle.
For the wordle key, black = 0, yellow = 1, and green = 2.  Enter the key with no spaces in order.
'''

from wordle_solver import solve_wordle_no_ray

if __name__ == "__main__":
    solve_wordle_no_ray(prune_valid_words = False)