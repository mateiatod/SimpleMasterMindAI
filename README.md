# SimpleMastermindAI
A simple program that utilizes "entropy" to find the next guess.

The function "game" can be used to start a game; it takes in as arguments: 
agent (the agent that will play the game, ie "AI" or "Real_Player")
password (if set to None, it will choose a password randomly)
n_colors (number of types of colors that the password can contain)
verbose 

One can also use the function "loop" to check how well the agent performs. Takes in similar arguments with the addition of:
nb_tries (the number of times the game function is called)
