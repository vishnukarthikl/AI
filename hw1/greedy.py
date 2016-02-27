class GreedyStrategy:
    def __init__(self, player):
        self.player = player

    def move(self, board):
        best_position = (board, board.evaluate(self.player))
        for i in range(board.size):
            for j in range(board.size):
                new_state = board.sneak((i, j), self.player)
                new_evaluation = new_state.evaluate(self.player)
                if new_evaluation > best_position[1]:
                    best_position = (new_state, new_evaluation)
        return [], best_position[0]
