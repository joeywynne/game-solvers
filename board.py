import numpy as np
from pathlib import Path
from io import StringIO
import matplotlib.pyplot as plt
from matplotlib import cm
from dataclasses import dataclass


DISPLAY_MAP = {
    0: " ",
    1: "-",
    2: "T"
}

@dataclass
class Square():
    """Square dataclass."""
    shape_id: int
    coords: tuple[int, int]
    symbol_id: int = 0


class Board:
    """Board class to handle state and display.

    Grid info denoted by 3D Numpy Grid
    2D grid for position of shapes
    3rd dimension denotes the Symbol to display [ , T, -]
    Value represents the shapes (int)

    Add display
        - with coloured grid
        - before and after
        - outlines of shapes
    """
    def __init__(self, grid: np.ndarray):

        board_state = generate_state(grid)

        self.board_state = self._is_valid_state(board_state)
        self.start_state = self.board_state.copy()
    
    def _is_valid_state(self, state):
        """Check that the state is valid for a tree game
        1. Checks is a square grid
        2. Checks 3rd dimension only contains valid chars
        3. Checks shapes are connected
        """
        return state
    
    def display(self, solved: bool | None = None, sub_title: str = "", state_type: str="current"):
        n = self.num_shapes
        colours = cm.tab10(range(n))

        board = self.board_state if state_type == "current" else self.start_state
        rows, cols = board.shape
        _, ax = plt.subplots(figsize=(cols, rows))

        for i in range(rows):
            for j in range(cols):
                shape_symbol = board[i, j].symbol_id
                shape_colour = colours[board[i, j].shape_id]

                rect = plt.Rectangle((j, rows -i -1), 1, 1, facecolor=shape_colour, edgecolor='black')
                ax.add_patch(rect)

                symbol = DISPLAY_MAP[shape_symbol]
                ax.text(j + 0.5, rows - i - 1 + 0.5, symbol, ha="center", va="center", fontsize=20, color="black", fontweight='bold')
        
                ax.set_xlim(0, cols)

        ax.set_ylim(0, rows)
        ax.set_xticks(np.arange(cols) + 0.5)
        ax.set_yticks(np.arange(rows) + 0.5)
        ax.set_xticklabels(np.arange(cols))
        ax.set_yticklabels(np.arange(rows)[::-1])
        ax.grid(False)
        ax.set_aspect('equal')
        if solved is not None:
            title = "Solved!" if solved else "Failed..."
        if sub_title:
            title += "\n" + sub_title
        ax.set_title(title)

        plt.show()
    
    def place_dash(self, square_coords: tuple) -> None:
        """Placing dash just adds dash."""
        # Dash is 1
        self.board_state[square_coords].symbol_id = 1
    
    def place_tree(self, square_coords: tuple) -> None:
        """Placing tree and dashes where it blocks."""
        # T is 2
        square = self.board_state[square_coords]
        square.symbol_id = 2
        # Set blocked squares and rest of shape to dash (1)
        squares_to_dash = self.get_blocked_squares(square) + self.get_squares_of_shape(square.shape_id)
        deduped_coords = set(square.coords for square in squares_to_dash).difference([square_coords])
        for coords in deduped_coords:
            self.place_dash(coords)
 

    def board_shape_ids(self) -> np.ndarray:
        return np.array([[cell.shape_id for cell in row] for row in self.board_state])
    
    def board_symbols(self) -> np.ndarray:
        return np.array([[cell.symbol_id for cell in row] for row in self.board_state])
    
    def get_squares_with_symbol(self, symbol_id: int) -> list[tuple]:
        """Get the coords of squares with given symbol id """
        coords = np.where(self.board_symbols() == symbol_id)
        # Warning must be standardised as ints
        return [self.board_state[coord] for coord in zip(*coords)]
    
    def get_squares_of_shape(self, shape_id: int) -> list[Square]:
        """Get the squares with given shape id """
        coords = np.where(self.board_shape_ids() == shape_id)
        # Warning must be standardised as ints
        return [self.board_state[coord] for coord in zip(*coords)]
    
    def get_empty_squares(self) -> list[Square]:
        """Get the coords of squares without symbols"""
        return self.get_squares_with_symbol(0)
    
    def get_blocked_squares(self, square: Square) -> list[Square]:
        """Get all squares that are blocked if square is a tree.
        
        Full row + Full column + diagonal neighbours
        """
        lim_i, lim_j = self.board_state.shape
        square_coords = square.coords
        diag_neighbours = [
            (square_coords[0] + 1, square_coords[1] + 1),
            (square_coords[0] + 1, square_coords[1] - 1),
            (square_coords[0] - 1, square_coords[1] + 1),
            (square_coords[0] - 1, square_coords[1] - 1)
        ]
        diag_neighbours = [
            n for n in diag_neighbours if 
            0 <= n[0] < lim_i and 0 <= n[1] < lim_j
        ]
        row = [(square_coords[0], i) for i in range(lim_i)]
        col = [(j, square_coords[1]) for j in range(lim_j)]
        coords = set(row + col + diag_neighbours) - {square_coords}
        return [self.board_state[coord] for coord in coords]
    
    def get_groups(self) -> dict:
        """Return dict lookup of group id to group info.
        
        Group info is coords plus symbol
        """
        result = dict()
        for i in np.unique(self.board_shape_ids()):
            squares = self.get_squares_of_shape(i)
            result[i] = squares
        return result

    @property
    def num_shapes(self):
        return len(set(self.board_shape_ids().flatten()))
    
    @property
    def is_solved(self):
        return not (self.board_symbols() == 0).any()
    
    @property
    def size(self):
        """Return number of rows in board.
        
        Note: board is always square.
        """
        return len(self.board_state)


def read_board(file_path: Path) -> Board:
    """Create a Board object from a csv file path"""
    data_txt = file_path.read_text()
    start_grid = np.genfromtxt(StringIO(data_txt), delimiter=",", dtype=int)
    return Board(start_grid)

def generate_state(grid: np.ndarray) -> np.ndarray:
    """Create a board state from the grid"""
    state = np.empty(grid.shape, dtype=object)
    for i, row in enumerate(grid):
        for j, shape_id in enumerate(row):
            state[i, j] = Square(shape_id=shape_id, coords=(i, j), symbol_id=0)
    return state

