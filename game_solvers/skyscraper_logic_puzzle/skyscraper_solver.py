from board import read_board, Board
import numpy as np
from game_solvers.logger import LOG
from itertools import combinations
from game_solvers.sporcle_parser import DOWNLOAD_BASE_PATH
from pathlib import Path


SKYSCRAPER_PUZZLES_PATH = DOWNLOAD_BASE_PATH / "skyscraper_logic_puzzles"

def solve_board(board: Board) -> bool:
    """Main loop to solve the board."""
    while board.is_live:
        changed = any(
            [
                square_has_one_possible_value(board),
                value_in_group_has_one_possible_square(board)
            ]
        )
        if not changed:
            break

    return board.is_solved


def square_has_one_possible_value(board: Board) -> bool:
    """If a square only has one possible value, assign it."""
    # Check all squares
    updated = False
    for square in board.all_squares():
        sub_values = square.sub_values
        if len(square.sub_values) == 1:
            square_coords = square.coords
            value = sub_values[0]
            board.assign_value(square_coords, value)
            LOG(f"Square at {square_coords} has only one possible value - {value}")
            updated = True
    return updated


def value_in_group_has_one_possible_square(board: Board) -> bool:
    """If a value in a row/col can only fit in one square, assign it."""

    def has_one_possible_square(group: np.ndarray):
        """Return list of values which occur once in sub_values, with Square"""
        res = []
        all_values = np.concatenate([g.sub_values for g in group])
        values, counts = np.unique_counts(all_values)
        for value, count in zip(values, counts):
            if count != 1:
                continue
            # One possible place for value
            for square in group:
                if value in square.sub_values:
                    res.append(square, value)
        return res

    updated = False
    success_log_msg = "In {} {} the value {} is only possible in square at {}."

    for row_idx, row in enumerate(board.board_state):
        res = has_one_possible_square(row)
        if res:
            updated = True
            for square, value in res:
                coords = square.coords
                LOG.info(success_log_msg.format("row", row_idx, value, coords))
                board.assign_value(square.coords, value)
    
    for col_idx, col in enumerate(board.board_state.T):
        res = has_one_possible_square(col)
        if res:
            updated = True
            for square, value in res:
                coords = square.coords
                LOG.info(success_log_msg.format("column", col_idx, value, coords))
                board.assign_value(square.coords, value)
    return updated


if __name__ == "__main__":
    for csv_path in SKYSCRAPER_PUZZLES_PATH.iterdir():
        csv_path = SKYSCRAPER_PUZZLES_PATH / "skyscrapers-logic-puzzle-i.csv"
        board = read_board(csv_path)
        solved = solve_board(board)
        if not solved or solved:
            board.display(solved)
            exit()