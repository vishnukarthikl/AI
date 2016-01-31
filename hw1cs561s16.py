import sys

from alpha_beta import AlphaBetaStrategy
from board import Board
from board import SIZE
from board import Status
from game_simulator import GameSimulator
from greedy import GreedyStrategy
from min_max import MinMaxStrategy


def write_next_state(board, file):
    with open(file, 'w') as f:
        f.truncate()
        f.writelines(board.__str__())


def write_states(states, file):
    with open(file, 'w') as f:
        f.truncate()
        for state in states:
            f.writelines(state.__str__())


def get_board_input(lines, start_index):
    values = map(lambda line: line.strip().split(' '), lines[start_index:start_index + 5])
    position = map(lambda line: list(line.strip()), lines[start_index + 5:start_index + 10])
    board = Board()
    for i in range(SIZE):
        for j in range(SIZE):
            board.set_cell((i, j), Status(int(values[i][j]), position[i][j], (i, j)))
    return board


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


def get_strategy(strategy, player, depth):
    if strategy == '1':
        return GreedyStrategy(player)
    elif strategy == '2':
        return MinMaxStrategy(player, depth)
    else:
        return AlphaBetaStrategy(player, depth)


if search_strategy != '4':
    player = lines[1].strip()
    depth = int(lines[2].strip())
    board = get_board_input(lines, 3)
    if search_strategy == '1':
        trace, next_state = GreedyStrategy(player).move(board)
        write_next_state(next_state, 'next_state.txt')
    elif search_strategy == '2':
        move_trace, next_state = MinMaxStrategy(player, depth).move(board)
        write_next_state(next_state, 'next_state.txt')
        write_minmax_trace_log(move_trace, 'traverse_log.txt')
    elif search_strategy == '3':
        move_trace, next_state = AlphaBetaStrategy(player, depth).move(board)
        write_next_state(next_state, 'next_state.txt')
        write_alphabeta_trace_log(move_trace, 'traverse_log.txt')
else:
    players = [get_strategy(lines[2].strip(), lines[1].strip(), int(lines[3].strip())),
               get_strategy(lines[5].strip(), lines[4].strip(), int(lines[6].strip()))]
    board = get_board_input(lines, 7)
    states = GameSimulator(board, players).play()
    write_states(states, 'trace_state.txt')
