
from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log, isclose
import time

explore_faction = 2.

# Eval consts
# The value given to a tile that is a win for one player
win_value = 10
# The value given to a move that gives the opponent free choice on their turn
# Free choice means they can place a mark in any tile because the designated tile was full
free_choice_penalty = -5

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """ Traverses the tree until the end criterion are met.
    e.g. find the best expandable node (node with untried action) if it exist,
    or else a terminal node

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 1 or 2

    Returns:
        node: A node from which the next stage of the search can proceed.
        state: The state associated with that node

    """
    while True:
        assert node, "Node is none in traverse_nodes"

        #if there are untried actions, return this node
        if node.untried_actions:
            return node, state
        
        #if the game is over, return this node
        if board.is_ended(state):
            return node, state
        
        #if neither, select next node based on UCB
        best_child, best_value = None, -float('inf')
        for action, child in node.child_nodes.items():
            is_opponent = (bot_identity != board.current_player(state))
            child_value = ucb(child, is_opponent)
            if child_value > best_value:
                best_value = child_value
                best_child = child

        #update node and state for next loop
        node = best_child
        state = board.next_state(state, node.parent_action)


def expand_leaf(node: MCTSNode, board: Board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node (if it is non-terminal).

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:
        node: The added child node
        state: The state associated with that node

    """
    assert node, "Node is none in expand_leaf"

    #if there are any untried actions for the supplied node
    if node.untried_actions:
        action = node.untried_actions.pop()
        next_state = board.next_state(state, action)
        child_node = MCTSNode(parent=node, parent_action=action, action_list=board.legal_actions(next_state))
        node.child_nodes[action] = child_node
        return child_node, next_state
    #otherwise we can assume this node has no other actions to perform (game ended)
    else:
        return node, state


def rollout(board: Board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.
    
    Returns:
        state: The terminal game state

    """
    while board.points_values(state) is None:
        player = board.current_player(state)
        best_action = choice(board.legal_actions(state))
        best_value = float('INF') * 1 if player == 2 else -1
        #  1   2   4
        #  8   16  32
        #  64  128 256

        for action in board.legal_actions(state):
            R, C, r, c = action
            next_state = board.next_state(state, action)
            action_score = evaluate_tile(board, next_state, R, C)
            # Is action placing tile into a generally good square?
            # Will action be good for this tile? Ex. set player up to score
            # Will action place opponent in bad tile?
            next_tile_score = evaluate_tile(board, next_state, r, c)
            if isclose(abs(next_tile_score), win_value):
                action_score += free_choice_penalty * 1 if player == 1 else -1
            else:
                if next_tile_score < 0 and player == 1 or next_tile_score > 0 and player == 2:
                    action_score += next_tile_score * 0.5
            if player == 1 and action_score > best_value or player == 2 and action_score < best_value:
                best_action = action
                best_value = action_score
        state = board.next_state(state, best_action)
    return state 


def backpropagate(node: MCTSNode|None, won: bool):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    if not node:
        return
    node.visits += 1
    node.wins += int(won)
    backpropagate(node.parent, won) 


def ucb(node: MCTSNode, is_opponent: bool):
    """ Calcualtes the UCB value for the given node from the perspective of the bot

    Args:
        node:   A node.
        is_opponent: A boolean indicating whether or not the last action was performed by the MCTS bot
    Returns:
        The value of the UCB function for the given node
    """
    assert node, "Node is None in ucb function"
    assert node.visits > 0, "Node has not been visited yet in ucb function"
    assert node.parent, "Node does not have a parent in ucb function"
    win_rate = (node.wins / node.visits)
    if is_opponent:
        win_rate = 1 - win_rate
    explore_value = explore_faction * sqrt(log(node.parent.visits) / node.visits)
    return win_rate + explore_value


def get_best_action(root_node: MCTSNode):
    """ Selects the best action from the root node in the MCTS tree

    Args:
        root_node:   The root node
    Returns:
        action: The best action from the root node
    
    """
    assert root_node.child_nodes, "Root node has no children"
    return max(root_node.child_nodes.values(), key=lambda x: x.wins / max(x.visits, 1)).parent_action


def is_win(board: Board, state, identity_of_bot: int):
    # checks if state is a win state for identity_of_bot
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1


def think(board: Board, current_state, num_nodes: int = 1000, time_limit: float = None):
    bot_identity = board.current_player(current_state) # 1 or 2
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))
    if time_limit is not None:
        num_nodes = None
    start_time = time.time()
    num_iterations = 0
    while (time_limit is None or time.time() < start_time + time_limit) and (num_nodes is None or num_iterations < num_nodes):
        state = current_state
        node = root_node
        # Do MCTS - This is all you!
        node, state = traverse_nodes(node, board, state, bot_identity)
        node, state = expand_leaf(node, board, state)
        terminal_state = rollout(board, state)
        player_won = is_win(board, terminal_state, bot_identity)
        backpropagate(node, player_won)
        num_iterations += 1

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best_action = get_best_action(root_node)
    print("Modified Tree size: ", root_node.visits, file=open("tree_sizes.txt", "a"))
    print(f"Action chosen: {best_action}")
    return best_action


def evaluate_tile(board : Board, state, row, column):
    """

    Returns:    The evaluation for  the board: positive for p1 and negative for p2.

    """
    # Constants
    row_mask = lambda row: 0b111 << row
    col_mask = lambda col: 0b001001001 << col
    lr_diag_mask = 0b100010001
    rl_diag_mask = 0b001010100

    score = 0
    p1 = state[3 * row + column]
    p2 = state[3 * row + column + 1]
    all = p1 | p2
    # Check for wins/winnability in rows and cols
    # If player wins then return immediately
    for row in range(3):
        p1_row = row_mask(row) & p1
        p2_row = row_mask(row) & p2
        row_score = 0
        # Check for win
        if not (p1_row ^ row_mask(row) and p2_row ^ row_mask(row)):
            return win_value * (1 if p1_row else -1)
        # Score in favor of player that can score off of this row
        row_score = count_bits(p1_row) - count_bits(p2_row)
        # Check for ties
        row_score *= (p1_row == 0 or p2_row == 0) and (p1_row | p2_row) != 0
        score += row_score
    for col in range(3):
        p1_col = col_mask(col) & p1
        p2_col = col_mask(col) & p2
        col_score = 0
        # Check for win
        if not (p1_col ^ col_mask(col) and p2_col ^ col_mask(col)):
            return win_value * (1 if p1_col else -1)
        # Score in favor of player that can score off of this col
        col_score = count_bits(p1_col) - count_bits(p2_col)
        # Check for ties
        col_score *= (p1_col == 0 or p2_col == 0) and (p1_col | p2_col) != 0
        score += col_score
    
    # Check for diagonal wins
    lr_diag = lr_diag_mask & all
    rl_diag = rl_diag_mask & all
    diag_score = 0
    # Check for win in left-to-right diagonal
    if not ((lr_diag & p1) ^ lr_diag_mask and (lr_diag & p2) ^ lr_diag_mask):
        return win_value * (1 if lr_diag & p1 else -1)
    # Score in favor of player that can score off of this diagonal
    diag_score = count_bits(lr_diag & p1) - count_bits(lr_diag & p2)
    # Check for ties
    diag_score *= bool(lr_diag & p1) ^ bool(lr_diag & p2)
    score += diag_score
    # Check for win in right-to-left diagonal
    if not ((rl_diag & p1) ^ rl_diag_mask and (rl_diag & p1) ^ rl_diag_mask):
        return win_value * (1 if rl_diag & p1 else -1)
    # Score in favor of player that can score off of this diagonal
    diag_score = count_bits(rl_diag & p1) - count_bits(rl_diag & p2)
    # Check for ties
    diag_score *= bool(rl_diag & p1) ^ bool(rl_diag & p2)
    score += diag_score
    
    return score

def count_bits(mask):
    bits = 0
    while(mask):
        bits += mask & 1
        mask >>= 1
    return bits