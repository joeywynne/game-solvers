from board import read_board, Board, Square
import numpy as np
from game_solvers.logger import LOG
from itertools import combinations
from game_solvers.sporcle_parser import DOWNLOAD_BASE_PATH
from pathlib import Path


SKYSCRAPER_PUZZLES_PATH = DOWNLOAD_BASE_PATH / "skyscraper_logic_puzzles"

def solve_board(board: Board) -> bool:
    """Main loop to solve the board."""
    while board.is_live:
        # Apply to all squares:
        for square in board.all_squares():
            square_coords, value = square_has_one_possible_value(square)
            if square_coords:
                board.assign_value(square_coords, value)

        #for row in board.board_state:
            

        #for col in board.board_state.T:


    return board.is_solved


def square_has_one_possible_value(square: Square) -> tuple[tuple, int]:
    """If a square only has one possible value, assign it."""
    sub_values = square.sub_values
    if len(square.sub_values) == 1:
        LOG(f"Square at {square.coords} has only one possible value - {sub_values[0]}")
        return square.coords, sub_values[0]
    return (), 0


def value_in_group_has_one_possible_square(group: np.ndarray):
    """If a value in a row/col can only fit in one square, assign it"""

if __name__ == "__main__":
    for csv_path in SKYSCRAPER_PUZZLES_PATH.iterdir():
        board = read_board(csv_path)
        solved = solve_board(board)
        if not solved or solved:
            board.display(solved)
            exit()