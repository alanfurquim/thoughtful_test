from RPA.Browser.Selenium import Selenium
from robocorp.tasks import task
from RPA.Excel.Files import Files
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
import os


class NewsScraper:
    def __init__(self):
        self.browser = Selenium()
        self.excel = Files()
        self.base_url = 'https://www.latimes.com/'

    def open_browser(self):
        self.browser.open_available_browser(self.base_url)
        self.browser.maximize_browser_window()
        self.browser.set_browser_implicit_wait(10)

    def search_theme(self, theme):
        self.browser.click_element(
            "css:body > ps-header > header > div.flex.\[\@media_print\]\:hidden > button")
        self.browser.input_text("name:q", theme)
        self.browser.press_keys("name:q", "ENTER")

    def filter_topic(self, topic):
        if topic:
            self.browser.click_element(
                "css:body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > aside > div > div.search-results-module-filters-content.SearchResultsModule-filters-content > div:nth-child(1) > ps-toggler > ps-toggler > button")
            try:
                self.browser.click_element(
                    f"xpath://span[text()='{topic.title()}']")
            except:
                print('Topic not found')
        self.browser.select_from_list_by_value("name:s", '1')

    def fetch_data(self, ref_date):
        title_list = []
        date_list = []
        desc_list = []
        img_url_list = []
        valid_data = True

        while valid_data:
            for i in range(1, 11):
                try:
                    stamp = self.browser.get_element_attribute(
                        f'css:body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul > li:nth-child({i}) > ps-promo > div > div.promo-content > p.promo-timestamp', 'data-timestamp')
                    news_datetime = datetime.fromtimestamp(int(stamp) / 1000)

                    if news_datetime >= ref_date:
                        title = self.browser.get_text(
                            f'css:body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul > li:nth-child({i}) > ps-promo > div > div.promo-content > div > h3 > a')
                        desc = self.browser.get_text(
                            f'css:body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul > li:nth-child({i}) > ps-promo > div > div.promo-content > p.promo-description')
                        img_url = self.browser.get_element_attribute(
                            f'css:body > div.page-content > ps-search-results-module > form > div.search-results-module-ajax > ps-search-filters > div > main > ul > li:nth-child({i}) > ps-promo > div > div.promo-media > a > picture > img', 'src')

                        title_list.append(title)
                        desc_list.append(desc)
                        date_list.append(news_datetime.strftime("%Y-%m-%d"))
                        img_url_list.append(img_url)
                    else:
                        valid_data = False
                except:
                    valid_data = False

            url = self.browser.get_location()
            if '&p=' in url:
                if url[-2] == '=':
                    page = url[-1]
                    self.browser.go_to(f'{url[0:-1]}{int(page) + 1}')
                else:
                    valid_data = False
            else:
                self.browser.go_to(f'{url}&p=2')

        return title_list, date_list, desc_list, img_url_list

    def download_images(self, img_urls):
        os.makedirs("output/imgs", exist_ok=True)
        img_names = []
        for i, img_url in enumerate(img_urls):
            self.browser.go_to(img_url)
            img_name = f'imgs/image_{i+1}.jpg'
            self.browser.capture_element_screenshot(
                'css:img', f'output/{img_name}')
            img_names.append(img_name)
        return img_names

    def save_to_excel(self, data, theme, filename='output/Target_file.xlsx'):
        titles, dates, descriptions, img_names = data
        records = [
            {"Title": title, "Date": date,
                "Description": desc, "Picture file name": img}
            for title, date, desc, img in zip(titles, dates, descriptions, img_names)
        ]

        search_phrases_count = [
            title.lower().count(theme.lower()) + desc.lower().count(theme.lower())
            for title, desc in zip(titles, descriptions)
        ]

        money_regex = re.compile(r"""
                            (?:
                                \$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})? |
                                \d+(?:\.\d+)?\s?(?:dollars|USD)
                            )
                            """, re.VERBOSE)

        monetary_value = [
            bool(money_regex.search(title) or money_regex.search(desc))
            for title, desc in zip(titles, descriptions)
        ]

        for record, spc, mv in zip(records, search_phrases_count, monetary_value):
            record["Search phrases count"] = spc
            record["Monetary value"] = mv

        self.excel.create_workbook(filename)
        self.excel.append_rows_to_worksheet(records, header=True)
        self.excel.save_workbook()

    def close_browser(self):
        self.browser.close_browser()


@task
def main():
    scraper = NewsScraper()
    scraper.open_browser()

    # Substitute input calls with variables for Robocorp tasks
    theme = "climate change"
    topic = "Environment"
    months = 3

    scraper.search_theme(theme)
    scraper.filter_topic(topic)

    if months <= 1:
        base_date = datetime(datetime.now().year, datetime.now().month, 1)
    else:
        base_date = datetime(datetime.now().year, datetime.now(
        ).month, 1) - relativedelta(months=months - 1)

    titles, dates, descriptions, pic_urls = scraper.fetch_data(base_date)
    pic_names = scraper.download_images(pic_urls)
    scraper.save_to_excel([titles, dates, descriptions, pic_names], theme)
    scraper.close_browser()


if __name__ == "__main__":
    main()
