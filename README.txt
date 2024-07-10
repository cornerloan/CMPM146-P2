Group members: Cole Falxa-Sturken, Connor Lowe

To explain the new rollout function in modified, I first have to bring up two helper functions named count_bits() and evaluate_tile()

count_bits(mask) takes a mask as input and returns the number of 1s in the binary representation of the mask variable.

evaluate_tile(board: Board, state, row, column) takes the board, current state of the board, and a specified row and column on the board as input. This function first creates masks for rows, columns, and diagonals, then uses set bits to determine a score for each of those categories to come up with a total score for this move. If the move simply wins the game, then this function returns right away.

rollout(board: Board, state) takes the board and state of the game as input. This function runs until a terminal state is reached, setting up a best_action based on a random move and a best_value set to infinity for player 2 and negative infinity for player 1. Then the main loop begins by looping through all legal actions and performing:
- calculating the next state based off this legal action
- creating a score for this move using evaluate_tile(), using the R and C values (score based on choosing a sub-board)
- evaluate a score for this move using evaluate_tile(), using the r and c values (score based on move in the sub-board)
- update best_action and best_value if this move scores better than the current best move for player 1, or worse than the current best move for player 2
After this loop ends, the board is advanced to the next state using the best_action. Once a terminal state is reached in the game, the final state is returned by rollout()