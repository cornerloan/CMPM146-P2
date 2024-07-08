from calendar import c
import math
from random import randrange
from mcts_node import MCTSNode
from p2_t3 import Board
from mcts_vanilla import *
from math import sqrt, log, isclose

def test_expand_leaf():
    # Test case 1: Node with untried actions
    node = MCTSNode(parent=None, parent_action=None, action_list=[1, 2, 3])
    board = Board()
    state = board.starting_state()
    result_node, result_state = expand_leaf(node, board, state)
    assert len(result_node.child_nodes) == 1
    assert result_state == board.next_state(state, 1)

    # Test case 2: Terminal node
    node = MCTSNode(parent=None, parent_action=None, action_list=[])
    board = Board()
    state = board.starting_state()
    board.next_state(state, 1)
    board.next_state(state, 2)
    board.next_state(state, 3)
    result_node, result_state = expand_leaf(node, board, state)
    assert result_node == node
    assert result_state == state

    print("All test cases passed!")

def test_rollout(num_rollouts=1000):
    # Test case 1: Starting state
    board = Board()
    state = board.starting_state()
    result_state = rollout(board, state)
    assert board.points_values(result_state) is not None
    # Test case 2: Terminal state
    same_state = rollout(board, result_state)
    assert result_state == same_state
    assert board.points_values(same_state) is not None
    # Test case 3: Intermediate state
    state = board.next_state(state, (1,1,1,1))
    state = board.next_state(state, (2,2,2,2))
    state = board.next_state(state, (1,2,1,2))
    result_state = rollout(board, state)
    assert board.points_values(result_state) is not None
    # Test case 4: Random Intermediate states
    p1_wins = 0
    p2_wins = 0
    draws = 0
    for _ in range(num_rollouts):
        state = board.starting_state()
        for _ in range(randrange(5, 15)):
            state = board.next_state(state, choice(board.legal_actions(state)))
            if board.points_values(state) is not None:
                break
        result_state = rollout(board, state)
        assert board.points_values(result_state) is not None
        board_points = board.win_values(result_state)
        if board_points[1] != board_points[2]:
            p1_wins += board_points[1]
            p2_wins += board_points[2]
        else:
            draws += 1
    assert p1_wins + p2_wins + draws == num_rollouts
    print(f"Player 1 wins: {p1_wins}, Player 2 wins: {p2_wins}, Draws: {draws}")
    print("All test cases passed!")

def test_backpropagate():
    # Test case 1: Single node
    node = MCTSNode(parent=None, parent_action=None, action_list=[])
    backpropagate(node, True)
    assert node.visits == 1
    assert node.wins == 1

    # Test case 2: Multiple nodes
    parent_node = MCTSNode(parent=None, parent_action=None, action_list=[])
    child_node1 = MCTSNode(parent=parent_node, parent_action=(1,1,1,1), action_list=[])
    child_node2 = MCTSNode(parent=parent_node, parent_action=(2,2,2,2), action_list=[])
    parent_node.child_nodes = {(1,1,1,1): child_node1, (2,2,2,2): child_node2}
    backpropagate(child_node1, True)
    backpropagate(child_node2, False)
    assert parent_node.visits == 2
    assert parent_node.wins == 1

    # Test case 3: No nodes
    backpropagate(None, False)

    # Test case 4: Multiple nodes
    parent_node = MCTSNode(parent=None, parent_action=None, action_list=[])
    child_node1 = MCTSNode(parent=parent_node, parent_action=(1,1,1,1), action_list=[])
    child_node2 = MCTSNode(parent=parent_node, parent_action=(2,2,2,2), action_list=[])
    child_node3 = MCTSNode(parent=parent_node, parent_action=(2,1,0,2), action_list=[])
    grandchild_node1 = MCTSNode(parent=child_node1, parent_action=(0, 0, 1, 1), action_list=[])
    grandchild_node2 = MCTSNode(parent=child_node1, parent_action=(0, 0, 1, 2), action_list=[])
    child_node1.child_nodes = {(0, 0, 1, 1): grandchild_node1, (0, 0, 1, 2): grandchild_node2}
    parent_node.child_nodes = {(1,1,1,1): child_node1, (2,2,2,2): child_node2, (2,1,0,2): child_node3}
    backpropagate(child_node1, True)
    backpropagate(child_node2, False)
    backpropagate(child_node3, True)
    assert parent_node.visits == 3
    assert parent_node.wins == 2
    assert child_node1.visits == 1
    assert child_node1.wins == 1
    assert child_node2.visits == 1
    assert child_node2.wins == 0
    assert child_node3.visits == 1
    assert child_node3.wins == 1
    backpropagate(grandchild_node1, True)
    backpropagate(grandchild_node2, False)
    assert parent_node.visits == 5
    assert parent_node.wins == 3
    assert child_node1.visits == 3
    assert child_node1.wins == 2
    assert child_node2.visits == 1
    assert child_node2.wins == 0
    print("All test cases passed!")

def test_ucb():
    node = MCTSNode(parent=None, parent_action=None, action_list=[])
    child_node1 = MCTSNode(parent=node, parent_action=(1,1,1,1), action_list=[])
    child_node1.visits = 5
    child_node1.wins = 3
    child_node2 = MCTSNode(parent=node, parent_action=(1,1,0,1), action_list=[])
    child_node2.visits = 8
    child_node2.wins = 5
    node.child_nodes = {(1,1,1,1): child_node1, (1,1,0,1): child_node2}
    node.visits = child_node1.visits + child_node2.visits
    node.wins = child_node1.wins + child_node2.wins
    assert math.isclose(ucb(child_node1, False), 2.032, rel_tol=1e-3, abs_tol=1e-3), ucb(child_node1, False)
    assert math.isclose(ucb(child_node2, False), 1.757, rel_tol=1e-3, abs_tol=1e-3), ucb(child_node2, False)
    assert math.isclose(ucb(child_node1, True), 1.832, rel_tol=1e-3, abs_tol=1e-3), ucb(child_node1, True)
    assert math.isclose(ucb(child_node2, True), 1.507, rel_tol=1e-3, abs_tol=1e-3), ucb(child_node2, True)
    
    print("All test cases passed!")

def test_get_best_action():
    # Test case 1: Even win rates
    root_node = MCTSNode(parent=None, parent_action=None, action_list=[])
    child_node1 = MCTSNode(parent=root_node, parent_action=(1,1,1,1), action_list=[])
    child_node1.visits = 10
    child_node1.wins = 5
    child_node2 = MCTSNode(parent=root_node, parent_action=(1,1,0,1), action_list=[])
    child_node2.visits = 20
    child_node2.wins = 10
    root_node.child_nodes = {1: child_node1, 2: child_node2}
    assert get_best_action(root_node) == (1,1,1,1), get_best_action(root_node)
    
    # Test case 2: Uneven win rates
    child_node2.visits = 10
    child_node2.wins = 6
    assert get_best_action(root_node) == (1,1,0,1), get_best_action(root_node)

    
    # Test case 3: Grandchild nodes
    root_node = MCTSNode(parent=None, parent_action=None, action_list=[])
    child_node1 = MCTSNode(parent=root_node, parent_action=(1,1,1,1), action_list=[])
    child_node1.visits = 10
    child_node1.wins = 5
    child_node2 = MCTSNode(parent=root_node, parent_action=(1,1,0,1), action_list=[])
    child_node2.visits = 20
    child_node2.wins = 10
    grandchild_node1 = MCTSNode(parent=child_node1, parent_action=(0,0,1,1), action_list=[])
    grandchild_node1.visits = 5
    grandchild_node1.wins = 3
    grandchild_node2 = MCTSNode(parent=child_node1, parent_action=(0,0,1,2), action_list=[])
    grandchild_node2.visits = 8
    grandchild_node2.wins = 4
    child_node1.child_nodes = {(0,0,1,1): grandchild_node1, (0,0,1,2): grandchild_node2}
    root_node.child_nodes = {1: child_node1, 2: child_node2}
    assert get_best_action(root_node) == (1,1,1,1), get_best_action(root_node)

    print("All test cases passed!")

# Add more test functions as needed

#test_expand_leaf()
test_rollout()
test_backpropagate()
test_ucb()
test_get_best_action()
