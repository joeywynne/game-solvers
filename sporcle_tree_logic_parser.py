from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import re
import json
import numpy as np
from pathlib import Path
from request_handler import get_page
from logger import LOG
from itertools import combinations

SPORCLE_URL = "https://www.sporcle.com"
KATIE_QUIZZES_BASE = f"{SPORCLE_URL}/user/Katie_Wandering/quizzes"
SPORCLE_GAMES_BASE = f"{SPORCLE_URL}/games"
DOWNLOAD_BASE_PATH = Path("sporcle_games/tree_logic_puzzles")

COLOUR_SIMILARITY_THRESH = 30


def get_tree_puzzle_links(base_url: Path) -> list[str]:
    """Returns a list of all urls relating to logic tree puzzles"""
    # each page is /2 /3 /4 etc
    tree_puzzle_urls = []
    page = 1
    first_quiz_on_page = "None"
    while True:
        LOG.info(f"Querying page: {base_url}/{page}")
        page_text = get_page(f"{base_url}/{page}")
        soup = BeautifulSoup(StringIO(page_text), "html.parser")
        scripts_js = soup.find_all("script", {"type": "text/javascript"})
        
        
        for script in scripts_js:
            if "listRows" not in script.text:
                continue
        
            # Extract the JavaScript variable
            pattern = r"app\.payload\.listRows\s*=\s*(\[\{.*?\}\])"
            match = re.search(pattern, script.text, re.DOTALL)

            if not match:
                raise ValueError("Could not find app.payload.listRows in page.")

            json_str = match.group(1)
            quiz_list = json.loads(json_str)
            
            # Use this to exit loop
            past_first_quiz = first_quiz_on_page
            first_quiz_on_page = quiz_list[0]["game_name"]
            if first_quiz_on_page == past_first_quiz:
                # This is the exit condition - this page is the same as the last
                return tree_puzzle_urls

            for quiz in quiz_list:
                if not quiz["game_name"].startswith("Trees Logic Puzzle"):
                    continue
                tree_puzzle_urls.append(f"{SPORCLE_GAMES_BASE}/{quiz['game_url']}")

        page += 1

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


def clean_square_colours(squares: dict) -> dict:
    """Clean up the colour values for the squares.
    
    All to RGBA format
    Combine similar colours
    """
    # Convert to RGBA
    squares = {
        k : to_rgba(v) for k, v in squares.items()
    }

    unique_colours = set(squares.values())
    print(unique_colours)
    colour_mapping = {}
    for cols in combinations(unique_colours, 2):
        distance = sum(abs(cols[0][i] - cols[1][i]) for i in range(3)) # ignore channel a
        if distance < COLOUR_SIMILARITY_THRESH:
            # Replace the second with the first
            colour_mapping[cols[1]] = cols[0]

    return {
        k : colour_mapping[v] if v in colour_mapping else v
        for k, v in squares.items()
    }


def to_rgba(hex_code: str) -> tuple[int]:
    pattern = r"rgba?\((\d*),(\d*),(\d*),?(0.\d*)?\)"
    match = re.search(pattern, hex_code, re.DOTALL)
    if match:
        groups = match.groups()
        if len(groups) == 4:
            return (int(g) for g in groups)
        else:
            r, g, b = groups
        return (r, g, b, 1)
    h = hex_code.lstrip("#")
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return (rgb[0], rgb[1], rgb[2], 1)


def save_grid_as_csv(grid: np.ndarray, csv_path: Path) -> None:
    df = pd.DataFrame(grid)
    df.to_csv(csv_path, header=False, index=False)


def download_sporcle_tree_games(limit: int=-1):
    """Loop over all sporcle games and download. Saving as CSV"""
    puzzle_tree_links = get_tree_puzzle_links(KATIE_QUIZZES_BASE) + get_tree_puzzle_links(f"{KATIE_QUIZZES_BASE}/published")
    for i, link in enumerate(puzzle_tree_links):
        if i >= limit and limit >= 0:
            return
        name = link.split("/")[-1]
        LOG.info(f"Creating csv for {link}")
        tree_game = parse_tree_game_page(link)
        save_grid_as_csv(tree_game, DOWNLOAD_BASE_PATH/f"{name}.csv")


if __name__ == "__main__":
    download_sporcle_tree_games()