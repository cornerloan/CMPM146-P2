from os import name
import time
import matplotlib.pyplot as plt
import json
import os

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
    file_name = 'game_data.json'
    i = 1
    while os.path.exists(file_name):
        file_name = f'game_data({i}).json'
        i += 1
    with open(file_name, 'w') as file:
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
    plt.title("Winrate VS. Tree Size")
    plt.legend(bar_labels)
    plt.show()


def plot_exp_2() -> None:
    bar_labels = ["Vanilla", "Modified"]
    labels = [f"Test {i}" for i in range(1, len(game_data) + 1)]
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


def plot_exp_3() -> None:
    modified = []
    vanilla = []

    with open('tree_sizes.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            subs = line.split(":")
            if len(subs) > 1:
                if 'vanilla' in line.lower():
                    line = subs[1].strip()
                    vanilla.append(int(line))
                elif 'modified' in line.lower():
                    line = subs[1].strip()
                    modified.append(int(line))
    with open('tree_size_analysis.txt', 'w') as file:
        file.write("Vanilla:\n")
        file.write(f"Mean: {sum(vanilla) / len(vanilla)}\n")
        file.write(f"Median: {sorted(vanilla)[len(vanilla) // 2]}\n")
        file.write(f"Min: {min(vanilla)}\n")
        file.write(f"Max: {max(vanilla)}\n\n")
        
        file.write("Modified:\n")
        file.write(f"Mean: {sum(modified) / len(modified)}\n")
        file.write(f"Median: {sorted(modified)[len(modified) // 2]}\n")
        file.write(f"Min: {min(modified)}\n")
        file.write(f"Max: {max(modified)}\n")


if __name__ == '__main__':
    plot_exp_3()
    pass