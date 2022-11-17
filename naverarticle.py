from selenium import webdriver
from selenium.webdriver.common.by import By
import argparse
from crawler import Crawlin
import time

class NewsPage (Crawlin):

    def __init__(self, url:str, verbose:bool=True, **kwargs) -> None:
        super().__init__(**kwargs)

        self.driver = webdriver.Chrome()
        try:
            print(url)
            self.driver.get(url)
        except:
            raise ValueError("Invalid URL")

        time.sleep(1)

        self.data['url'] = url
        self.data['title'] = self.driver.find_element(By.CLASS_NAME, "media_end_head_headline").text
        try: self.data['summary'] = self.driver.find_element(By.CLASS_NAME, "media_end_summary").text
        except: pass
        self.data['article'] = self.driver.find_element(By.ID, "dic_area").text
        self.data['author'] = self.driver.find_element(By.CLASS_NAME, "byline_s").text
        self.data['date'] = self.driver.find_element(By.CLASS_NAME, "_ARTICLE_DATE_TIME").get_attribute('data-date-time')
        try: temp = self.driver.find_element(By.CLASS_NAME, "_ARTICLE_MODIFY_DATE_TIME").get_attribute('data-modify-date-time')
        except: pass
        self.data['press'] = self.driver.find_elements(By.CLASS_NAME, "media_end_head_top_logo_img")[0].get_attribute('title')
        self.data['press_addr'] = self.driver.find_elements(By.CLASS_NAME, "media_end_head_top_logo")[0].get_attribute('href')
        self.data['comments'] = {'num':0, 'list':[]}

        if verbose:
            self.verbose = verbose
            print(self.data['title'])

    def crawlin(self)->None: # Crawlin comments

        comment_url = self.data['url'].replace('article', 'article/comment')

        try:
            self.driver.get(comment_url)
        except:
            raise ValueError(f"Not a Naver news page URL : {comment_url}")

        time.sleep(1)

        more = self.driver.find_element(By.CLASS_NAME, "u_cbox_paginate")
        while more.get_attribute('style') != "display: none;":
            try: more.click()
            except: break

        comments = self.driver.find_elements(By.CLASS_NAME, "u_cbox_area")

        for comment in comments:
            try: comment_text = comment.find_element(By.CLASS_NAME, "u_cbox_text_wrap").find_element(By.CLASS_NAME, "u_cbox_contents").text
            except: continue
            comment_date = comment.find_element(By.CLASS_NAME, "u_cbox_info_base").find_element(By.CLASS_NAME, "u_cbox_date").get_attribute("data-value")
            self.data['comments']['num'] += 1
            self.data['comments']['list'].append({'date':comment_date, 'text':comment_text})
            if self.verbose:
                print(f"ㄴ {comment_text}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='News Page (Naver) Parser')
    parser.add_argument('url', type=str)
    args = parser.parse_args()
    crawler = NewsPage(args.url)
    crawler.crawlin()