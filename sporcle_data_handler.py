from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import re
import json

from request_handler import get_page

SPORCLE_URL = "https://www.sporcle.com"
KATIE_QUIZZES_BASE = f"{SPORCLE_URL}/user/Katie_Wandering/quizzes"
SPORCLE_GAMES_BASE = f"{SPORCLE_URL}/games"

def parse_tree_logic_game(raw_soup: BeautifulSoup) -> pd.DataFrame:
    pass

def get_tree_puzzle_links() -> list[str]:
    """Returns a list of all urls relating to logic tree puzzles"""
    # each page is /2 /3 /4 etc
    page = 1
    page_text = get_page(f"{KATIE_QUIZZES_BASE}/{page}")
    current_first_game = None
    first_game = None
    while not current_first_game or first_game != current_first_game:
        soup = BeautifulSoup(StringIO(page_text), "html.parser")
        scripts_js = soup.find_all("script", {"type": "text/javascript"})
        
        tree_puzzle_urls = []
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

            current_first_game = first_game
            first_game = quiz_list[0]["game_name"]

            for quiz in quiz_list:
                if not quiz["game_name"].startswith("Trees Logic Puzzle"):
                    continue
                tree_puzzle_urls.append(f"{SPORCLE_GAMES_BASE}/{quiz['game_url']}")

        page += 1
        page_text = get_page(f"{KATIE_QUIZZES_BASE}/{page}")
    return tree_puzzle_urls
    


get_tree_puzzle_links()


