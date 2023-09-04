from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from string import ascii_lowercase as alc


# Define user agent and headers
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
options = webdriver.ChromeOptions()
options.add_argument(f'user-agent={user_agent}')

# Set up the Chrome WebDriver

driver = webdriver.Chrome(options=options)

# Main scraping logic
base_url = 'https://www.whathouse.com/housebuilders/'

visited_links = set()

for i in alc:
    page_url = f'{base_url}{i}'
    driver.get(page_url)

    # Find all links that follow the pattern '/housebuilders/<name>'
    try:
        developer_links = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/housebuilders/"]')

        for link in developer_links:
            if link not in visited_links:
                visited_links.add(link.get_attribute("href"))



        print(str(i) + ' done')

    except:

        print(str(i) + ' has none')

links_list = list(visited_links)

df = pd.DataFrame(links_list, columns=['link'])
df.to_csv('outputs/links/all.csv')

# Close the WebDriver when done
driver.quit()
