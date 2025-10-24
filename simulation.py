import numpy as np
from models import Game

if __name__ == '__main__':
    num_iterations = int(1e6)

    player_one_wins = 0
    player_two_wins = 0
    player_one_scores = []
    player_two_scores = []
    num_rounds_list = []
    for i in range(num_iterations):
        game = Game()
        if i % (num_iterations / 100) == 0:
            print(f"{i / (num_iterations / 100)}%")
        winner, player_one_hand, player_one_score, player_two_hand, player_two_score, num_rounds = game.start(random_state=i)
        if winner == 0:
            player_one_wins += 1
        else:
            player_two_wins += 1
        player_one_scores.append(player_one_score)
        player_two_scores.append(player_two_score)
        num_rounds_list.append(num_rounds)
    print(player_one_wins)
    print(player_two_wins)
    print(np.mean(num_rounds_list))
