"""
Logic - ask mary
1. If Column, row or shape has only one option - fill it with T         (done)
2. If placing a T would block a shape from being able to have a T, it can not be a T        (done)
3. If all of shape in one row/column then all other squares in that row/column are -        (done)
5. If a row/col contains only 2 colours then the rest of these colours are - (extends to n=3, n=4 etc.)
4. If 2 shapes exist only in 2 columns/rows then all others in those rows/columns are - (same as 3 but for n=2, n=3 etc)    (done)


Make a move
1. If adding -, then nothing
2. If adding T then fill the rest of the shape, row, column and surroundings with -

Add logger to explain the moves made (narration)
- outlines of shapes
"""
from board import read_board, Board
import numpy as np
from logger import LOG
from itertools import combinations
from sporcle_tree_logic_parser import DOWNLOAD_BASE_PATH
from pathlib import Path
from copy import deepcopy

def solve_board(board: Board) -> bool:
    """Main loop to solve the board."""
    while board.is_live:
        # We restart the loop if any of the rules causes a change
        # Try to run cheap tests first
        if is_only_one_square_available(board):
            continue

        if square_blocks_all(board):
            continue

        for n in range(1, board.board_state.shape[0] + 1):
            if any_n_rows_cols_only_n_colours(board, n):
                break
            if n == 1:
                continue
            if any_n_shapes_exist_in_n_rows_cols(board, n):
                break
        
        # None of the strategies made progress
        # find a contradiction in one of the available options
        if find_contradiction(board):
            continue

        else:
            # No solution found
            return False

    return board.is_solved
        
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
        
        
def square_blocks_all(board: Board) -> bool:
    """If square being tree blocks all of another shape/row/col it is not a tree.

    This is rule 2 but also does 3.
    
    Note: doesn't count if it blocks its own shape/col/row
    """
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

        # rows
        row_idx, col_idx = square.coords
        for idx, row in enumerate(board.board_state):
            if idx == row_idx:
                continue
            available_row = [s for s in row if s.symbol_id == 0]
            if available_row and all(s in blocked_squares for s in available_row):
                board.place_dash(square.coords)
                LOG.info(f"Square at {square.coords} would block entire row {idx}. Placing a dash.")
                return True
        
        # cols
        for idx, col in enumerate(board.board_state.T):
            if idx == col_idx:
                continue
            available_col = [s for s in col if s.symbol_id == 0]
            if available_col and all(s in blocked_squares for s in available_col):
                board.place_dash(square.coords)
                LOG.info(f"Square at {square.coords} would block entire column {idx}. Placing a dash.")
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
           i: set(s.shape_id for s in available_squares)
           for i, available_squares in available_squares_per_group.items()
        }
        
        # Need to check each group has the same unique shape ids
        # and length is equal to num_colours
        first = unique_shape_ids[0]
        if all(first == u for u in unique_shape_ids.values()) and len(first) == num_colours:
            # We have a group with exactly <num_colours> shape_ids.
            # All other values in these shapes must be dashes
            shape_squares = {
                square.coords for i in first for square in board.get_squares_of_shape(shape_id=i)
                if square.symbol_id == 0
            }
            group_squares = {s.coords for group in groups_to_scan for s in group}
            squares_to_update = shape_squares.difference(group_squares)

            if not squares_to_update:
                return False
            for square_coords in squares_to_update:
                board.place_dash(square_coords)
            return True

    success_log_msg = "The squares in {} numbers {} only contain squares from {} shapes. The rest of the shapes are dashes."

    for row_idxs in combinations(range(board.size), num_colours):
        selected_rows = [board.board_state[i] for i in row_idxs]
        res = check_group_n_colours(selected_rows, num_colours=num_colours)
        if res:
            LOG.info(success_log_msg.format("row", row_idxs, num_colours))
            return True
        
    # cols
    for col_idxs in combinations(range(board.size), num_colours):
        selected_cols = [board.board_state[:, i] for i in col_idxs]
        res = check_group_n_colours(selected_cols, num_colours=num_colours)
        if res:
            LOG.info(success_log_msg.format("col", col_idxs, num_colours))
            return True
    return False

def any_n_shapes_exist_in_n_rows_cols(board: Board, num_shapes: int) -> bool:
    """If N shapes only exist in N rows/cols any other shapes in those columns is -
    
    Note we only consider available squares.
    Don't need to consider n=1
    """
    def check_colour_n_groups(shape_squares: list) -> set:
        """For any N shapes if they are only in N rows/cols the rest of the row/col must be -
        """
        squares = [item for sublist in shape_squares for item in sublist]
        row_idxs = set(square.coords[0] for square in squares)
        if len(row_idxs) == len(shape_squares):
            selected_rows = [board.board_state[i] for i in row_idxs]
            coords_to_update = [s.coords for s in selected_rows if s not in squares]
            for coord in coords_to_update:
                board.place_dash(coord)
            return row_idxs, "rows"
        
        col_idxs = set(square.coords[1] for square in squares)
        if len(col_idxs) == len(shape_squares):
            selected_cols = [board.board_state.T[i] for i in col_idxs]
            coords_to_update = [s.coords for s in selected_cols if s not in squares]
            for coord in coords_to_update:
                board.place_dash(coord)
            return col_idxs, "columns"
        return set(), None
        
    for shapes in combinations(board.get_groups().items(), num_shapes):
        shape_idx, shape_squares = zip(*[shapes[i] for i in range(num_shapes)])
        group_idx, group_type = check_colour_n_groups(shape_squares)
        if group_idx:
            LOG.info(f"Shapes {shape_idx} exist only in {group_type} {group_idx} all other squares in these {group_type} are dashes.")
            return True
    return False

def find_contradiction(board: Board) -> bool:
    """Attempt to locate a contradiction by recursively solving
    
    Try the groups with smallest number of possibilities first
    """
    sorted_possibilities = get_sorted_possibilities(board)
    for p in sorted_possibilities:
        for square in p:
            board_copy = deepcopy(board)
            board_copy.place_tree(square.coords)
            LOG.info(f"Attempting to place a tree at {square.coords}")
            # Check contradiction
            solved_copy = solve_board(board_copy)

            if solved_copy:
                LOG.info(f"Attempt to place a tree at {square.coords} was successful")
                # Replace the original with the solved version
                board.set_board_state(board_copy.board_state)
                return True

            else:
                LOG.info(f"Attempt to place a tree at {square.coords} was unsuccessful")
                if board_copy.is_valid():
                    # Can't say anything - no evidence. Try the next
                    LOG.info("No contradiction - trying next option")
                    continue
                LOG.info("Contradiction - place a -")
                board.place_dash(square.coords)
                return True

def get_sorted_possibilities(board: Board) -> list[list]:
    """Return a list of options to try.
    
    Rows/Cols/Groups where no symbol placed
    Sorted on length of the list of possible squares in the option
    """
    possibilities = []
    for row in board.board_state:
        avail_row = [r for r in row if r.symbol_id == 0]
        if avail_row:
            possibilities.append(avail_row)
    for col in board.board_state.T:
        avail_col = [c for c in col if c.symbol_id == 0]
        if avail_col:
            possibilities.append(avail_col)
    for group in board.get_groups().values():
        avail_group = [g for g in group if g.symbol_id == 0]
        if avail_group:
            possibilities.append(avail_group)
    # sort list by length of the options
    return sorted(possibilities, key= lambda x: len(x))


# TODO: add selection of data sample
# TODO: add logging of how we solved
# TODO: add tests
if __name__ == "__main__":

    for csv_path in DOWNLOAD_BASE_PATH.iterdir():
        board = read_board(csv_path)
        solved = solve_board(board)
        if not solved:
            board.display(sub_title=str(csv_path))
            exit()


# 174 fails - obvious....