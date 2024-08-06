"""
.py created to extract the news information according to the input parameters
"""
import os
import re
from datetime import datetime

import pandas as pd
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager


class DriverProcess:
    """
        This class is responsible to run all the commands in the chrome.
    """

    def __init__(self, download_dir=None):
        self.driver = self.create_driver(download_dir)

    def create_driver(self, download_dir=None):
        """
        It creates a Chrome webdriver with the specified options.
        :param download_dir: The directory where you want to download the files to
        :return: A webdriver object
        """
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        chrome_install = ChromeDriverManager().install()
        folder = os.path.dirname(chrome_install)
        chromedriver_path = os.path.join(folder, "chromedriver.exe")
        service = Service(chromedriver_path)
        chrome_options.add_experimental_option("prefs", prefs)
        return webdriver.Chrome(service=service, options=chrome_options)

    def search_theme(self, theme):
        """
        The function searches for a specified theme on the Los Angeles Times website.

        :param theme: The `search_theme` function is designed to search for a specific theme on the
        Los Angeles Times website. The theme parameter is the keyword or topic that you want to
        search for on the website. When you call this function, you should pass the theme that 
        you want to search for as an argument
        """
        self.driver.get('https://www.latimes.com/')
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        self.driver.find_element(
            By.CSS_SELECTOR, r'body > ps-header > header > div.flex.\[\@media_print\]\:hidden > button').click()
        search_bar = self.driver.find_element(By.NAME, 'q')
        search_bar.send_keys(theme)
        search_bar.send_keys(Keys.ENTER)

    def filter_topic(self, topic):
        """
        The `filter_topic` function filters search results by specified topic in a web application.

        :param topic: The `filter_topic` method takes a `topic` parameter as input. This parameter
        is used to filter search results based on the specified topic. The method first clicks on
        a specific element on the page to open the filters section. Then, it attempts to find and
        click on an element with the text
        """
        if topic:
            self.driver.find_element(
                By.CSS_SELECTOR, 'body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > aside > div > div.search-results-module-filters-content.SearchResultsModule-filters-content > div:nth-child(1) > ps-toggler > ps-toggler > button').click()
            try:
                self.driver.find_element(
                    By.XPATH, f"//span[text()='{topic.title()}']").click()
            except NoSuchElementException:
                print('Topic not found')
        Select(self.driver.find_element(By.NAME, 's')).select_by_value('1')

    def download_img(self, img_download_list):
        """
        The function `download_img` downloads images from a list of URLs and saves them as JPG.

        :param img_download_list: The `img_download_list` parameter is a list of URLs pointing to
        images that need to be downloaded. The function `download_img` iterates through this list,
        downloads each image, saves it as a .jpg file in a specific directory, and returns a list
        of the file names of the downloaded
        :return: The function `download_img` returns a list of file names for the downloaded images.
        """
        name_list = []

        for i, img_url in enumerate(img_download_list):
            self.driver.get(img_url)
            file_name = f'imgs/image_{i+1}.jpg'
            with open(file_name, 'wb') as file:
                file.write(self.driver.find_element(
                    By.TAG_NAME, 'img').screenshot_as_png)
            name_list.append(file_name)

        return name_list

    def fetch_data(self, ref_date):
        """
        The `fetch_data` function retrieves news data based on a given date from a web page using
        Selenium in Python.

        :param ref_date: The `ref_date` parameter in the `fetch_data` method is used to filter news
        articles based on their publication date. The method retrieves news articles from a webpage
        and checks if the publication date of each article is greater than or equal to the ref_date.
        If it is, the article details
        :return: The `fetch_data` method returns four lists: `title_list`, `date_list`, `desc_list`,
        and `img_url_list`, which contain the titles, dates, descriptions, and image URLs of news
        articles respectively.
        """
        title_list = []
        date_list = []
        desc_list = []
        img_url_list = []
        valid_data = True

        while valid_data:
            for i in range(1, 11):
                self.driver.
                stamp = self.driver.find_element(
                    By.CSS_SELECTOR, f'body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul > li:nth-child({i}) > ps-promo > div > div.promo-content > p.promo-timestamp')
                news_datetime = datetime.fromtimestamp(
                    int(stamp.get_attribute("data-timestamp")) / 1000)

                if news_datetime >= ref_date:
                    title = self.driver.find_element(
                        By.CSS_SELECTOR, f'body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul > li:nth-child({i}) > ps-promo > div > div.promo-content > div > h3 > a')
                    desc = self.driver.find_element(
                        By.CSS_SELECTOR, f'body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul > li:nth-child({i}) > ps-promo > div > div.promo-content > p.promo-description')
                    img_url = self.driver.find_element(
                        By.CSS_SELECTOR, f'body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul > li:nth-child({i}) > ps-promo > div > div.promo-media > a > picture > img')

                    title_list.append(title.text)
                    desc_list.append(desc.text)
                    date_list.append(news_datetime.strftime("%Y-%m-%d"))
                    img_url_list.append(img_url.get_attribute('src'))
                else:
                    valid_data = False

            url = self.driver.current_url
            if '&p=' in url:
                if url[-2] == '=':
                    page = url[-1]
                    self.driver.get(f'{url[0:-1]}{int(page) + 1}')
                else:
                    valid_data = False
            else:
                self.driver.get(f'{url}&p=2')

        return title_list, date_list, desc_list, img_url_list

    def close_driver(self):
        """
        The `close_driver` function in Python closes the driver instance by quitting it.
        """
        self.driver.quit()


class ExcelProcess:
    def __init__(self, data_list):
        self.df = self.create_df(data_list)

    def create_df(self, data_list):
        """
        The function `create_df` takes a list of data and creates a DataFrame with specific
        column names and default values for additional columns.

        :param data_list: It looks like the code snippet you provided is a function that creates
        a DataFrame using the data from a given data_list.
        """
        df = pd.DataFrame({
            "Title": data_list[0],
            "Date": data_list[1],
            "Description": data_list[2],
            "Picture file name": data_list[3],
            "Search phrases count": pd.NA,
            "Monetary value": pd.NA
        })

        return df

    def count_ocurrences(self, searched_theme):
        """
        This function counts the occurrences of a searched theme in the 'Title' column of a
        DataFrame and stores the total count in a new column 'Search phrases count'.

        :param searched_theme: The `count_ocurrences` method you provided seems to be counting the
        occurrences of a searched theme in the 'Title' column of a DataFrame.
        :return: The function `count_ocurrences` is returning the DataFrame `self.df` after updating
        the 'Search phrases count' column with the total count of occurrences of the
        `searched_theme` in the 'Title' column (case-insensitive) for each row in the DataFrame.
        """
        for i in range(self.df.shape[0]):
            count_t = self.df.at[i, 'Title'].lower().count(
                searched_theme.lower())

            count_d = self.df.at[i, 'Description'].lower().count(
                searched_theme.lower())

            self.df.at[i, 'Search phrases count'] = count_t + count_d

        self.df['Search phrases count'].fillna(0)

        return self.df

    def regex_usd(self):
        """
        The `regex_usd` function uses regular expressions to identify monetary values in a DataFrame
        column containing titles.
        """
        regex = re.compile(r"""
                            (?:
                                \$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})? |
                                \d+(?:\.\d+)?\s?(?:dollars|USD)
                            )
                            """, re.VERBOSE)

        for i in range(self.df.shape[0]):
            if regex.search(self.df.at[i, 'Title']) or regex.search(self.df.at[i, 'Title']):
                self.df.at[i, 'Monetary value'] = True
            else:
                self.df.at[i, 'Monetary value'] = False

        return self.df

    def save(self):
        """
        The `save` function saves the DataFrame to an Excel file named 'Target_file.xlsx'
        without including the index.
        """
        self.df.to_excel('Target_file.xlsx', index=False)


if __name__ == "__main__":
    news_page = DriverProcess()
    theme = input("Theme: ")
    news_page.search_theme(theme)

    search_topic = input("Topic: ")
    news_page.filter_topic(search_topic)

    months = int(input("Number of months: "))
    if months <= 1:
        base_date = datetime(datetime.now().year, datetime.now().month, 1)
    else:
        base_date = datetime(datetime.now().year, datetime.now(
        ).month, 1) - relativedelta(months=months - 1)

    titles, dates, descriptions, pic_urls = news_page.fetch_data(base_date)
    pic_names = news_page.download_img(pic_urls)
    news_page.close_driver()

    file_data = ExcelProcess([titles, dates, descriptions, pic_names])
    file_data.count_ocurrences(theme)
    file_data.regex_usd()
    file_data.save()
