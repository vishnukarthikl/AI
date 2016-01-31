from board import Board

board = Board()
board.set_player((0, 2), '1')
board.set_player((0, 3), '1')
board.set_player((1, 2), '1')
board.set_player((1, 3), '2')
board.set_player((1, 4), '1')
board.set_player((2, 3), '2')
board.set_player((3, 2), '2')
board.set_player((3, 3), '2')
for cell in board.free_neighbors('2'):
    print cell.location
