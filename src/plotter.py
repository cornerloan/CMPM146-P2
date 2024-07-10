from os import name
import time
import matplotlib.pyplot as plt
import json

timers = {}
game_data = {}


def stop_timer(key=None) -> float:
    start_time = timers.get(key, None)
    if start_time:
        timers.pop(key)
        return time.perf_counter() - start_time
    else:
        return 0


def start_timer(key=None) -> None:
    timers[key] = time.perf_counter()


def add_game_data(winning_player: int, game_duration: float, category: str) -> None:
    if not category in game_data:
        game_data[category] = []
    game_data[category].append({"winner": winning_player, "duration": game_duration})


def clear_game_data() -> dict:
    data = game_data
    game_data = None
    return data


def save_data_to_file():
    with open('game_data.json', 'w') as file:
        json.dump(game_data, file)


def plot_exp_1() -> None:	
    tree_sizes = [int(size) for size in game_data.keys()]
    bar_labels = ["Player 1", "Player 2"]
    winrates_p1, winrates_p2 = [], []
    bar_width = 0.35
    for _, data in game_data.items():
        p1_wr = len(list(filter(lambda game: game["winner"] == 1, data))) / len(data)
        p2_wr = len(list(filter(lambda game: game["winner"] == 2, data))) / len(data)
        winrates_p1.append(p1_wr)
        winrates_p2.append(p2_wr)

    # Adjust x positions for the two sets of bars
    x_positions = range(len(tree_sizes))  # Original x positions
    x_positions_p1 = [x - bar_width/2 for x in x_positions]
    x_positions_p2 = [x + bar_width/2 for x in x_positions]

    # Plotting
    plt.bar(x_positions_p1, winrates_p1, width=bar_width, label=bar_labels[0])
    plt.bar(x_positions_p2, winrates_p2, width=bar_width, label=bar_labels[1])

    plt.xticks(x_positions, tree_sizes)  # Set x-ticks to be the tree sizes
    plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1], ['0%', '20%', '40%', '60%', '80%', '100%'])
    #plt.xticks(list(set(tree_sizes)))
    plt.xlabel("Tree Size")
    plt.ylabel("Winrate")
    plt.title("Winrate vs Tree Size")
    plt.legend(bar_labels)
    plt.show()


def plot_exp_2() -> None:
    bar_labels = ["Vanilla", "Modified"]
    labels = [f"Test {i}" for i in range(len(game_data))]
    winrates_p1, winrates_p2 = [], []
    bar_width = 0.35
    for _, data in game_data.items():
        p1_wr = len(list(filter(lambda game: game["winner"] == 1, data))) / len(data)
        p2_wr = len(list(filter(lambda game: game["winner"] == 2, data))) / len(data)
        winrates_p1.append(p1_wr)
        winrates_p2.append(p2_wr)

    # Adjust x positions for the two sets of bars
    x_positions = range(len(labels))  # Original x positions
    x_positions_p1 = [x - bar_width/2 for x in x_positions]
    x_positions_p2 = [x + bar_width/2 for x in x_positions]

    # Plotting
    plt.bar(x_positions_p1, winrates_p1, width=bar_width, label=bar_labels[0])
    plt.bar(x_positions_p2, winrates_p2, width=bar_width, label=bar_labels[1])

    plt.xticks(x_positions, labels)  # Set x-ticks to be the tree sizes
    plt.xlabel("Tests")
    plt.ylabel("Winrate")
    plt.title("Vanilla VS. Modified")
    plt.legend(bar_labels)
    plt.show()