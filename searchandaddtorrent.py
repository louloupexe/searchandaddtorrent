import os
import urllib.parse
import re
import time
import requests
import urllib3
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Disable warnings for unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# qBittorrent server configuration
# change QB_URL,USER,PASS
QB_URL = "qbittorrent link"
QB_USER = "USERNAME"
QB_PASS = "PASSWORD"

# ANSI color codes
COLORS = {
    'header': '\033[1;37m',  # Bold white
    'number': '\033[1;33m',  # Bold yellow
    'french': '\033[1;34m',  # Bold blue
    'multi': '\033[1;32m',   # Bold green
    'vo': '\033[1;31m',      # Bold red
    'stfr': '\033[0;37m',    # Normal white
    'vostfr': '\033[1;33m',  # Light bold yellow
    'unknown': '\033[1;35m', # Bold magenta
    'reset': '\033[0m'       # Reset
}

def clear_terminal():
    """Clears the terminal based on the operating system."""
    os.system('cls' if os.name == 'nt' else 'clear')

def parse_torrent_info(name, size):
    """Parses torrent information from the name and size."""
    language = 'Unknown'
    quality = []
    year = 'Unknown'

    # Extract language information
    lang_match = re.search(r'\b(VF|VFF|TRUEFRENCH|MULTI|VO|VOSTFR|FRENCH|STFR)\b', name, re.IGNORECASE)
    if lang_match:
        language = lang_match.group(0).upper()
        # Remove language from name
        name = re.sub(r'\b' + re.escape(language) + r'\b', '', name, flags=re.IGNORECASE).strip()

    # Extract quality information
    quality_matches = re.findall(r'(BluRay|720p|1080p|4K|DVDRIP|WEBRIP|HDLight|ULTRA HD|HDTV)', name, re.IGNORECASE)
    if quality_matches:
        quality = list(set(quality_matches))  # Create a unique list of qualities
        for match in quality_matches:
            name = re.sub(match, '', name, flags=re.IGNORECASE).strip()

    # Extract year
    year_match = re.search(r'\b\d{4}\b', name)
    if year_match:
        year = year_match.group(0)
        name = re.sub(year, '', name).strip()

    quality = ', '.join(sorted(quality)).upper()

    return name, language, quality, year, size

def search_and_save_torrent(film_name):
    edge_options = Options()
    edge_options.add_argument('--headless')
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument('--disable-dev-shm-usage')

    service = Service(executable_path='C:/WebDriver/msedgedriver.exe', log_path=os.devnull)

    driver = webdriver.Edge(service=service, options=edge_options)

    search_query = urllib.parse.quote(film_name, safe='')
    search_url = f"https://www.torrent9-p2p.com/recherche/{search_query}"

    try:
        while True:
            driver.get(search_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table')))

            rows = driver.find_elements(By.CSS_SELECTOR, 'table.table tbody tr')

            if rows:
                torrents = []
                for row in rows:
                    name_element = row.find_element(By.CSS_SELECTOR, 'td a')
                    size_element = row.find_elements(By.CSS_SELECTOR, 'td')[1]

                    name = name_element.text
                    size = size_element.text

                    if "PC" in name:
                        continue

                    name, language, quality, year, size = parse_torrent_info(name, size)
                    torrents.append((name, language, quality, year, size))

                if torrents:
                    clear_terminal()  # Clear terminal before displaying the table

                    max_name_length = max(len(torrent[0]) for torrent in torrents)
                    max_language_length = max(len(torrent[1]) for torrent in torrents)
                    max_quality_length = max(len(torrent[2]) for torrent in torrents)
                    max_year_length = max(len(torrent[3]) for torrent in torrents)
                    max_size_length = max(len(torrent[4]) for torrent in torrents)

                    header = f"{COLORS['header']}{'N°':<5} | {'Nom'.ljust(max_name_length)} | {'Langue'.ljust(max_language_length)} | {'Qualité'.ljust(max_quality_length)} | {'Année'.ljust(max_year_length)} | {'Taille'.ljust(max_size_length)}{COLORS['reset']}"
                    separator_length = len(header) + 2
                    separator = '+' + '-' * (separator_length - 12) + '+'

                    print(separator)
                    print(f"| {COLORS['header']}{'N°':<4}{COLORS['reset']} | {COLORS['header']}{'Nom'.ljust(max_name_length)}{COLORS['reset']} | {COLORS['header']}{'Langue'.ljust(max_language_length)}{COLORS['reset']} | {COLORS['header']}{'Qualité'.ljust(max_quality_length)}{COLORS['reset']} | {COLORS['header']}{'Année'.ljust(max_year_length)}{COLORS['reset']} | {COLORS['header']}{'Taille'.ljust(max_size_length)}{COLORS['reset']} |")
                    print(separator)
                    for index, torrent in enumerate(torrents, start=1):
                        name, language, quality, year, size = torrent
                        language_color = COLORS['reset']
                        if 'Unknown' in language:
                            language_color = COLORS['unknown']
                        elif language in ['VF', 'VFF', 'TRUEFRENCH', 'FRENCH']:
                            language_color = COLORS['french']
                        elif language == 'MULTI':
                            language_color = COLORS['multi']
                        elif language == 'VO':
                            language_color = COLORS['vo']
                        elif language == 'STFR':
                            language_color = COLORS['stfr']
                        elif language == 'VOSTFR':
                            language_color = COLORS['vostfr']

                        print(f"| {COLORS['number']}{index:<4}{COLORS['reset']} | {name.ljust(max_name_length)} | {language_color}{language.ljust(max_language_length)}{COLORS['reset']} | {quality.ljust(max_quality_length)} | {year.ljust(max_year_length)} | {size.ljust(max_size_length)} |")
                    print(separator)

                    selection = int(input("Enter the number of the torrent you want to select: "))

                    if selection < 1 or selection > len(torrents):
                        print("Invalid selection.")
                        break

                    selected_torrent_url = rows[selection - 1].find_element(By.CSS_SELECTOR, 'td a').get_attribute('href')
                    driver.get(selected_torrent_url)

                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href^="magnet:"]')))
                        magnet_elements = driver.find_elements(By.CSS_SELECTOR, 'a[href^="magnet:"]')

                        if magnet_elements:
                            magnet_link = magnet_elements[0].get_attribute('href')

                            # Save the magnet link in a file
                            with open("magnet.txt", "a") as f:
                                f.write(magnet_link + "\n")

                            return  # Exit the function after finding and saving the magnet link

                        else:
                            print("No magnet link found.")

                    except Exception as e:
                        print(f"Error retrieving magnet link: {e}")

            print("No results found or magnet link not available. Repeating search in 3 seconds.")
            time.sleep(3)

    except Exception as e:
        print(f"General error: {e}")

    finally:
        driver.quit()

def qbittorrent_auth():
    """Authenticate with qBittorrent."""
    session = requests.Session()
    response = session.post(f"{QB_URL}/api/v2/auth/login", data={"username": QB_USER, "password": QB_PASS}, verify=False)
    if response.ok:
        return session
    else:
        raise Exception("Failed to authenticate with qBittorrent.")

def test_qbittorrent_connection():
    """Test the connection to qBittorrent."""
    try:
        session = qbittorrent_auth()
        response = session.get(f"{QB_URL}/api/v2/app/version", verify=False)
        if response.ok:
            return True
        else:
            return False
    except Exception as e:
        return False

def qbittorrent_add_torrent(session, magnet_link, category, tags):
    """Add a torrent to qBittorrent with specified category and tags."""
    params = {
        "urls": magnet_link,
        "category": category,
        "tags": ",".join(tags)  # Assign tags as a comma-separated string
    }
    response = session.post(f"{QB_URL}/api/v2/torrents/add", data=params, verify=False)
    if not response.ok:
        raise Exception("Failed to add torrent to qBittorrent.")

def check_torrent_status(session, torrent_hash):
    """Check the status of the torrent."""
    response = session.get(f"{QB_URL}/api/v2/torrents/info?hashes={torrent_hash}", verify=False)
    if response.ok:
        torrent_info = response.json()
        if torrent_info and torrent_info[0]["state"] == "completed":
            return True
    return False

def process_magnet_file():
    """Read and process the magnet.txt file."""
    if not os.path.isfile('magnet.txt'):
        return False

    with open('magnet.txt', 'r') as file:
        magnet_links = file.readlines()

    if not magnet_links:
        return False

    if test_qbittorrent_connection():
        session = qbittorrent_auth()

        # Add all magnet links to the qBittorrent server
        for magnet_link in magnet_links:
            magnet_link = magnet_link.strip()
            if re.search(r'\b(saison|s\d+)\b', magnet_link, re.IGNORECASE):
                category = "series"
                tags = ["series"]
            else:
                category = "films"
                tags = ["films"]

            qbittorrent_add_torrent(session, magnet_link, category, tags)

        # Delete the file after processing
        os.remove('magnet.txt')

        return True

    return False

def main():
    """Main function of the script."""
    while True:
        clear_terminal()  # Clear terminal at the beginning of each loop
        print("Welcome to the Torrent Movie Finder!")
        print("This program make by toolwind/loulouexe github.com/toolwind")
        film_name = input("Enter the name of the movie to search for: ")
        search_and_save_torrent(film_name)

        while True:
            if process_magnet_file():
                break
            time.sleep(10)  # Wait 10 seconds before checking again

        another = input("Do you want to add another movie? (yes/no): ").strip().lower()
        if another != 'yes':
            break

if __name__ == "__main__":
    main()
