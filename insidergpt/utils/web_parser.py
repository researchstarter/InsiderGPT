import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from googlesearch import search


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def sanitize_url(url):
    return urljoin(url, urlparse(url).path)


def check_local_file_access(url):
    local_prefixes = [
        "file:///",
        "file://localhost",
        "http://localhost",
        "https://localhost",
    ]
    return any(url.startswith(prefix) for prefix in local_prefixes)


def get_response(url, timeout=10) -> tuple:
  
    try:
        # Restrict access to local files
        if check_local_file_access(url):
            raise ValueError("Mahalliy fayllarga kirish cheklangan")

        # Most basic check if the URL is valid:
        if not url.startswith("http://") and not url.startswith("https://"):
            raise ValueError("URL formati noto‘g‘ri")

        sanitized_url = sanitize_url(url)

        user_agent_header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        }

        response = requests.get(
            sanitized_url, headers=user_agent_header, timeout=timeout
        )


        if response.status_code >= 400:
            return None, f"Error: HTTP {response.status_code} error"

        return response, None
    except ValueError as ve:
        return None, f"Error: {str(ve)}"

    except requests.exceptions.RequestException as re:

        return None, f"Error: {str(re)}"


def parse_web(url) -> str:

    response, potential_error = get_response(url)
    if response is None:
        return potential_error


    if response.status_code >= 400:
        return f"Error: HTTP {str(response.status_code)} error"

    soup = BeautifulSoup(response.text, "html.parser")

    for script in soup(["script", "style"]):
        script.extract()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)

    return text


def google_search(keyword, num_results=5) -> dict:
    
    search_result = {
        url: parse_web(url)
        for url in search(
            keyword, tld="com", num=num_results, stop=num_results, pause=2
        )
    }
    return {"keyword": keyword, "search_result": search_result}


