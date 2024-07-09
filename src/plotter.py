import time
import matplotlib.pyplot as plt
from functools import reduce, filter
import json

timers = {}
game_data = {[]}

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
	tree_sizes = [int(size) for size in game_data.keys() for _ in range(2)]
	bar_labels = ["Player 1", "Player 2"]
	winrates = []
	for _, data in game_data:
		p1_wr = len(filter(lambda game: game["winner"] == 1, data))
		p2_wr = len(filter(lambda game: game["winner"] == 2, data))
		winrates.append(p1_wr)
		winrates.append(p2_wr)
	
	plt.bar(tree_sizes, winrates)
	plt.xticks(tree_sizes)
	plt.xlabel("Tree Size")
	plt.ylabel("Winrate")
	plt.title("Winrate vs Tree Size")
	plt.legend(bar_labels)
	plt.show()


def plot_exp_2() -> None:
	bar_labels = ["Vanilla", "Modified"]
	winrates = []
	labels = [f"Test {i}" for i in range(len(game_data)) for _ in range(2)]
	for _, data in game_data:
		p1_wr = len(filter(lambda game: game["winner"] == 1, data))
		p2_wr = len(filter(lambda game: game["winner"] == 2, data))
		winrates.append(p1_wr)
		winrates.append(p2_wr)
	
	plt.bar(labels, winrates)
	plt.xlabel("Tests")
	plt.ylabel("Winrate")
	plt.title("Vanilla VS. Modified")
	plt.legend(bar_labels)
	plt.show()
	