from pathlib import Path
from itertools import combinations
import re
import pandas as pd
import numpy as np
import json
from bs4 import BeautifulSoup
from game_solvers.logger import LOG
from game_solvers.request_handler import get_page
from io import StringIO


SPORCLE_URL = "https://www.sporcle.com"
KATIE_QUIZZES_BASE = f"{SPORCLE_URL}/user/Katie_Wandering/quizzes"
SPORCLE_GAMES_BASE = f"{SPORCLE_URL}/games"
DOWNLOAD_BASE_PATH = (Path(__file__).parent / "../game_data").resolve()

COLOUR_SIMILARITY_THRESH = 30

def download_sporcle_games(search_str: str, parser: callable, download_folder: str, limit: int=-1):
    """Loop over all sporcle games and download. Saving as CSV"""
    
    puzzle_links = get_sporcle_puzzle_links(KATIE_QUIZZES_BASE, search_str) + get_sporcle_puzzle_links(f"{KATIE_QUIZZES_BASE}/published", search_str)
    for i, link in enumerate(puzzle_links):
        if i >= limit and limit >= 0:
            return
        name = link.split("/")[-1]
        LOG.info(f"Creating csv for {link}")
        game = parser(link)
        save_grid_as_csv(game, f"{download_folder}/{name}.csv")

def get_sporcle_puzzle_links(base_url: Path, search_str: str) -> list[str]:
    """Returns a list of all urls relating to logic puzzles"""
    # each page is /2 /3 /4 etc
    puzzle_urls = []
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
                LOG.info(f"Found {len(puzzle_urls)}")
                return puzzle_urls

            for quiz in quiz_list:
                if not quiz["game_name"].startswith(search_str):
                    continue
                puzzle_urls.append(f"{SPORCLE_GAMES_BASE}/{quiz['game_url']}")

        page += 1

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
            r, g, b, a = groups
            return (int(r), int(g), int(b), float(a))
        else:
            r, g, b = groups
        return (r, g, b, 1)
    h = hex_code.lstrip("#")
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return (rgb[0], rgb[1], rgb[2], 1)


def save_grid_as_csv(grid: np.ndarray, csv_path_end: Path) -> None:
    df = pd.DataFrame(grid)
    df.to_csv(DOWNLOAD_BASE_PATH / csv_path_end, header=False, index=False)