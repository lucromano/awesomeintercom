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

links_file = 'outputs/links/all.csv'

df_all = pd.read_csv(links_file)


dev_list = []


for idx, row in df_all.iterrows():
    link = row['link']
    driver.get(link)

    try:
        element = driver.find_element(By.LINK_TEXT, 'By Types')

        element.click()

        div_elements = driver.find_elements(By.CSS_SELECTOR, 'div.OSInline')

        for i in div_elements:
            div_text = i.text

            if "1, 2 and 3 bed apartments" in div_text:
                parent_element = i.find_element(By.XPATH, './..')

                development_elements = parent_element.find_elements(By.TAG_NAME, 'a')
                for d in development_elements:
                    name = d.text
                    href = d.get_attribute("href")
                    dev_list.append([link, name, href])

    except:
        print(str(link) + ' has none')


df_developments = pd.DataFrame(dev_list, columns=['developer', 'development_name', 'development_link'])

df_developments.to_csv('outputs/developments.csv')




