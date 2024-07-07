from mcts_node import MCTSNode
from p2_t3 import Board
import mcts_vanilla
from math import sqrt, log

def test_expand_leaf():
    # Test case 1: Node with untried actions
    node = MCTSNode(parent=None, parent_action=None, action_list=[(0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 0, 2)])
    board = Board()
    state = board.starting_state()
    result_node, result_state = expand_leaf(node, board, state)
    assert len(result_node.child_nodes) == 1
    assert result_node in node.child_nodes.values()
    assert result_state in [board.next_state(state, action) for action in [(0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 0, 2)]]

    # Test case 2: Terminal node (assuming game ending after all moves exhausted, adjust if different)
    node = MCTSNode(parent=None, parent_action=None, action_list=[])
    board = Board()
    state = board.starting_state()
    # Assume state represents an ended state (customize this part as per your game logic)
    # This is a placeholder; you need to set up an actual terminal state
    while not board.is_ended(state):
        for move in board.legal_actions(state):
            state = board.next_state(state, move)
    result_node, result_state = expand_leaf(node, board, state)
    assert result_node == node
    assert result_state == state

    print("All test cases passed!")

def test_rollout():
    board = Board()
    state = board.starting_state()
    result_state = rollout(board, state)
    assert board.points_values(result_state) is not None

    print("All test cases passed!")

def test_backpropagate():
    # Test case 1: Single node
    node = MCTSNode(parent=None, parent_action=None, action_list=[])
    backpropagate(node, True)
    assert node.visits == 1
    assert node.wins == 1

    # Test case 2: Multiple nodes
    parent_node = MCTSNode(parent=None, parent_action=None, action_list=[])
    child_node1 = MCTSNode(parent=parent_node, parent_action=(0, 0, 0, 1), action_list=[])
    child_node2 = MCTSNode(parent=parent_node, parent_action=(0, 0, 0, 2), action_list=[])
    parent_node.child_nodes = {(0, 0, 0, 1): child_node1, (0, 0, 0, 2): child_node2}
    backpropagate(child_node1, True)
    backpropagate(child_node2, False)
    assert parent_node.visits == 2
    assert parent_node.wins == 1

    print("All test cases passed!")

def test_ucb():
    node = MCTSNode(parent=None, parent_action=None, action_list=[])
    node.visits = 10
    node.wins = 5
    parent_node = MCTSNode(parent=None, parent_action=None, action_list=[])
    parent_node.visits = 20
    node.parent = parent_node
    assert ucb(node, False) == 0.5

    print("All test cases passed!")

def test_get_best_action():
    root_node = MCTSNode(parent=None, parent_action=None, action_list=[])
    child_node1 = MCTSNode(parent=root_node, parent_action=(0, 0, 0, 1), action_list=[])
    child_node1.visits = 10
    child_node1.wins = 5
    child_node2 = MCTSNode(parent=root_node, parent_action=(0, 0, 0, 2), action_list=[])
    child_node2.visits = 20
    child_node2.wins = 10
    root_node.child_nodes = {(0, 0, 0, 1): child_node1, (0, 0, 0, 2): child_node2}
    assert get_best_action(root_node) == (0, 0, 0, 2)

    print("All test cases passed!")

def test_is_win():
    board = Board()
    state = board.starting_state()
    assert is_win(board, state, 1) == False

    # Custom setup for a winning state
    winning_state = state
    # Assume specific moves leading to a win for player 1, adjust accordingly
    # Placeholder example:
    for move in [(0, 0, 0, 1), (0, 0, 0, 2), (0, 0, 0, 3), (0, 0, 0, 4), (0, 0, 0, 5), (0, 0, 0, 6), (0, 0, 0, 7), (0, 0, 0, 8)]:
        winning_state = board.next_state(winning_state, move)
    assert is_win(board, winning_state, 1) == True

    print("All test cases passed!")

# Add more test functions as needed

test_expand_leaf()
test_rollout()
test_backpropagate()
test_ucb()
test_get_best_action()
test_is_win()
