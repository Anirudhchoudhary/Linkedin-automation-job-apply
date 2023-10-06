from playwright.sync_api import sync_playwright
import time
from datetime import datetime
from bs4 import BeautifulSoup


class LinkedinJob(object):
    def __init__(self, cache_key, expire_at, job_title):
        self.soup = None
        self.__init_scraper()
        self.EXTRA_FIELD = "Additional Questions"
        self.set_cache(cache_key, expire_at)
        self.open_home_page(job_title)

    def init_praser(self, html_text):

        if not html_text:
            print("html text is blank")
            return

        self.soup = BeautifulSoup(html_text, features="lxml")

        label_list = self.soup.find_all('label')
        form_heading = self.soup.find(attrs={"class": "t-16"})

        if form_heading.lower() != self.EXTRA_FIELD.lower():
            print("Currently only work for %s section" % (self.EXTRA_FIELD))

            return

        for i in range(len(label_list)):
            label = label_list[i]

            id = label['for']
            input_field = self.soup.find(attrs={"id": id})

            type_of_input = input_field.type

            if type_of_input is None:
                if "multipleChoice" in input_field:
                    if ":" in id:
                        type_of_input = "fieldset"
                    else:
                        type_of_input = "select" 

            if type_of_input == "text":
                input_item = self.page.locator('xpath=*//input[@id="%s"]' % (id))

                try:
                    input_item.type("Anirudh", delay=1000)
                except Exception as e:
                    print(e)
            elif type_of_input == "select":
                input_item = self.page.locator('xpath=*//input[@id="%s"]' % (id))

                try:
                    input_item.select_option("India")
                except Exception as e:
                    print(e)
            elif type_of_input == "fieldset":
                # will implement it in next release.
                pass
            else:
                print("only Internal field")
                return
                

    def __init_scraper(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.firefox.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.context.set_default_timeout(30000)

    def timestamp_to_number(self, expire_at):
        
        if not expire_at:
            raise ValueError("expire at can't be None.")

        timestamp_datetime = datetime.strptime(expire_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        timestamp_numeric = timestamp_datetime.timestamp()

        return timestamp_numeric

    def set_cache(self, cache_key, expire_at):
        self.context.add_cookies([{
            "name": "li_at",
            "value": cache_key,
            "expires": self.timestamp_to_number(expire_at),
            "httpOnly": True,
            "secure": True,
            "domain": "www.linkedin.com",
            "path": "/"
        }])


    def job_modal_open(self):
        xpath = 'xpath=*//div[contains(@class, "jobs-easy-apply-modal__content")]//form'

        try:
            visible = self.page.locator(xpath).is_visible()
            return visible
        except:
            return False
        
    def get_form_text(self):
        xpath = 'xpath=*//div[contains(@class, "jobs-easy-apply-modal__content")]//form'

        try:
            inner_html = self.page.locator(xpath).inner_html()
            return inner_html
        except:
            return ''


    def click_next(self):
        xpath = 'xpath=*//span[text()="Next"]'

        try:
            next_btn = self.page.locator(xpath).nth(0)

            if next_btn:
                next_btn.click()

            return True, False
        except Exception as e:
            print("Next text button not shown")
        
        try:
            xpath = "xpath=*//span[text()='Review']"
            next_btn = self.page.locator(xpath).nth(0)

            if next_btn:
                next_btn.click()

            return True, False
        except Exception as e:
            print("Review Button not shown")
        
        try:
            xpath = "xpath=*//span[text()='Submit application']"
            next_btn = self.page.locator(xpath).nth(0)

            if next_btn:
                next_btn.click()

            xpath = "xpath=*//span[text()='Done']"
            done_btn = self.page.locator(xpath).nth(0)

            if done_btn:
                done_btn.click()

                return True, True

            return True, False
        except Exception as e:
            print("Submit Button not shown")

        
        return False, False

    def apply_job(self):
        try:
            easy_apply_job_btn = self.page.locator('xpath=*//span[text()="Easy Apply"]').nth(0)
            easy_apply_job_btn.click()
        except:
            raise Exception("Unable to click Easy Apply Inside job description section.")

        for _ in range(10):
            try:

                if self.job_modal_open():
                    self.click_next()
                    form_html = self.get_form_text()

                    if form_html:
                        self.init_praser(form_html)
                    else:
                        print("form html is blank")
            except Exception as e:
                print(e)
            finally:
                time.sleep(5)

    def open_home_page(self, search_text):
        self.page.goto("https://www.linkedin.com/jobs/search/")
        self.page.wait_for_timeout(10000)


        try:
            search_box = self.page.locator('xpath=*//input[@aria-label="Search by title, skill, or company"]').nth(0)
            search_box.type(search_text, delay=100)
            search_btn = self.page.locator('xpath=*//button[text()="Search"]')
            search_btn.click()
        except Exception as e:
            raise TimeoutError(e)


        try:
            easy_apply_btn = self.page.locator('xpath=*//button[text()="Easy Apply"]')
            easy_apply_btn.click()
        except:
            raise Exception("Unable to click Easy Apply Button.")
        
        try:
            job_items = self.page.locator("xpath=*//main//div[contains(@class, 'jobs-search-results-list')]//li[contains(@class, 'jobs-search-results__list-item')]")
            job_count = len(job_items.all())

            for i in range(job_count):
                try:
                    j = job_items.nth(i)
                    j.click()
                    succ, last_step = self.apply_job()

                    if last_step:
                        print("Job Successfully applied")
                        return

                except Exception as e:
                    print(e)

        except Exception as e:
            print(e)
            



if __name__ == "__main__":
    cache_key = str(input("Enter value of li at key from cache storage: \n"))
    expire_time = str(input("Enter expire at time for li_at cache key: \n"))
    job_title = str(input("Enter your job title.\n"))
    scraper = LinkedinJob(cache_key, expire_time, job_title)