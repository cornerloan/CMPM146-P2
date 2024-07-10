import p2_t3
import mcts_vanilla
import mcts_modified
import mcts_parallel
import random_bot
import rollout_bot
import plotter
from mcts_vanilla import num_nodes

players = dict(
    random_bot=random_bot.think,
    rollout_bot=rollout_bot.think,
    mcts_vanilla=mcts_vanilla.think,
    mcts_modified=mcts_modified.think,
    mcts_parallel=mcts_parallel.think
)

if __name__ == '__main__':
    board = p2_t3.Board()
    state0 = board.starting_state()

    player1 = players['mcts_vanilla']
    player2 = players['mcts_vanilla']

    rounds = 100
    sets = 4
    wins = {'draw':0, 1:0, 2:0}

    #start = time()  # To log how much time the simulation takes.
    for set in range(1, sets + 1):
        plotter.start_timer('main')
        for i in range(rounds):
            plotter.start_timer('round')
            print("\nRound %d, fight!" % i)

            state = state0
            last_action = None
            current_player = player1
            while not board.is_ended(state):
                if current_player == player1:
                    num_nodes = 100
                else:
                    num_nodes = 250 * set
                last_action = current_player(board, state)
                state = board.next_state(state, last_action)
                current_player = player1 if current_player == player2 else player2
            print("Finished!\n")
            final_score = board.points_values(state)
            winner = 'draw'
            if final_score[1] == 1:
                winner = 1
            elif final_score[2] == 1:
                winner = 2
            print("The %s bot wins this round! (%s)" % (winner, str(final_score)))
            if winner == 'draw':
                winner = 0
            plotter.add_game_data(winner, plotter.stop_timer('round'), str(250 * set))
            wins[winner] = wins.get(winner, 0) + 1
        plotter.stop_timer('main')
    plotter.plot_exp_1()
    #print("")
    #print("Final win counts:", dict(wins))

    # Also output the time elapsed.
    #end = time()
    #print(end - start, ' seconds')


    #plotter.plot_exp_2()