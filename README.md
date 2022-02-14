Code By Garrett Fosdick 
Credit to tabatkins for providing a word list for wordle: https://github.com/tabatkins/wordle-list/commit/ae0403f957ae7312d72929403432becc0b0f5d63

# WordleBot
An entropy bot that will solve a game of Wordle!  Average guess of 3.5 with no losses.

Install: 
-Make sure to be running python 3.8. Newer version are likely to work as well, but the code was made and tested with 3.8. 
-Install ray and matplotlib. Depending on how your python is set up either run: 
  python3.8 -m pip install ray 
  python3.8 -m pip install matplotlib 
Or: 
  python -m pip install ray 
  python -m pip install matplotlib -You are good to go!

Contents: daily_solver_wordle.py: This python script helps the user solve the daily wordle. Enter the guess given to you by our wordle bot and then enter the corresponding key given to you by wordle. For the wordle key, black = 0, yellow = 1, and green = 2. Enter the key with no spaces in order. Example Green, Yellow, Black, Black, Yellow would be entered as 21001.

full_dictionary_wordle.py: This python script will make the wordle bot automatically play all 2350 possible wordle games. (This takes a few minutes.) Once the run is done, it will produce a graph of the number of games that ended in a set number of guesses.

wordle_solver.py: This is where the majority of the code exists. The actual wordle solving code exists here and the other scripts just make use of it.
