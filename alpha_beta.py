def toggle_player(player):
    if player == 'X':
        return 'O'
    else:
        return 'X'


class AlphaBetaStrategy:
    def __init__(self, player, depth):
        self.player = player
        self.depth = depth
        self.trace = []

    def move(self, board):
        next_best_move = board
        alpha = float('-Infinity')
        beta = float('Infinity')
        value = alpha
        self.trace = [('root', 0, value, alpha, beta)]
        moves = board.valid_moves(self.player)
        for move in moves:
            next_level_evaluation = self.traverse_next_level(board, move, 1, self.player, alpha,
                                                             beta)
            if next_level_evaluation > value:
                value = next_level_evaluation
                next_best_move = board.sneak(move, self.player)
                alpha = value

            self.trace.append(('root', 0, value, alpha, beta))
        return self.trace, next_best_move

    def traverse_next_level(self, board, move, current_depth, player, alpha, beta):
        state = board.sneak(move, player)
        if current_depth == self.depth:
            next_state_evaluation = state.evaluate(self.player)
            self.trace.append((state.location_name(move), current_depth, next_state_evaluation, alpha, beta))
            return next_state_evaluation
        else:
            should_minimize = current_depth % 2 == 1
            if should_minimize:
                value = float('Infinity')
            else:
                value = float('-Infinity')

            next_moves = state.valid_moves(player)

            for next_move in next_moves:
                self.trace.append((board.location_name(move), current_depth, value, alpha, beta))
                next_state_evaluation = self.traverse_next_level(board.sneak(move, player), next_move,
                                                                 current_depth + 1,
                                                                 toggle_player(player), alpha, beta)
                if should_minimize:
                    value = min(value, next_state_evaluation)
                    if value <= alpha:
                        break
                    beta = min(value, beta)
                else:
                    value = max(value, next_state_evaluation)
                    if next_state_evaluation >= beta:
                        break
                    alpha = max(alpha, value)
            self.trace.append((board.location_name(move), current_depth, value, alpha, beta))
        return value
