from board import Board

board = Board()
board.set_player((0, 2), '1')
board.set_player((0, 3), '1')
board.set_player((1, 2), '1')
board.set_player((1, 3), '1')
board.set_player((1, 4), '1')
board.set_player((3, 2), '2')
board.set_player((3, 3), '2')

new_board = board.raid((2, 3), '2')
new_board = new_board.raid((0, 4), '1')
new_board = new_board.raid((0, 1), '1')
new_board = new_board.raid((1, 1), '1')
new_board = new_board.raid((2, 1), '1')
new_board = new_board.raid((2, 2), '2')

# print new_board
# new_board = new_board.sneak((3, 4), '2')
# print new_board

board = Board()
board = board.sneak((0, 0), '1')
board = board.sneak((0, 1), '2')
board = board.raid((1, 1), '2')
board = board.sneak((1, 0), '2')
print board
