"""
Logic - ask mary
1. If Column, row or shape has only one option - fill it with T
2. If placing a T would block a shape from being able to have a T, it can not be a T
2. If all of shape in one row/column then all other squares in that row/column are -
3. If 2 shapes exist only in 2 columns/rows then all others in those rows/columns are - (same as 2 but for n=2, n=3 etc)

Make a move
1. If adding -, then nothing
2. If adding T then fill the rest of the shape, row, column and surroundings with -

Add logger to explain the moves made (narration)
Add display
- with coloured grid
- before and after
- outlines of shapes
"""
from board import read_board, Board
from pathlib import Path
import numpy as np

EXAMPLES = Path("examples")

def solve_board(board: Board) -> bool:
    """Main loop to solve the board."""
    while not board.is_solved:
        changes = [
            is_only_one_square_available(board),
            square_blocks_all_of_shape(board)
        ]
        if any(changes):
            continue
        return False
    return True
        
def is_only_one_square_available(board: Board) -> bool:
    """Place a T if there is only one square available in a row, column or square."""

    # row
    for row_idx, row in enumerate(board.board_state):
        available_idx = np.where([r.symbol_id == 0 for r in row])[0]
        if len(available_idx) == 1:
            # 1 available - this is a tree
            board.place_tree((row_idx, available_idx[0]))
            return True
    
    # col
    for col_idx, col in enumerate(board.board_state.T):
        available_idx = np.where([c.symbol_id == 0 for c in col])[0]
        if len(available_idx) == 1:
            # 1 available - this is a tree
            board.place_tree((available_idx[0], col_idx))
            return True
    
    # Shape
    groups = board.get_groups()
    for group_squares in groups.values():
        available_idx = np.where([s.symbol_id == 0 for s in group_squares])[0]
        if len(available_idx) == 1:
            # 1 available - this is a tree
            board.place_tree((group_squares[available_idx[0]].coords))
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
                return True
    return False

# TODO: add selection of data sample
# TODO: add logging of how we solved
# TODO: add method of generating tree puzzles
# TODO: add tests

for i in range(5):
    board = read_board(EXAMPLES / f"{i + 1}.csv")
    solved = solve_board(board)
    board.display(solved)