"""
Logic - ask mary
1. If Column, row or shape has only one option - fill it with T
2. If placing a T would block a shape from being able to have a T, it can not be a T
3. If all of shape in one row/column then all other squares in that row/column are -
4. If 2 shapes exist only in 2 columns/rows then all others in those rows/columns are - (same as 2 but for n=2, n=3 etc)

Make a move
1. If adding -, then nothing
2. If adding T then fill the rest of the shape, row, column and surroundings with -

Add logger to explain the moves made (narration)
- outlines of shapes
"""
from board import read_board, Board
import numpy as np
from pathlib import Path

def solve_board(board: Board) -> bool:
    """Main loop to solve the board."""
    while not board.is_solved:
        changes = [
            is_only_one_square_available(board),
            square_blocks_all_of_shape(board),
            is_row_col_single_colour(board)
        ]
        if any(changes):
            continue
        return False
    return True
        
def is_only_one_square_available(board: Board) -> bool:
    """Place a T if there is only one square available in a row, column or square."""

    def check_one_square_available(group_to_scan: np.ndarray | list) -> bool:
        """For any given group check whether only one square is available

        Returns: int index if one square, else -1
        
        Here group is row/col/shape
        """
        available_idx = np.where([g.symbol_id == 0 for g in group_to_scan])[0]
        if len(available_idx) != 1:
            return False
        board.place_tree(group_to_scan[available_idx[0]].coords)
        return True

    # row
    for row in board.board_state:
        res = check_one_square_available(row)
        if res:
            return res
    
    # col
    for col in board.board_state.T:
        res = check_one_square_available(col)
        if res:
            return res
    
    # Shape
    groups = board.get_groups()
    for group_squares in groups.values():
        res = check_one_square_available(group_squares)
        if res:
            return res

    return False
        
        
def square_blocks_all_of_shape(board: Board) -> bool:
    """If square being tree blocks all of another shape it is not a tree."""
    empty_squares = board.get_empty_squares()
    groups = board.get_groups()

    for square in empty_squares:
        blocked_squares = board.get_blocked_squares(square)

        for group_id, group in groups.items():
            if square.shape_id == group_id:
                # Don't check the square's own group
                continue
            # 2 is T
            if any(s.symbol_id == 2 for s in group):
                # This group is not blocked
                continue

            available_squares = [
                s for s in group if s.symbol_id == 0 and s not in blocked_squares
            ]
            if not available_squares:
                # Group has no available squares and has no T - SQUARE BLOCKS
                board.place_dash(square.coords)
                return True
    return False

def is_row_col_single_colour(board: Board) -> bool:
    """If a row/col is only one colour the rest of the shape cannot be a tree
    
    Note we only consider available squares.
    """
    def check_group_single_colour(group_to_scan: np.ndarray | list) -> bool:
        """For any given group check whether only one square is available

        Returns: int index if one square, else -1
        
        Here group is row/col
        """
        available_msk = [g.symbol_id == 0 for g in group_to_scan]
        available_squares = group_to_scan[available_msk]
        if len(available_squares) == 0:
            # Nothing available, nothing to do here
            return False

        shape_ids = [s.shape_id for s in available_squares]
        if all([s == shape_ids[0] for s in shape_ids]):
            # We have a group with only one shape_id.
            # All other values in this shape must be dashes
            shape = board.get_squares_of_shape(shape_id=shape_ids[0])

            squares_to_update = [s for s in shape if s not in group_to_scan]
            if all(s.symbol_id != 0 for s in squares_to_update):
                return False
            for square in squares_to_update:
                board.place_dash(square.coords)
            return True

    for row in board.board_state:
        res = check_group_single_colour(row)
        if res:
            return res
        
    # cols
    for col in board.board_state.T:
        res = check_group_single_colour(col)
        if res:
            return res
    return False


# TODO: add selection of data sample
# TODO: add logging of how we solved
# TODO: add tests

suffixes = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]
if __name__ == "__main__":
    for suffix in suffixes:
        csv_path = Path("sporcle_games")/"tree_logic_puzzles"/f"trees-logic-puzzle-{suffix}.csv"
        board = read_board(csv_path)
        solved = solve_board(board)
        board.display(solved)