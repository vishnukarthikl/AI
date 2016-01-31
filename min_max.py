def toggle_player(player):
    if player == 'X':
        return 'O'
    else:
        return 'X'


class MinMaxStrategy:
    def __init__(self, player, depth):
        self.player = player
        self.depth = depth
        self.trace = []

    def move(self, board):
        next_best_move = board
        current_max = float('-Infinity')
        self.trace = [('root', 0, current_max)]
        moves = board.valid_moves(self.player)
        for move in moves:
            next_level_evaluation = self.traverse_next_level(board, move, 1, self.player)
            if next_level_evaluation > current_max:
                current_max = next_level_evaluation
                next_best_move = board.sneak(move, self.player)
            self.trace.append(('root', 0, current_max))
        return self.trace, next_best_move

    def traverse_next_level(self, board, move, current_depth, player):
        state = board.sneak(move, player)
        if current_depth == self.depth:
            next_state_evaluation = state.evaluate(self.player)
            self.trace.append((state.location_name(move), current_depth, next_state_evaluation))
            return next_state_evaluation
        else:
            should_minimize = current_depth % 2 == 1
            if should_minimize:
                value = float('Infinity')
            else:
                value = float('-Infinity')

            next_moves = state.valid_moves(player)

            for next_move in next_moves:
                self.trace.append((board.location_name(move), current_depth, value))
                next_state_evaluation = self.traverse_next_level(board.sneak(move, player), next_move,
                                                                 current_depth + 1,
                                                                 toggle_player(player))
                if should_minimize:
                    if next_state_evaluation < value:
                        value = next_state_evaluation
                else:
                    if next_state_evaluation > value:
                        value = next_state_evaluation

            self.trace.append((board.location_name(move), current_depth, value))
        return value
