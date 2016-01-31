class GreedyStrategy:
    def __init__(self, board, player):
        self.initial_board = board
        self.player = player

    def move(self):
        best_position = (self.initial_board, self.initial_board.evaluate(self.player))
        for i in range(self.initial_board.size):
            for j in range(self.initial_board.size):
                new_state = self.initial_board.sneak((i, j), self.player)
                new_evaluation = new_state.evaluate(self.player)
                if new_evaluation > best_position[1]:
                    best_position = (new_state, new_evaluation)
        return best_position
