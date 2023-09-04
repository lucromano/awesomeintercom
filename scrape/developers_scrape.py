import requests
from bs4 import BeautifulSoup
import re
import time


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Function to scrape data from a developer's page
def scrape_developer_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup)

    time.sleep(30)

    # Find the tab with the name "By types"
    by_types_tab = soup.find('a', text='By types')

    if by_types_tab:
        by_types_tab.click()  # Click on the "By types" tab if it exists

        # Find the list underneath "1, 2 and 3 bed apartments"
        apartments_list = soup.find('div', {'id': re.compile(r'wt48_wtMainContent_wtApartmentsList_\d+')})

        if apartments_list:
            # Parse and print the data from the list
            items = apartments_list.find_all('li')
            for item in items:
                print(item.text)


# Main scraping logic
base_url = 'https://www.whathouse.com/housebuilders/'
page_number = 1
visited_links = set()

while True:
    # page_url = f'{base_url}?page={page_number}'
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    print(links)
    # Filter the links that match the pattern '/housebuilders/<name>'
    developer_links = [link['href'] for link in links if re.match(r'^/housebuilders/[\w-]+$', link['href'])]

    print(developer_links)

    if not developer_links:
        break  # No more pages to scrape

    for link in developer_links:
        developer_url = f'https://www.whathouse.com{link["href"]}'

        # Check if we've already visited this developer's page
        if developer_url not in visited_links:
            visited_links.add(developer_url)

print(visited_links)
