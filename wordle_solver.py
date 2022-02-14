import ray
import math

valid_wordle_keys = "012"

def clean_word_list(word_list):
    '''
    The word list has some garbage characters on the front and back.  This just strips those off.
    '''
    clean_list = []
    for word in word_list:
        clean_list.append(word.strip().strip("\""))
    return clean_list

def create_wordle_key(v, c):
    '''
    v: guessed word (pull from Valid words.)
    c: secret word (pull from Corret words.)
    The wordle key is the string of letter colors given for each guess.
    We use these keys to group the words.  Entropy is calculated based on group sizes.
    '''
    key = list("00000")
    #  Correct Position Pass
    correct_letters = {}
    for idx in range(5):
        if v[idx] == c[idx]:
            if v[idx] in correct_letters:
                correct_letters[v[idx]].append(idx)
            else:
                correct_letters[v[idx]] = [idx]
            key[idx] = "2"
    #  Correct Letter Pass
    for idx in range(5):
        if key[idx] != "2":
            if v[idx] in c:
                #  There are some weird interactions when there are multiple copies of the same letter.
                #  The reason this section of code might seem more complicated than you might expect is because of that.
                v_count = v[:idx].count(v[idx])
                c_count = c.count(v[idx])
                correct_count = 0
                if v[idx] in correct_letters:
                    correct_count = 0
                    for cor_idx in correct_letters[v[idx]]:
                        if cor_idx > idx:
                            correct_count += 1
                if v_count + correct_count < c_count:
                    key[idx] = "1"
    return key

def trim_dictionary_by_key(guess, guess_key, dictionary):
    '''
    Trims dictionary of words that would not provide the associated wordle key given the guess.
    '''
    new_dictionary = []
    for word in dictionary:
        iter_key = create_wordle_key(guess, word)
        if iter_key == guess_key:
            new_dictionary.append(word)
    return new_dictionary

@ray.remote(num_cpus=1)
def solve_wordle(secret_word = None, prune_valid_words = False):
    '''
    secret_word:  The word wordle bot is solving for.  If given the wordle bot will run automatically.  If None is given, wordle bot will ask for user inputs.
    prune_valid_words:  Sometimes guessing words you know are incorrect to gather info is the better strategy.  However this makes things run longer as there are more words to go through.
    Turn on prune_valid_words for better performance but slightly worse results.

    Returns the amount of guesses it took to win the provided game.
    '''
    #  Loads all words that may possibly be the secret word. (correct_words).
    #  Loads all words that are valid guesses. (valid_words).
    #  Only commonly used 5 letter words can be the secret word, but uncommon words are still accepted as guesses.
    with open("./wordle-word-answers.txt", 'r') as file:
        data = file.read()
        temp1 = data.split("[")
        correct_words = temp1[1].split("]")[0].split(",")
        correct_words = clean_word_list(correct_words)
        valid_words = temp1[2].split("]")[0].split(",")
        valid_words = clean_word_list(valid_words)
        valid_words += correct_words
    game_won = False
    word_to_guess = secret_word
    print("==================================================================")
    if word_to_guess:
        print("Correct Word: " + word_to_guess)
    else:
        print("Correct word is unkown.")
    #  soare is the word we calculated to have the highest entropy from the beginning game state.
    #  To save on resources, we have it automatically guess soare first instead of calculating that it should use soare.
    #  Fun fact: Soare is a young hawk.
    guess = "soare"

    for guess_iteration in range(6):
        print("-----------------------------------------------------------------------")
        print("Guessing: " + guess)
        if guess == word_to_guess:
            print("YOU WIN ON ITERATION: " + str(guess_iteration + 1))
            return guess_iteration
        if secret_word:
            guess_key = create_wordle_key(guess, word_to_guess)
        else:
            guess_key = list(input("Entere Wordle Key: (Green = 2, Yellow = 1, Black = 0)"))
        #  Word lists are pruned to represent the limiting of options as we gather more information.
        #  I disabled these lines of code as it is a bit noisy.  Re-enable these if you want more info on how pruned the word lists are becoming with each step.
        if prune_valid_words:
            valid_words = trim_dictionary_by_key(guess, guess_key, valid_words)
        correct_words = trim_dictionary_by_key(guess, guess_key, correct_words)

        #  Guessing is based on entropy of the words typically.  However there are two exceptions.  If there is only one correct word left we just force the last word to be guessed.
        #  If there are only two correct words reamining, it is possible a non-correct but still valid word will provide the same entropy as one of the correct words.
        #  Because of this we force it to use one of the correct words which will provide the same entropy but also end the game faster.
        if len(correct_words) == 1:
            guess = correct_words[0]
            continue
        elif len(correct_words) == 2:
            valid_words = correct_words

        #  Calculates the entropy of every possible guess.
        #  Only records the word with the current best entropy.
        total_correct_words = len(correct_words)
        best_word = ""
        best_group_worth = 0
        for v in valid_words:
            dictionary_word_groups = {}
            for c in correct_words:
                key = create_wordle_key(v, c)
                key = "".join(key)
                if key in dictionary_word_groups:
                    dictionary_word_groups[key] += 1
                else:
                    dictionary_word_groups[key] = 1
            word_worth = 0
            for key in dictionary_word_groups:
                group_count = dictionary_word_groups[key]
                probability = group_count/total_correct_words
                word_worth += -probability * math.log2(probability)

            if word_worth > best_group_worth:
                best_group_worth = word_worth
                best_word = v
        guess = best_word
    if not game_won:
        return 6

def solve_wordle_no_ray(secret_word = None, prune_valid_words = False):
    '''
    This is the exact same function as above except it does not use ray and thus can not be used with threading.
    User inputs do not work well with threading, and is intended to be used with the daily solver.

    secret_word:  The word wordle bot is solving for.  If given the wordle bot will run automatically.  If None is given, wordle bot will ask for user inputs.
    prune_valid_words:  Sometimes guessing words you know are incorrect to gather info is the better strategy.  However this makes things run longer as there are more words to go through.
    Turn on prune_valid_words for better performance but slightly worse results.

    Returns the amount of guesses it took to win the provided game.
    '''
    #  Loads all words that may possibly be the secret word. (correct_words).
    #  Loads all words that are valid guesses. (valid_words).
    #  Only commonly used 5 letter words can be the secret word, but uncommon words are still accepted as guesses.
    with open("./wordle-word-answers.txt", 'r') as file:
        data = file.read()
        temp1 = data.split("[")
        correct_words = temp1[1].split("]")[0].split(",")
        correct_words = clean_word_list(correct_words)
        valid_words = temp1[2].split("]")[0].split(",")
        valid_words = clean_word_list(valid_words)
        valid_words += correct_words
    game_won = False
    word_to_guess = secret_word
    print("==================================================================")
    if word_to_guess:
        print("Correct Word: " + word_to_guess)
    else:
        print("Correct word is unkown.")
    #  soare is the word we calculated to have the highest entropy from the beginning game state.
    #  To save on resources, we have it automatically guess soare first instead of calculating that it should use soare.
    #  Fun fact: Soare is a young hawk.
    guess = "soare"

    for guess_iteration in range(6):
        print("-----------------------------------------------------------------------")
        if secret_word is None:
            print("Please enter the following guess into wordle and then enter the key you recieve.")
        print("Guessing: " + guess)
        if secret_word:
            guess_key = create_wordle_key(guess, word_to_guess)
        else:
            while True:
                guess_key = list(input("Entere Wordle Key: (Green = 2, Yellow = 1, Black = 0)"))
                if len(guess_key) == 5 and all(elem in valid_wordle_keys for elem in guess_key):
                    break
                else:
                    print("Invalid input.  Do not use spaces and make sure to only use 5 numbers.  The wordle key is the colors you get back after your guess.")
        if guess_key == ['2', '2', '2', '2', '2']:
            print("YOU WIN ON ITERATION: " + str(guess_iteration + 1))
            return guess_iteration
        if prune_valid_words:
            print("Previous valid_word count = " + str(len(valid_words)))
            valid_words = trim_dictionary_by_key(guess, guess_key, valid_words)
            print("Current valid_word count = " + str(len(valid_words)))
        print("Previous possible correct_word count = " + str(len(correct_words)))
        correct_words = trim_dictionary_by_key(guess, guess_key, correct_words)
        print("Current possible correct_word count = " + str(len(correct_words)))

        #  Guessing is based on entropy of the words typically.  However there are two exceptions.  If there is only one correct word left we just force the last word to be guessed.
        #  If there are only two correct words reamining, it is possible a non-correct but still valid word will provide the same entropy as one of the correct words.
        #  Because of this we force it to use one of the correct words which will provide the same entropy but also end the game faster.
        if len(correct_words) == 1:
            guess = correct_words[0]
            continue
        elif len(correct_words) == 2:
            valid_words = correct_words

        #  Calculates the entropy of every possible guess.
        #  Only records the word with the current best entropy.
        total_correct_words = len(correct_words)
        best_word = ""
        best_group_worth = 0
        for v in valid_words:
            dictionary_word_groups = {}
            for c in correct_words:
                key = create_wordle_key(v, c)
                key = "".join(key)
                if key in dictionary_word_groups:
                    dictionary_word_groups[key] += 1
                else:
                    dictionary_word_groups[key] = 1
            word_worth = 0
            for key in dictionary_word_groups:
                group_count = dictionary_word_groups[key]
                probability = group_count/total_correct_words
                word_worth += -probability * math.log2(probability)

            if word_worth > best_group_worth:
                best_group_worth = word_worth
                best_word = v
        guess = best_word
    if not game_won:
        return 6

