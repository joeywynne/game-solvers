from bs4 import BeautifulSoup
from io import StringIO
import re
import json
import numpy as np
from game_solvers.request_handler import get_page
from game_solvers.logger import LOG
from game_solvers.sporcle_parser import download_sporcle_games

SKYSCRAPER_SEARCH_STR = "Skyscrapers Logic Puzzle"

def parse_skyscraper_game_page(url: str) -> np.ndarray:
    """Parses a single Tree logic puzzle from a url"""
    LOG.info(f"Querying page: {url}")
    page_text = get_page(f"{url}")
    soup = BeautifulSoup(StringIO(page_text), "html.parser")
    scripts_js = soup.find_all("script", {"type": "text/javascript"})

    for script in scripts_js:
        if "payload" in script.text and "allCells" in script.text:
            break
        
    # Extract the JavaScript variable
    pattern = r"window\._payload\s*=\s*(\{.*\})"
    match = re.search(pattern, script.text, re.DOTALL)
    if not match:
        raise ValueError("Could not find window._payload in page.")
    
    json_str = match.group(1)
    json_info = json.loads(json_str)
    grid_size = json_info["colCount"] - 2
    cells = json_info["allCells"]
    # key is coordinate pair e.g. 0,0
    # x,y is distance from top left
    # value.text contains the hints (if is digit)
    # Also value.x and value.y can find coordinates
    # Note we swap x and y for numpy grid ref
    visible_squares = {
        (value["y"], value["x"]): value["text"]
        for value in cells.values()
        if "pre_visible" in value["options"] and value["options"]["pre_visible"] == 'true'
    }

    # Aim to save a csv form with the 4 rows representing the clues
    top = [visible_squares.get((0, i + 1), 0) for i in range(grid_size)]
    left = [visible_squares.get((i + 1, 0), 0) for i in range(grid_size)]
    right = [visible_squares.get((i + 1, grid_size + 1), 0) for i in range(grid_size)]
    bottom = [visible_squares.get((grid_size + 1, i + 1), 0) for i in range(grid_size)]

    # Now add the game grid
    game_grid = np.zeros((grid_size, grid_size), dtype=int)
    for square, value in visible_squares.items():
        if square[0] == 0 or square[0] == grid_size + 1:
            continue
        if square[1] == 0 or square[1] == grid_size + 1:
            continue
        game_coords = tuple(s - 1 for s in square)
        game_value = alpha_to_num(value)
        game_grid[game_coords] = game_value

    return np.concatenate(
        [
            np.array([top, left, right, bottom]).astype(int),
            game_grid
        ], axis=0
    )


def alpha_to_num(char: str | float | int) -> int:
    """Convert data to int."""
    if isinstance(char, (int, float)) or char.isdigit():
        return int(char)
    else:
        #  a: 1, b: 2 etc...
        return ord(char.upper()) - 64


if __name__ == "__main__":
    download_sporcle_games(SKYSCRAPER_SEARCH_STR, parse_skyscraper_game_page, "skyscraper_logic_puzzles")
    #d = parse_skyscraper_game_page("https://www.sporcle.com/games/Katie_Wandering/skyscrapers-logic-puzzle-16")
    #print(d)
