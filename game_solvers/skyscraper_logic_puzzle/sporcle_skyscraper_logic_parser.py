from bs4 import BeautifulSoup
from io import StringIO
import re
import json
import numpy as np
from game_solvers.request_handler import get_page
from game_solvers.logger import LOG
from game_solvers.sporcle_parser import download_sporcle_games
from math import sqrt

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
    cells = json_info["allCells"]
    grid_size = int(sqrt(json_info["activeCellCount"]))  # always a perfect square
    # key is coordinate pair e.g. 0,0
    # x,y is distance from top left
    # value.text contains the hints (if is digit)
    # Also value.x and value.y can find coordinates
    # Note we swap x and y for numpy grid ref
    squares = {
        (value["y"], value["x"]): int(value["text"]) if value["text"].isdigit() else ""
        for value in cells.values()
    }

    # Aim to save a csv form with the 4 rows representing the clues
    top = [squares.get((0, i + 1), 0) for i in range(grid_size)]
    left = [squares.get((i + 1, 0), 0) for i in range(grid_size)]
    right = [squares.get((i + 1, grid_size + 1), 0) for i in range(grid_size)]
    bottom = [squares.get((grid_size + 1, i + 1), 0) for i in range(grid_size)]

    return np.array([top, left, right, bottom])


if __name__ == "__main__":
    download_sporcle_games(SKYSCRAPER_SEARCH_STR, parse_skyscraper_game_page, "skyscraper_logic_puzzles")
