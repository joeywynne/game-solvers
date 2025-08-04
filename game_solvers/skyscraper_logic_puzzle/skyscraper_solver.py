from board import read_board, Board, Square
import numpy as np
from game_solvers.logger import LOG
from game_solvers.sporcle_parser import DOWNLOAD_BASE_PATH
from pathlib import Path
from itertools import product


SKYSCRAPER_PUZZLES_PATH = DOWNLOAD_BASE_PATH / "skyscraper_logic_puzzles"

def solve_board(board: Board) -> bool:
    """Main loop to solve the board."""
    # Rules to run once
    buildings_seen_limits_max_square_value(board)

    while board.is_live:
        changed = any(
            [
                square_has_one_possible_value(board),
                value_in_group_has_one_possible_square(board),
            ]
        )
        if changed:
            continue

        # Last one to try
        if not if_rule_try_the_options(board):
            break


    return board.is_solved


def square_has_one_possible_value(board: Board) -> bool:
    """If a square only has one possible value, assign it."""
    # Check all squares
    updated = False
    for square in board.all_squares(active=True):
        sub_values = square.sub_values
        if len(square.sub_values) == 1:
            square_coords = square.coords
            value = sub_values[0]
            board.assign_value(square_coords, value)
            LOG.info(f"Square at {square_coords} has only one possible value: {value}")
            updated = True
    return updated


def value_in_group_has_one_possible_square(board: Board) -> bool:
    """If a value in a row/col can only fit in one square, assign it."""

    def has_one_possible_square(group: np.ndarray) -> list[tuple[Square, int]]:
        """Return (Square, value) pairs where value appears only once in sub_values."""
        all_values = np.concatenate([sq.sub_values for sq in group])
        values, counts = np.unique_counts(all_values)
        return [
            (square, int(value))
            for value, count in zip(values, counts)
            for square in group
            if count == 1 and value in square.sub_values
        ]

    updated = False
    success_log_msg = "In {} {} the value {} is only possible in square at {}."

    for axis, label  in zip([board.board_state, board.board_state.T], ["row", "column"]):
        for idx, group in enumerate(axis):
            candidates = has_one_possible_square(group)
            for square, value in candidates:
                if square.shape_value != 0:
                    # already assigned
                    continue
                updated = True
                LOG.info(success_log_msg.format(label, idx, value, square.coords))
                board.assign_value(square.coords, value)

    return updated


def if_rule_try_the_options(board: Board) -> bool:
    """If we have a rule and squares available - try all options."""
    updated = False
    for direction, rules in board.visible_buildings.items():
        for idx, rule in enumerate(rules):
            if rule == 0:
                # 0 represents no rule
                continue
            group = board.get_group(direction, idx)
            unplaced = np.where([g.shape_value == 0 for g in group])[0]
            if len(unplaced) == 0:
                # Group is complete
                continue
            valid_options = attempt_to_fit_buildings(group, unplaced, rule)
            
            for id, option in valid_options.items():
                square = group[id]
                if square.sub_values != list(option):
                    updated = True
                    # TODO improve this log message (detail)
                    LOG.info("Updating group with valid options")
                    square.sub_values = list(option)
    return updated



def attempt_to_fit_buildings(group: np.ndarray, unplaced: np.ndarray, rule: int) -> dict:
    """Attempt to recursively find a solution for a row.
    
    Return a dict of idx -> sub_values.
    """
    results = {u: set() for u in unplaced}
    sub_values = (g.sub_values for g in group[unplaced])
    all_candidates = product(*sub_values)
    # Filter out all_candidates with duplicates
    all_candidates = [sublist for sublist in all_candidates if len(sublist) == len(set(sublist))]
    
    for candidate in all_candidates:
        unplaced_iter = iter(candidate)
        test_group = [
            g.shape_value if i not in unplaced else next(unplaced_iter)
            for i, g in enumerate(group)
        ]
        is_valid = (calc_number_buildings_seen(test_group) == rule)
        if not is_valid:
            continue

        for i, candidate in enumerate(test_group):
            if i in results:
                results[i].add(candidate)
    return results


def calc_number_buildings_seen(building_group: np.ndarray) -> int:
    """Calculate the number of buildings seen from the start."""
    highest_seen = building_group[0]
    count = 1
    for building in building_group[1:]:
        if building > highest_seen:
            count += 1
            highest_seen = building
    return count

def buildings_seen_limits_max_square_value(board: Board) -> None:
    """If x buildings seen then tallest building in square one is 2 + N - r + i
    N = Grid size
    r = Rule
    i = square index
    
    E.g.
    If only one building is seen, the first building is the tallest (blocks the rest).
    
    Run once.
    """
    LOG.info("Applying max limits to rows and columns based on the rules")
    for direction, rules in board.visible_buildings.items():
        for idx, rule in enumerate(rules):
            if rule == 0:
                # 0 represents no rule
                continue
            max_allowed_value = 1 + board.game_size - rule # + idx
            # Group is in correct direction based on viewing
            group = board.get_group(direction, idx)
            for idx, g in enumerate(group):
                g.sub_values = [s for s in g.sub_values if s <= max_allowed_value + idx]


if __name__ == "__main__":
    for csv_path in SKYSCRAPER_PUZZLES_PATH.iterdir():
        csv_path = SKYSCRAPER_PUZZLES_PATH / "skyscrapers-logic-puzzle-i.csv"
        board = read_board(csv_path)
        solved = solve_board(board)
        if not solved or solved:
            board.display(solved)
            exit()