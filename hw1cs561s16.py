import sys

from alpha_beta import AlphaBetaStrategy
from board import Board
from board import SIZE
from board import Status
from greedy import GreedyStrategy
from min_max import MinMaxStrategy


def write_next_state(board, file):
    with open(file, 'w') as f:
        f.truncate()
        f.writelines(board.__str__())


def transform_inf(value):
    if value == float('-inf'):
        return '-Infinity'
    elif value == float('inf'):
        return 'Infinity'
    else:
        return value


def write_minmax_trace_log(move_trace, file):
    with open(file, 'w') as f:
        f.truncate()
        f.write('Node,Depth,Value\n')
        for move in move_trace:
            f.write("%s,%s,%s\n" % (move[0], move[1], transform_inf(move[2])))


def write_alphabeta_trace_log(move_trace, file):
    with open(file, 'w') as f:
        f.truncate()
        f.write('Node,Depth,Value,Alpha,Beta\n')
        for move in move_trace:
            f.write("%s,%s,%s,%s,%s\n" % (
                move[0], move[1], transform_inf(move[2]), transform_inf(move[3]), transform_inf(move[4])))


input_file = sys.argv[2]
with open(input_file, 'r') as fin:
    lines = fin.readlines()

search_strategy = lines[0].strip()

if search_strategy != '4':
    player = lines[1].strip()
    depth = int(lines[2].strip())
    values = map(lambda line: line.strip().split(' '), lines[3:8])
    position = map(lambda line: list(line.strip()), lines[8:13])
    board = Board()
    for i in range(SIZE):
        for j in range(SIZE):
            board.set_cell((i, j), Status(int(values[i][j]), position[i][j], (i, j)))
    if search_strategy == '1':
        next_state, evaluation = GreedyStrategy(board, player).move()
        write_next_state(next_state, 'next_state.txt')
    elif search_strategy == '2':
        move_trace, next_state = MinMaxStrategy(board, player, depth).move()
        write_next_state(next_state, 'next_state.txt')
        write_minmax_trace_log(move_trace, 'traverse_log.txt')
    elif search_strategy == '3':
        move_trace, next_state = AlphaBetaStrategy(board, player, depth).move()
        write_next_state(next_state, 'next_state.txt')
        write_alphabeta_trace_log(move_trace, 'traverse_log.txt')
else:
    print search_strategy + " not handled"
