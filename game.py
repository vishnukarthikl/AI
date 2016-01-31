from board import Board

board = Board()
board.set_player((0, 0), '1')
board.set_player((0, 1), '0')
for cell in board.free_neighbors('1'):
    print cell.location

