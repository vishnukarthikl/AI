SIZE = 5
EMPTY = '*'


class Board:
    def __init__(self):
        self.size = SIZE
        self.board = [[''] * SIZE for _ in range(SIZE)]
        self.for_each_cell(lambda (i, j), cell: self.set_cell((i, j), Status(0, EMPTY, (i, j))))

    def set_cell(self, location, status):
        self.board[location[0]][location[1]] = status

    def set_player(self, location, player):
        (self.board[location[0]][location[1]]).player = player

    def raid(self, location, player):
        new_board = self.clone()
        to_raid = new_board.cell_at(location)
        if (not new_board.adjacent_cells(location, player)) or to_raid.is_occupied():
            return new_board
        new_board.set_player(location, player)
        opponent_cells = new_board.adjacent_opponent_cells(location, player)
        for opponent_cell in opponent_cells:
            new_board.set_player(opponent_cell.location, player)

        return new_board

    def sneak(self, location, player):
        new_board = self.clone()
        to_sneak = new_board.cell_at(location)
        if to_sneak.is_occupied():
            return new_board
        if new_board.adjacent_cells(location, player):
            return new_board.raid(location, player)

        new_board.set_player(location, player)
        return new_board

    def for_each_cell(self, fn):
        for i in range(SIZE):
            for j in range(SIZE):
                fn((i, j), self.cell_at((i, j)))

    def all_cells(self):
        cells = []
        for i in range(SIZE):
            for j in range(SIZE):
                cells.append(self.cell_at((i, j)))
        return cells

    def __str__(self):
        str = ""
        for row in self.board:
            for cell in row:
                str += (cell.__str__())
            str += '\n'
        return str

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def location_name(self, location):
        rows = ['A', 'B', 'C', 'D', 'E']
        return rows[location[1]] + str(location[0] + 1)

    def free_neighbors(self, player):
        neighbors = []
        for i in range(SIZE):
            for j in range(SIZE):
                location = (i, j)
                cell = self.cell_at(location)
                if cell and (not cell.is_occupied()) and self.adjacent_cells(location, player):
                    neighbors.append(cell)
        return neighbors

    def adjacent_opponent_cells(self, location, player):
        i = location[0]
        j = location[1]
        adjacent = []
        possible_cells = [self.cell_at((i - 1, j)), self.cell_at((i + 1, j)), self.cell_at((i, j - 1)),
                          self.cell_at((i, j + 1))]
        for cell in possible_cells:
            if cell and cell.player != player and cell.is_occupied():
                adjacent.append(cell)
        return adjacent

    def adjacent_cells(self, location, player):
        i = location[0]
        j = location[1]
        adjacent = []
        possible_cells = [self.cell_at((i - 1, j)), self.cell_at((i + 1, j)), self.cell_at((i, j - 1)),
                          self.cell_at((i, j + 1))]
        for cell in possible_cells:
            if cell and cell.player == player:
                adjacent.append(cell)
        return adjacent

    def evaluate(self, player):
        player_score = reduce(
                lambda acc, row: acc + reduce(
                        lambda row_acc, cell: cell.value + row_acc if cell.player == player else row_acc, row,
                        0),
                self.board, 0)
        opponent_score = reduce(
                lambda acc, row: acc + reduce(
                        lambda row_acc,
                               cell: cell.value + row_acc if cell.is_occupied() and cell.player != player else row_acc,
                        row,
                        0),
                self.board, 0)
        return player_score - opponent_score

    def cell_at(self, location):
        i = location[0]
        j = location[1]
        if i < 0 or j < 0 or i > 4 or j > 4:
            return None

        return self.board[i][j]

    def clone(self):
        board = Board()
        for i in range(SIZE):
            for j in range(SIZE):
                board.set_cell((i, j), self.cell_at((i, j)).clone())
        return board

    def valid_moves(self, player):
        moves = []
        for i in range(SIZE):
            for j in range(SIZE):
                if self.sneak((i, j), player) != self:
                    moves.append((i, j))
        return moves

    def is_over(self):
        return reduce(lambda acc, cell: acc and cell.is_occupied(), self.all_cells(), True)

    def winner(self):
        if self.evaluate('X') > 0:
            return 'X'
        else:
            return 'O'


class Status:
    def __init__(self, value, player, location):
        self.value = value
        self.player = player
        self.location = location

    def change_player(self, player):
        self.player = player

    def is_occupied(self):
        return self.player != EMPTY

    def __str__(self):
        return self.player

    def clone(self):
        return Status(self.value, self.player, self.location)

    def __eq__(self, other):
        return self.player == other.player
