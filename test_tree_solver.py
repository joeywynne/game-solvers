"""Test the tree solver against all of the puzzles in the folder"""
from sporcle_tree_logic_parser import DOWNLOAD_BASE_PATH
from tree_logic_solver import read_board, solve_board
import time


score_count = {
    "solved": 0,
    "failed": 0
}

start = time.time()
for file_path in DOWNLOAD_BASE_PATH.iterdir():
    board = read_board(file_path)
    solved = solve_board(board)
    
    if solved:
        score_count["solved"] += 1
    else:
        score_count["failed"] += 1

total_tests = sum(score_count.values())
end = time.time()

print("Results:")
print(f"Number of tests ran: {total_tests}")
print(f"Solved: {score_count["solved"]} ({100 * score_count["solved"] / total_tests :2f}%)")
print(f"Failed: {score_count["failed"]} ({100 * score_count["failed"] / total_tests :2f}%)")
print()
print(f"Tests ran in: {end - start} seconds")
