# -*- coding: utf-8 -*-
"""
Created on Sun May 12 20:24:01 2024

@author: Laptop
"""

import math
import concurrent.futures
import random
import numpy as np

def check_score(password, guess):
    """ Computes the number of pegs based on the password and guess """
    black_pegs = 0
    white_pegs = 0
    
    password_matched = [False] * 4
    guess_matched = [False] * 4
    
    for i in range(4):
        if guess[i] == password[i]:
            black_pegs += 1
            password_matched[i] = True
            guess_matched[i] = True
    
    for i in range(4):
        if not guess_matched[i]: 
            for j in range(4):
                if not password_matched[j] and guess[i] == password[j]:
                    white_pegs += 1
                    password_matched[j] = True
                    break  
    
    return [black_pegs, white_pegs]


class Mastermind:
    """This class is the game itself, containing the attemps, the passsword, the number of colors allowed,
    and has the ability to allow a "player" to play the game"""
    
    def __init__(self, password = None, n_attempts = 12, n_colors = 9):
        if password == None:
            self.password = self.generate_password(n_colors)
        else:
            self.password = password
        self.attempts = []
        self.n_attempts = n_attempts
        self.n_colors = n_colors
        
    def get_nguesses(self):
        return len(self.attempts)

    def generate_password(self, n_colors):
        return [random.randint(0, n_colors - 1) for _ in range(4)]

    def check_guess(self, guess):
        """Checks a guess by returns the number of pegs that are computed"""
        
        return check_score(self.password, guess)
    
    def print_attempts(self):
        print("Attempts:")
        for attempt, score in self.attempts:
            print("Guess:", attempt, "Score:", score)
        print("Password:", self.password)

    def play_round(self, guess):
        result = self.check_guess(guess)
        self.attempts.append((guess, result))
        return result
    
    def is_game_over(self):
        if (self.password, [4, 0]) in self.attempts:
                return True, True
        if self.get_nguesses() >= self.n_attempts:
            return True, False
        return False, None
    
class Real_Player:
    """Allows a human to play the game by interacting with the console"""
    
    def __init__(self, n_colors = 9):
        self.attempts = []
        if n_colors != 9:
            raise TypeError
        print('Get ready to guess')

    def next_guess(self):
        """Allows the human player to input their next guess
        Also allows for the "help" command to be inputed"""
        
        color_map = {
            "hole": 0,
            "red": 1,
            "blue": 2,
            "green": 3,
            "yellow": 4,
            "orange": 5,
            "pink": 6,
            "white": 7,
            "grey": 8 
        }
        guess_input = input("Enter your guess (4 colors or numbers separated by spaces, e.g., 'red blue green yellow' or '0 1 2 ... 8'): ").split()
        print(guess_input)
        if guess_input == ['help']:
            return guess_input[0]
        for color in guess_input: 
            if color not in color_map and not color.isdigit() :
                raise TypeError
        guess = [color_map[color] if color in color_map else int(color) \
                 for color in guess_input]
        return guess

    def add_result(self, guess, result):
        """Adds and also prints the result of the previous guess"""
        
        self.attempts.append((guess, result))
        print(f'Your guess({guess}) had a result of {result}')
        
class AI:
    """Represent an AI agent capable of playing the game very efficiently using the concept of entorpy"""
    
    def __init__(self, n_colors):
        self.n_colors = n_colors
        self.attempts = []
        self.possible_results = []
        self.combinations = []
        self.entropies = []
        self.n_pos_res = 0
        self.n_combinations = 0
        self.prepare_combinations()
        self.prepare_pos_result()
            
    def prepare_combinations(self):
        """Creates a list that contains all the possible passwords"""
        
        entropies = []
        combinations = []
        for i in range(self.n_colors):
            for j in range(self.n_colors):
                for k in range(self.n_colors):
                    for l in range(self.n_colors):
                        new_entry = [i,j,k,l]
                        combinations.append(new_entry)
                        entropies.append(0)
        self.combinations = combinations
        self.n_combinations = len(self.combinations)
        self.entropies = entropies
        
    def prepare_pos_result(self):
        """Creates a list that contains all the possible results (black and white peg combinations)"""
        
        results = []
        for i in range(4):
            for j in range(4):
                if i + j <= 4 :
                    results.append([i,j])
        self.possible_results = results
        self.n_pos_res = len(self.possible_results)
        
    def coordinate_to_value(self, coordinate):
        """Maps a result (black and white peg combination) to a number for the sake of convenience"""
        
        mapping = {
            (0, 0): 0, (0, 1): 1, (0, 2): 2, (0, 3): 3, (0, 4): 4,
            (1, 0): 5, (1, 1): 6, (1, 2): 7, (1, 3): 8,
            (2, 0): 9, (2, 1): 10, (2, 2): 11,
            (3, 0): 12, (4, 0): 13
        }
        return mapping.get(tuple(coordinate), None)
        
    def compute_entropy_guess(self,guess_inx):
        """Computes the entropy of a single guess"""
        
        counts = []
        for i in range(15):
            counts.append(0)
        for combination in self.combinations:
            score = check_score(combination, self.combinations[guess_inx])
            counts[self.coordinate_to_value(score)] += 1
        probabilities = [x / self.n_combinations for x in counts]
        if np.sum(counts) != self.n_combinations:
            raise TypeError 
        self.entropies[guess_inx] = self.compute_entropy(probabilities)
        
    
    def compute_entropy(self, probabilities):
        """Computes the entropy of a list of probabilities."""
        if not probabilities:
            return 0
        
        probabilities = np.array(probabilities)  
        entropy = 0
        non_zero_indices = np.where(probabilities > 0)[0]  
        entropy = np.sum(-probabilities[non_zero_indices] * np.log2(probabilities[non_zero_indices])) 
        
        return float(entropy) 
        
    def next_guess(self):
        """Computes the next guess"""
        
        for i in range(self.n_combinations):
            self.compute_entropy_guess(i)
            # if i % 1000 == 0 :
            #     print(i)
        # print(self.entropies)
        return self.combinations[self.entropies.index(max(self.entropies))]
    
    def update_combinations(self):
        """Updates the list containing all the possible passwords"""
        
        attempt, score = self.attempts[-1]
        new_combinations = []
        for combination in self.combinations:
            if score == check_score(combination, attempt):
                new_combinations.append(combination)
        self.combinations = new_combinations
        self.n_combinations = len(self.combinations)
        self.entropies = [0] * self.n_combinations
        
    
    def add_result(self, guess, result):
        self.attempts.append((guess,result))
        self.update_combinations()
        

def game(Agent, password = None, n_attempts = 9, n_colors = 9, verbose = True):
    """Simple loop automatizing the playing of the game"""
    
    game = Mastermind(password = password, n_attempts = n_attempts, n_colors = n_colors)
    agent = Agent(n_colors)
    win = None
    while True:
        guess = agent.next_guess()
        if guess == 'help':
            game.print_attempts()
            continue
        result = game.play_round(guess)
        agent.add_result(guess, result)
        game_state, winner = game.is_game_over()
        if game_state:
            if winner:
                win = True
                if verbose:
                    print('Game Over!\n')
                    print('Player Wins!')
            else:
                win = False
                if verbose:
                    print('Game Over!\n')
                    print('Player Loses!\n :(\n')
                    game.print_attempts()
            return win, len(agent.attempts)

def loop(Agent, password = None, n_attempts = 9, n_colors = 9, verbose = False, nb_tries = 100):
    """Loops the previous function in order to compute the average round it takes to guess as well as the worst case scenario"""
    
    results = []
    all_won = True
    for i in range(nb_tries):
        res = game(Agent, password, n_attempts, n_colors, verbose)
        results.append(res[1])
        if not res[0]:
            all_won = False
        if i % 10 == 0 :
            print(i)
    if not all_won:
        print("At least one game was lost\n")
    return max(results), sum(results)/len(results)

#game = Mastermind()
#agent = AI()
#guess = agent.next_guess()
