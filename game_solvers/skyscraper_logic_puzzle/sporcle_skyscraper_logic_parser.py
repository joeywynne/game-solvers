from bs4 import BeautifulSoup
from io import StringIO
import re
import json
import numpy as np
from game_solvers.request_handler import get_page
from game_solvers.logger import LOG
from game_solvers.sporcle_parser import clean_square_colours, download_sporcle_games

SKYSCRAPER_SEARCH_STR = "Skyscrapers Logic Puzzle"

def parse_skyscraper_game_page(url: str) -> np.ndarray:
    """Parses a single Tree logic puzzle from a url"""
    LOG.info(f"Querying page: {url}")
    page_text = get_page(f"{url}")
    soup = BeautifulSoup(StringIO(page_text), "html.parser")
    scripts_js = soup.find_all("script", {"type": "text/javascript"})

    print(scripts_js)

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
    # key is coordinate pair e.g. 0,0
    # x,y is distance from top left
    # value is another dict.
    # value.options.bg_colour used to find groups
    # Also value.x and value.y can find coordinates
    # Note we swap x and y for numpy grid ref
    squares = {
        (value["y"], value["x"]): value["options"]["bg_color"]
        for value in cells.values()
    }

    # Clean the colour mapping first
    squares = clean_square_colours(squares)

    # Create an ordered list of unique colours (preserves insertion order)
    square_colours = list(dict.fromkeys(squares.values()))

    # Determine grid size
    max_row = max(coord[0] for coord in squares) + 1
    max_col = max(coord[1] for coord in squares) + 1

    # Initialize the grid with None
    grid = np.full((max_row, max_col), None, dtype=object)

    # Fill the grid with indices based on colour
    for coord, colour in squares.items():
        try:
            index = square_colours.index(colour)
        except ValueError:
            raise ValueError(f"Colour {colour} not found in square_colours list!")
        grid[coord] = index

    return grid


if __name__ == "__main__":
    download_sporcle_games(SKYSCRAPER_SEARCH_STR, parse_skyscraper_game_page, "skyscraper_logic_puzzles")