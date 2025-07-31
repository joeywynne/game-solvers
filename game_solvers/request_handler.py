import requests
import socket
import urllib3
import warnings

WORK_PROXY = "127.0.0.1"
WORK_PROXY_PORT = "9000"


def get_page(url: str) -> ...:
    "Request and return a page based on a url"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }

    proxies = None
    if is_office_network():
        proxy_url = f"http://{WORK_PROXY}:{WORK_PROXY_PORT}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, headers=headers, proxies=proxies, verify=False)
        response.raise_for_status()
        return response.text


def is_office_network():
    """
    Heuristic to detect if we're on office network:
    - Can use proxy presence (127.0.0.1:9000)
    - OR DNS suffix, hostname, IP, etc.
    """
    try:
        # Try to open a connection to local proxy (fast check)
        sock = socket.create_connection((WORK_PROXY, WORK_PROXY_PORT), timeout=1)
        sock.close()
        return True
    except Exception:
        return False
