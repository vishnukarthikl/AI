import sys

from board import Board
from board import SIZE
from board import Status
from greedy import GreedyStrategy


def write_next_state(board, file):
    with open(file, 'w') as f:
        f.truncate()
        f.writelines(board.__str__())


input_file = sys.argv[2]
with open(input_file, 'r') as fin:
    lines = fin.readlines()

search_strategy = lines[0].strip()
if search_strategy != '4':
    player = lines[1].strip()
    depth = lines[2].strip()
    values = map(lambda line: line.strip().split(' '), lines[3:8])
    position = map(lambda line: list(line.strip()), lines[8:13])
    board = Board()
    for i in range(SIZE):
        for j in range(SIZE):
            board.set_cell((i, j), Status(int(values[i][j]), position[i][j], (i, j)))
    if search_strategy == '1':
        board, evaluation = GreedyStrategy(board, player).move()
        write_next_state(board, 'next_state.txt')
    elif search_strategy == '2':
        best_move, traverse_log = MinMaxStrategy(board, player).move()
else:
    print search_strategy + " not handled"
