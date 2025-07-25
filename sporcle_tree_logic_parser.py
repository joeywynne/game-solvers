from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import re
import json
import numpy as np
from pathlib import Path
from request_handler import get_page

SPORCLE_URL = "https://www.sporcle.com"
KATIE_QUIZZES_BASE = f"{SPORCLE_URL}/user/Katie_Wandering/quizzes"
SPORCLE_GAMES_BASE = f"{SPORCLE_URL}/games"
DOWNLOAD_BASE_PATH = Path("sporcle_games/tree_logic_puzzles")


def get_tree_puzzle_links(base_url: Path) -> list[str]:
    """Returns a list of all urls relating to logic tree puzzles"""
    # each page is /2 /3 /4 etc
    tree_puzzle_urls = []
    page = 1
    first_quiz_on_page = "None"
    while True:
        print(f"Querying page: {base_url}/{page}")
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
    print(f"Querying page: {url}")
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
    colours = np.array(np.unique(list(squares.values())), dtype=str)
    
    max_row = max(coord[0] for coord in squares) + 1
    max_col = max(coord[1] for coord in squares) + 1

    grid = np.full((max_row, max_col), None, dtype=object)
    for coord, color in squares.items():
        grid[coord] = np.where(colours==color)[0].item()
    
    return grid

def save_grid_as_csv(grid: np.ndarray, csv_path: Path) -> None:
    df = pd.DataFrame(grid)
    df.to_csv(csv_path, header=False, index=False)


def download_sporcle_tree_games(limit: int=-1):
    """Loop over all sporcle games and download. Saving as CSV"""
    puzzle_tree_links = get_tree_puzzle_links(KATIE_QUIZZES_BASE) + get_tree_puzzle_links(KATIE_QUIZZES_BASE/"published")
    for i, link in enumerate(puzzle_tree_links):
        if i >= limit and limit >= 0:
            return
        name = link.split("/")[-1]
        print(f"Creating csv for {link}")
        tree_game = parse_tree_game_page(link)
        save_grid_as_csv(tree_game, DOWNLOAD_BASE_PATH/f"{name}.csv")


if __name__ == "__main__":
    download_sporcle_tree_games()