def test_expand_leaf():
    # Test case 1: Node with untried actions
    node = MCTSNode(parent=None, parent_action=None, action_list=[1, 2, 3])
    board = Board()
    state = board.start_state()
    result_node, result_state = expand_leaf(node, board, state)
    assert len(result_node.child_nodes) == 1
    assert result_state == board.next_state(state, 1)

    # Test case 2: Terminal node
    node = MCTSNode(parent=None, parent_action=None, action_list=[])
    board = Board()
    state = board.start_state()
    board.make_move(state, 1)
    board.make_move(state, 2)
    board.make_move(state, 3)
    result_node, result_state = expand_leaf(node, board, state)
    assert result_node == node
    assert result_state == state

    print("All test cases passed!")

def test_rollout():
    board = Board()
    state = board.start_state()
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
    child_node1 = MCTSNode(parent=parent_node, parent_action=1, action_list=[])
    child_node2 = MCTSNode(parent=parent_node, parent_action=2, action_list=[])
    parent_node.child_nodes = {1: child_node1, 2: child_node2}
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
    child_node1 = MCTSNode(parent=root_node, parent_action=1, action_list=[])
    child_node1.visits = 10
    child_node1.wins = 5
    child_node2 = MCTSNode(parent=root_node, parent_action=2, action_list=[])
    child_node2.visits = 20
    child_node2.wins = 10
    root_node.child_nodes = {1: child_node1, 2: child_node2}
    assert get_best_action(root_node) == 2

    print("All test cases passed!")

def test_is_win():
    board = Board()
    state = board.start_state()
    assert is_win(board, state, 1) == False

    state = board.next_state(state, 1)
    state = board.next_state(state, 2)
    state = board.next_state(state, 3)
    assert is_win(board, state, 1) == True

    print("All test cases passed!")

# Add more test functions as needed

test_expand_leaf()
test_rollout()
test_backpropagate()
test_ucb()
test_get_best_action()
test_is_win()