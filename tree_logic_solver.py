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
from logger import LOG
from itertools import combinations

def solve_board(board: Board) -> bool:
    """Main loop to solve the board."""
    while not board.is_solved:
        changes = [
            is_only_one_square_available(board),
            square_blocks_all_of_shape(board),
            any_n_rows_cols_only_n_colours(board, 1),
            any_n_rows_cols_only_n_colours(board, 2)
        ]
        if any(changes):
            continue
        return False
    return True
        
def is_only_one_square_available(board: Board) -> bool:
    """Place a T if there is only one square available in a row, column or square."""

    def check_one_square_available(group_to_scan: np.ndarray | list) -> tuple:
        """For any given group check whether only one square is available.
        
        Here group is row/col/shape
        """
        available_idx = np.where([g.symbol_id == 0 for g in group_to_scan])[0]
        if len(available_idx) != 1:
            return tuple()
        coords = group_to_scan[available_idx[0]].coords
        board.place_tree(coords)
        return coords

    success_log_message = "Only one available spot found for {} number {} with coordinates {}. Placing a tree."
    # row
    for row_idx, row in enumerate(board.board_state):
        res = check_one_square_available(row)
        if res:
            LOG.info(success_log_message.format("row", row_idx, str(res)))
            return True
    
    # col
    for col_idx, col in enumerate(board.board_state.T):
        res = check_one_square_available(col)
        if res:
            LOG.info(success_log_message.format("col", col_idx, str(res)))
            return True
    
    # Shape
    groups = board.get_groups()
    for group_id, group_squares in groups.items():
        res = check_one_square_available(group_squares)
        if res:
            LOG.info(success_log_message.format("shape", group_id, str(res)))
            return True

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
                LOG.info(f"The square at {square.coords} would block shapes if it was a tree. Placing a dash")
                return True
    return False

def any_n_rows_cols_only_n_colours(board: Board, num_colours: int) -> bool:
    """If a group of n rows/cols is made of the same n colours the rest of those n shapes are dashes.
    
    Note we only consider available squares.
    """
    def check_group_n_colours(groups_to_scan: np.ndarray | list, num_colours: int) -> bool:
        """For any given group check it is made up of the exactly <num_colours> colours.
        
        The colours must be the same in each row
        Here group is row/col
        """
        available_squares_per_group = {
            i: [g for g in group if g.symbol_id == 0]
            for i, group in enumerate(groups_to_scan)
        }

        if any(len(available_squares) == 0 for available_squares in available_squares_per_group.values()):
            # Nothing available, nothing to do here
            return False

        unique_shape_ids = {
           i: np.unique([s.shape_id for s in available_squares])
           for i, available_squares in available_squares_per_group.items()
        }
        
        # Need to check each group has the same unique shape ids
        # and length is equal to num_colours
        first = list(unique_shape_ids.values())[0]
        if all(np.array_equal(first, u) for u in unique_shape_ids.values()) and len(first) == num_colours:
            # We have a group with exactly <num_colours> shape_ids.
            # All other values in these shapes must be dashes
            shape_squares = [square for i in first for square in board.get_squares_of_shape(shape_id=i)]

            squares_to_update = [s for s in shape_squares if s not in groups_to_scan.flatten()]
            if all(s.symbol_id != 0 for s in squares_to_update):
                return False
            for square in squares_to_update:
                board.place_dash(square.coords)
            return True

    success_log_msg = "The squares in {} numbers {} only contain squares from {} shapes. The rest of the shapes are dashes."
    for rows in combinations(board.board_state, num_colours):
        res = check_group_n_colours(np.vstack(rows), num_colours=num_colours)
        if res:
            row_numbers = [i.coords[0] for i in np.vstack(rows)[:, 0]]

            LOG.info(success_log_msg.format("row", row_numbers, num_colours))
            return True
        
    # cols
    for cols in combinations(board.board_state.T, num_colours):
        res = check_group_n_colours(np.vstack(cols), num_colours=num_colours)
        if res:
            col_numbers = [i.coords[1] for i in np.vstack(cols)[:, 0]]
            LOG.info(success_log_msg.format("col", col_numbers, num_colours))
            return True
    return False


# TODO: add selection of data sample
# TODO: add logging of how we solved
# TODO: add tests

suffixes = ["vi"] # ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]
if __name__ == "__main__":
    for suffix in suffixes:
        csv_path = Path("sporcle_games")/"tree_logic_puzzles"/f"trees-logic-puzzle-{suffix}.csv"
        board = read_board(csv_path)
        solved = solve_board(board)
        board.display(solved)