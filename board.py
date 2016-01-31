SIZE = 5


class Board:
    def __init__(self):
        self.board = [[''] * SIZE for _ in range(SIZE)]
        self.for_each_cell(lambda (i, j), cell: self.set_cell((i, j), Status(0, '', (i, j))))

    def set_cell(self, location, status):
        self.board[location[0]][location[1]] = status

    def set_player(self, location, player):
        (self.board[location[0]][location[1]]).player = player

    def for_each_cell(self, fn):
        for i in range(SIZE):
            for j in range(SIZE):
                fn((i, j), self.cell_at((i, j)))

    def __str__(self):
        str = ""
        for row in self.board:
            str += "|"
            for cell in row:
                str += (cell.__str__() + "|")
            str += '\n'
        return str

    def free_neighbors(self, player):
        neighbors = []
        for i in range(SIZE):
            for j in range(SIZE):
                location = (i, j)
                cell = self.cell_at(location)
                if cell and cell.player == '' and self.adjacent_cells(location, player):
                    neighbors.append(cell)
        return neighbors

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

    def evaulate(self, player):
        player_score = reduce(
                lambda acc, row: acc + reduce(
                        lambda row_acc, cell: cell.value + row_acc if cell.occupied_by == player else row_acc, row,
                        0),
                self.board, 0)
        opponent_score = reduce(
                lambda acc, row: acc + reduce(
                        lambda row_acc, cell: cell.value + row_acc if cell.occupied_by != player else row_acc, row,
                        0),
                self.board, 0)
        return player_score - opponent_score

    def cell_at(self, location):
        i = location[0]
        j = location[1]
        if i < 0 or j < 0 or i > 4 or j > 4:
            return None

        return self.board[i][j]


class Status:
    def __init__(self, value, player, location):
        self.value = value
        self.player = player
        self.location = location

    def change_occupied(self, new_occupant):
        self.player = new_occupant

    def __str__(self):
        return self.player + str(self.location)
