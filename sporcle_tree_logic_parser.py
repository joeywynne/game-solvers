from bs4 import BeautifulSoup
from io import StringIO
import re
import json
import numpy as np
from request_handler import get_page
from logger import LOG
from sporcle_parser import clean_square_colours, save_grid_as_csv, get_sporcle_puzzle_links, KATIE_QUIZZES_BASE

def parse_tree_game_page(url: str) -> np.ndarray:
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


def download_sporcle_tree_games(limit: int=-1):
    """Loop over all sporcle games and download. Saving as CSV"""
    puzzle_tree_links = get_sporcle_puzzle_links(KATIE_QUIZZES_BASE, "Trees Logic Puzzle") + get_sporcle_puzzle_links(f"{KATIE_QUIZZES_BASE}/published", "Trees Logic Puzzles")
    for i, link in enumerate(puzzle_tree_links):
        if i >= limit and limit >= 0:
            return
        name = link.split("/")[-1]
        LOG.info(f"Creating csv for {link}")
        tree_game = parse_tree_game_page(link)
        save_grid_as_csv(tree_game, f"{name}.csv")


if __name__ == "__main__":
    download_sporcle_tree_games()