
from logging import root
import time
from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log
import multiprocessing as mp

num_nodes = 100
num_nodes_per_cpu = num_nodes // mp.cpu_count()
explore_faction = 2.

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
        action = choice(board.legal_actions(state))
        state = board.next_state(state, action)
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
    #return max(root_node.child_nodes.values(), key=lambda x: x.visits).parent_action
    
def is_win(board: Board, state, identity_of_bot: int):
    # checks if state is a win state for identity_of_bot
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state, timeout: float = -1):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        current_state:  The current state of the game.

    Returns:    The action to be taken from the current state

    """
    bot_identity = board.current_player(current_state) # 1 or 2
    end_time = time.time() + timeout - 0.25 if timeout > 0 else None
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))
    if num_nodes <= 100:
        num_nodes_per_cpu = num_nodes
        root_node = think_internal(root_node.untried_actions.copy(), board, current_state, bot_identity, end_time, num_nodes_per_cpu)
        num_nodes_per_cpu = temp
    else:
        pool = mp.Pool(mp.cpu_count())
        args_list = [(root_node.untried_actions.copy(), board, current_state, bot_identity, end_time) for _ in range(mp.cpu_count())]
        async_results = pool.starmap_async(think_internal, args_list)
        try:
            results = async_results.get(timeout if timeout > 0 else None)
        except mp.TimeoutError:
            raise TimeoutError("MCTS took too long to complete")
        finally:
            pool.close()
            pool.join()
        for result in results:
            if isinstance(result, Exception):
                raise result
            for node in result.child_nodes.values():
                if node.parent_action in root_node.child_nodes:
                    root_node.child_nodes[node.parent_action].visits += node.visits
                    root_node.child_nodes[node.parent_action].wins += node.wins
                else:
                    root_node.child_nodes[node.parent_action] = node
                    node.parent = root_node
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best_action = get_best_action(root_node)
    #print(f"Action chosen: {best_action} winrate: {root_node.child_nodes[best_action].wins / root_node.child_nodes[best_action].visits:.2f}")
    #print(board.display(current_state, None)) 
    print(f"Action chosen: {best_action}")
    return best_action

def think_internal(actions, board, current_state, bot_identity, end_time=None):
    root_node = MCTSNode(None, None, actions)
    try:
        if end_time is not None:
            while time.time() < end_time:
                node = root_node
                state = current_state
                node, state = traverse_nodes(node, board, state, bot_identity)
                node, state = expand_leaf(node, board, state)
                terminal_state = rollout(board, state)
                player_won = is_win(board, terminal_state, bot_identity)
                backpropagate(node, player_won)
        else:
            for _ in range(num_nodes_per_cpu):
                node = root_node
                state = current_state
                node, state = traverse_nodes(node, board, state, bot_identity)
                node, state = expand_leaf(node, board, state)
                terminal_state = rollout(board, state)
                player_won = is_win(board, terminal_state, bot_identity)
                backpropagate(node, player_won)
        return root_node
    except Exception as e:
        return e