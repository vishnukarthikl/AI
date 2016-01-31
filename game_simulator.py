class GameSimulator:
    def __init__(self, board, players):
        self.board = board
        self.players = players

    def play(self):
        turn = 0
        trace_states = []
        board = self.board
        while not board.is_over():
            board = self.players[turn].move(board)[1]
            trace_states.append(board)
            turn = (turn + 1) % 2

        return trace_states
