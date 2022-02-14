'''
Code by Garrett Fosdick
Runs all possible wordle games and gathers stats on bot performance.
'''

from wordle_solver import clean_word_list, solve_wordle
import matplotlib.pyplot as plt
import ray

if __name__ == "__main__":
    ray.init()
    #Loads all possbile correct wordle words.
    with open("./wordle-word-answers.txt", 'r') as file:
        data = file.read()
        temp1 = data.split("[")
        static_correct_words = temp1[1].split("]")[0].split(",")
        static_correct_words = clean_word_list(static_correct_words)

    game_wins = [0, 0, 0, 0, 0, 0, 0]
    #Submits tasks with threading for speedy completion.
    task_ref_list = []
    for static_word in static_correct_words:
        task_ref_list.append(solve_wordle.remote(secret_word = static_word, prune_valid_words = False))
    #Retrieves results of threaded tasks.
    for ref in task_ref_list:
        #Increments the number of wins.
        game_wins[ray.get(ref)] += 1

    print(game_wins)
    fig = plt.figure()
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
    time = ["One", "Two", "Three", "Four", "Five", "Six", "Loss"]
    ax.bar(time, game_wins)
    plt.show()