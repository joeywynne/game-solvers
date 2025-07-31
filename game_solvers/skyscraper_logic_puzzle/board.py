import numpy as np
from pathlib import Path
from io import StringIO
import matplotlib.pyplot as plt
from matplotlib import cm
from dataclasses import dataclass


@dataclass
class Square():
    """Square dataclass."""
    shape_value: int
    sub_values: list[int]
    coords: tuple[int, int]


class Board:
    """Board class to handle state and display.

    Grid info denoted by 2D Numpy Grid
    Value represents the height of building if game square or the clue if not
    """
    def __init__(self, grid: np.ndarray, file_path: Path):
        grid_size = grid.shape[0]

        self.game_size = grid_size
        self.game_board = self._generate_board(grid_size)
        self.visible_buildings = {
            "top_to_bottom": grid[0],
            "left_to_right": grid[1],
            "right_to_left": grid[2],
            "bottom_to_top": grid[3] 
        }
        self.name = file_path.name

    def _generate_board(self, board_size: int) -> np.ndarray:
        """Generates an initial board"""
        board = np.empty((board_size, board_size), dtype=object)
        for i, row in enumerate(board):
            for j, _ in enumerate(row):
                board[i, j] = Square(0, list(i + 1 for i in range(board_size)), (i, j))
        return board


    def display(self, solved: bool | None = None):
        colours = cm.tab20(range(self.game_size))
        display_size = self.game_size + 2

        _, ax = plt.subplots(figsize=(display_size, display_size))

        def place_rect(x: int, y: int, symbol: str = "", sub_values: list = [], colour: str = "white"):
            rect = plt.Rectangle((y, display_size -x -1), 1, 1, facecolor=colour, edgecolor='black')
            ax.add_patch(rect)
            
            if symbol:
                ax.text(y + 0.5, display_size - x - 0.5, symbol, ha="center", va="center", fontsize=25, color="black", fontweight='bold')
            
            if sub_values:
                # Sub values - display max 4 per line
                max_per_line = 4
                split_sub_values = [sub_values[i:i + max_per_line] for i in range(0, len(sub_values), max_per_line)]
                lines = "\n".join(", ".join(map(str, line)) for line in split_sub_values)
                
                margin = 0.05
                ax.text(y + 1 - margin, display_size - x - margin, lines, ha="right", va="top", fontsize=7, color="black")

        def draw_border_row(values: list, is_top: bool):
            for i, val in enumerate(values):
                x, y = (0, i + 1) if is_top else (display_size - 1, i + 1)
                place_rect(x, y, str(val) if val else "", colour="white" if val else "black")

        def draw_border_col(values: list, is_left: bool):
            for i, val in enumerate(values):
                x, y = (i + 1, 0) if is_left else (i + 1, display_size - 1)
                place_rect(x, y, str(val) if val else "", colour="white" if val else "black")
        
        # Game tiles
        for i in range(self.game_size):
            for j in range(self.game_size):
                value = self.game_board[i, j].shape_value
                sub_values = self.game_board[i, j].sub_values
                shape_symbol = str(value) if value else ""
                shape_colour = colours[value - 1] if value else "white"
                place_rect(i + 1, j + 1, shape_symbol, sub_values, shape_colour)
        
        # Rule Tiles
        # Corners
        for x in [0, display_size - 1]:
            for y in [0, display_size - 1]:
                place_rect(x, y, "", colour="black")
        
        # Border
        draw_border_row(self.visible_buildings["top_to_bottom"], is_top=True)
        draw_border_row(self.visible_buildings["bottom_to_top"], is_top=False)
        draw_border_col(self.visible_buildings["left_to_right"], is_left=True)
        draw_border_col(self.visible_buildings["right_to_left"], is_left=False)

        ax.set_ylim(0, display_size)
        ax.set_xlim(0, display_size)
        ax.grid(False)
        ax.axis("off")
        ax.set_aspect('equal')
        title = f"{'Solved!' if solved else 'Failed...'}\n" if solved is not None else ""
        ax.set_title(title + self.name)

        plt.show()

def read_board(file_path: Path) -> Board:
    """Create a Board object from a csv file path"""
    data_txt = file_path.read_text()
    start_grid = np.genfromtxt(StringIO(data_txt), delimiter=",", dtype=int)
    return Board(start_grid, file_path)
