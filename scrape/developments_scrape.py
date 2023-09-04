from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from string import ascii_lowercase as alc
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import re
from googlesearch import search


# Define user agent and headers
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
options = webdriver.ChromeOptions()
options.add_argument(f'user-agent={user_agent}')


class MailSpider(scrapy.Spider):
    name = 'email'

    def parse(self, response):

        links = LxmlLinkExtractor(allow=()).extract_links(response)
        links = [str(link.url) for link in links]
        links.append(str(response.url))

        for link in links:
            print('Link in links ' + str(link))
            yield scrapy.Request(url=link, callback=self.parse_link,
                                 # errback=self.errback_link,
                                 dont_filter=True)

    def parse_link(self, response):

        html_text = str(response.text)
        mail_list = re.findall(r'[\w.+-]+@[\w-]+\.[a-z.-]+', html_text)

        print(mail_list)

        # dic = {'email': mail_list, 'link': str(response.url)}
        # df = pd.DataFrame(dic)
        #
        # df.to_csv(self.path, mode='a', header=False)


    # def errback_link(self, failure):
    #     self.logger.error(repr(failure))
    #
    #     if failure.check(HttpError):
    #         response = failure.value.response
    #         self.logger.error('HttpError on %s', response.url)
    #
    #     # elif isinstance(failure.value, DNSLookupError):
    #     elif failure.check(DNSLookupError):
    #         # this is the original request
    #         request = failure.request
    #         self.logger.error('DNSLookupError on %s', request.url)
    #
    #     # elif isinstance(failure.value, TimeoutError):
    #     elif failure.check(TimeoutError):
    #         request = failure.request
    #         self.logger.error('TimeoutError on %s', request.url)


# Set up the Chrome WebDriver

driver = webdriver.Chrome(options=options)

devs_file = 'outputs/developments.csv'

df_developments = pd.read_csv(devs_file)


for idx, row in df_developments.iterrows():
    developer = row['developer']
    name = row['development_name']

    last_slash_index = developer.rfind('/')
    second_last_slash_index = developer.rfind('/', 0, last_slash_index)
    d = developer[second_last_slash_index + 1:last_slash_index].replace('-', ' ')
    n = name.split(',')[0]
    term = (d + ' ' + n)
    url = [search(term)][0]

    print('Searching for emails...')
    process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0'})
    process.crawl(MailSpider, start_urls=url)
    process.start()



# print('Searching for emails...')
# process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0'})
# process.crawl(MailSpider, start_urls=google_urls)
# process.start()


#
# for idx, row in df_all.iterrows():
#     link = row['link']
#     driver.get(link)
#
#     try:
#         element = driver.find_element(By.LINK_TEXT, 'By Types')
#
#         element.click()
#
#         div_elements = driver.find_elements(By.CSS_SELECTOR, 'div.OSInline')
#
#         for i in div_elements:
#             div_text = i.text
#
#             if "1, 2 and 3 bed apartments" in div_text:
#                 parent_element = i.find_element(By.XPATH, './..')
#
#                 development_elements = parent_element.find_elements(By.TAG_NAME, 'a')
#                 for d in development_elements:
#                     name = d.text
#                     href = d.get_attribute("href")
#                     dev_list.append([link, name, href])
#
#     except:
#         print(str(link) + ' has none')
#
#
# df_developments = pd.DataFrame(dev_list, columns=['developer', 'development_name', 'development_link'])
#
# df_developments.to_csv('outputs/developments.csv')




