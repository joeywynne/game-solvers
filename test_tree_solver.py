"""Test the tree solver against all of the puzzles in the folder"""
from sporcle_tree_logic_parser import DOWNLOAD_BASE_PATH
from tree_logic_solver import read_board, solve_board
import time
from logger import set_log_level, LOG
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


set_log_level(LOG, "WARN")

score_count = {
    "solved": 0,
    "failed": 0
}

progress_bar = Progress(
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    BarColumn(),
    MofNCompleteColumn(),
    TextColumn("•"),
    TimeElapsedColumn(),
    TextColumn("•"),
    TimeRemainingColumn(),
)

start = time.time()
with progress_bar as p:
    task = p.add_task("Solving...", total=len(list(DOWNLOAD_BASE_PATH.iterdir())))

    for file_path in DOWNLOAD_BASE_PATH.iterdir():
        board = read_board(file_path)
        solved = solve_board(board)

        if solved:
            score_count["solved"] += 1
        else:
            score_count["failed"] += 1

        p.advance(task)

total_tests = sum(score_count.values())
end = time.time()

print("Results:")
print(f"Number of tests ran: {total_tests}")
print(f"Solved: {score_count["solved"]} ({100 * score_count["solved"] / total_tests :2f}%)")
print(f"Failed: {score_count["failed"]} ({100 * score_count["failed"] / total_tests :2f}%)")
print()
print(f"Tests ran in: {end - start} seconds")
