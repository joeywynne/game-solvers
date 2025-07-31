from board import read_board, Board
import numpy as np
from game_solvers.logger import LOG
from itertools import combinations
from game_solvers.sporcle_parser import DOWNLOAD_BASE_PATH
from pathlib import Path
from copy import deepcopy

csv_path = Path("../game_data/skyscraper_logic_puzzles/skyscrapers-logic-puzzle-i.csv")
board = read_board(csv_path)
board.display()