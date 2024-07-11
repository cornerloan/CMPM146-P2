from math import e
import p2_t3
import sys
import mcts_vanilla
import mcts_modified
import mcts_parallel
import random_bot
import rollout_bot
import plotter
import statistics

players = dict(
    random_bot=random_bot.think,
    rollout_bot=rollout_bot.think,
    mcts_vanilla=mcts_vanilla.think,
    mcts_modified=mcts_modified.think,
    mcts_parallel=mcts_parallel.think
)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Need experiment number as argument")
        exit(1)
    
    exp = int(sys.argv[1])
    if exp not in [1, 2, 3, 4]:
        print("Experiment number must be 1, 2, 3, or 4")
        exit(1)
    board = p2_t3.Board()
    state0 = board.starting_state()
    wins = {'draw':0, 1:0, 2:0}
    rounds = 100
    if exp == 1:
        player1 = players['mcts_vanilla']
        player2 = players['mcts_vanilla']
        sets = 4

        #start = time()  # To log how much time the simulation takes.
        for set in range(1, sets + 1):
            plotter.start_timer('main')
            for i in range(rounds):
                plotter.start_timer('round')
                print("\nRound %d, fight!" % i)

                state = state0
                last_action = None
                current_player = player1
                turn = True
                while not board.is_ended(state):
                    last_action = current_player(board, state, 100 if turn else 250 * set)
                    state = board.next_state(state, last_action)
                    current_player = player1 if current_player == player2 else player2
                    turn = not turn
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
        print(f"Final win counts: {dict(wins)}")
        print("Experiment 1 complete")
        plotter.save_data_to_file()
        plotter.clear_game_data()
        exit(0)
    elif exp == 2:
        sets = 3
        rounds = 100
        player1 = players['mcts_vanilla']
        player2 = players['mcts_modified']
        for set in range(1, sets + 1):
            plotter.start_timer('main')
            for i in range(rounds):
                plotter.start_timer('round')
                print("\nRound %d, fight!" % i)
                state = state0
                last_action = None
                current_player = player1
                while not board.is_ended(state):
                    last_action = current_player(board, state, set * 250 + 250)
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
                plotter.add_game_data(winner, plotter.stop_timer('round'), str(set))
                wins[winner] = wins.get(winner, 0) + 1
        print(f"Final win counts: {dict(wins)} duration: {plotter.stop_timer('main')}")
        plotter.plot_exp_2()
        print("Experiment 2 complete")
        plotter.save_data_to_file()
        plotter.clear_game_data()
        exit(0)
    elif exp == 3:
        player1 = players['mcts_vanilla']
        player2 = players['mcts_modified']
        rounds = 10
        tree_sizes = {"vanilla": [], "modified": []}
        for i in range(rounds):
            print("\nRound %d, fight!" % i)
            state = state0
            last_action = None
            current_player = player1
            while not board.is_ended(state):
                last_action = current_player(board, state, time_limit=2.5)
                state = board.next_state(state, last_action)
                current_player = player1 if current_player == player2 else player2
            final_score = board.points_values(state)
            winner = 'draw'
            if final_score[1] == 1:
                winner = 1
            elif final_score[2] == 1:
                winner = 2
            print("\nThe %s bot wins this round! (%s)\n" % (winner, str(final_score)), file=open("tree_sizes.txt", "a"))
            plotter.plot_exp_3()
    elif exp == 4:
        player1 = players['mcts_vanilla']
        player2 = players['mcts_parallel']
        rounds = 5
        plotter.start_timer('main')
        times = {"vanilla": [], "parallel": []}
        for i in range(rounds):
            plotter.start_timer('round')
            print("\nRound %d, fight!" % i)
            state = state0
            last_action = None
            current_player = player1
            while not board.is_ended(state):
                plotter.start_timer('turn')
                last_action = current_player(board, state, 5000)
                turn_time = plotter.stop_timer('turn')
                if current_player == player1:
                    times["vanilla"].append(turn_time)
                    current_player = player2
                else:
                    times["parallel"].append(turn_time)
                    current_player = player1
                state = board.next_state(state, last_action)
        p1_mean = statistics.mean(times["vanilla"])
        p1_min = min(times["vanilla"])
        p1_max = max(times["vanilla"])
        p1_median = statistics.median(times["vanilla"])

        p2_mean = statistics.mean(times["parallel"])
        p2_min = min(times["parallel"])
        p2_max = max(times["parallel"])
        p2_median = statistics.median(times["parallel"])
        with open('exp4_analysis.txt_5000', 'w') as file:
            file.write("Player 1 (mcts_vanilla) stats:\n")
            file.write("Mean turn time: " + str(p1_mean) + "\n")
            file.write("Median turn time: " + str(p1_median) + "\n")
            file.write("Min turn time: " + str(p1_min) + "\n")
            file.write("Max turn time: " + str(p1_max) + "\n\n")

            file.write("Player 2 (mcts_parallel) stats:\n")
            file.write("Mean turn time: " + str(p2_mean) + "\n")
            file.write("Median turn time: " + str(p2_median) + "\n")
            file.write("Min turn time: " + str(p2_min) + "\n")
            file.write("Max turn time: " + str(p2_max) + "\n")
    #print("")
    #print("Final win counts:", dict(wins))

    # Also output the time elapsed.
    #end = time()
    #print(end - start, ' seconds')


    #plotter.plot_exp_2()