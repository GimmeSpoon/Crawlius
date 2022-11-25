from selenium import webdriver
from selenium.webdriver.common.by import By
import argparse
from crawler import Crawlin
import time

class NewsPage (Crawlin):

    def __init__(self, url:str, verbose:bool=True, **kwargs) -> None:
        super().__init__(**kwargs)

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.driver = webdriver.Chrome(options=options)
        try:
            print(url)
            self.driver.get(url)
        except:
            raise ValueError("Invalid URL")

        time.sleep(1)

        #Pagin Time
        self.data['url'] = url
        self.data['title'] = self.driver.find_element(By.CLASS_NAME, "media_end_head_headline").text
        try: self.data['summary'] = self.driver.find_element(By.CLASS_NAME, "media_end_summary").text
        except: pass
        self.data['article'] = self.driver.find_element(By.ID, "dic_area").text
        self.data['author'] = self.driver.find_element(By.CLASS_NAME, "byline_s").text
        self.data['date'] = self.driver.find_element(By.CLASS_NAME, "_ARTICLE_DATE_TIME").get_attribute('data-date-time')
        try: self.data['date_modify'] = self.driver.find_element(By.CLASS_NAME, "_ARTICLE_MODIFY_DATE_TIME").get_attribute('data-modify-date-time')
        except: pass
        self.data['press'] = self.driver.find_elements(By.CLASS_NAME, "media_end_head_top_logo_img")[0].get_attribute('title')
        self.data['press_addr'] = self.driver.find_elements(By.CLASS_NAME, "media_end_head_top_logo")[0].get_attribute('href')
        self.data['num_comments'] = 0
        self.data['comments'] = []

        if verbose:
            self.verbose = verbose
            print(self.data['title'])

    def crawlin(self)->dict: # Crawlin comments

        comment_url = self.data['url'].replace('article', 'article/comment')

        try:
            self.driver.get(comment_url)
        except:
            raise ValueError(f"Not a Naver news page URL : {comment_url}")

        time.sleep(1)

        try: more = self.driver.find_element(By.CLASS_NAME, "u_cbox_paginate")
        except: return self.data

        while more.get_attribute('style') != "display: none;":
            try: more.click()
            except: break

        comments = self.driver.find_elements(By.CLASS_NAME, "u_cbox_area")

        for comment in comments:
            try: comment_text = comment.find_element(By.CLASS_NAME, "u_cbox_text_wrap").find_element(By.CLASS_NAME, "u_cbox_contents").text
            except: continue
            comment_date = comment.find_element(By.CLASS_NAME, "u_cbox_info_base").find_element(By.CLASS_NAME, "u_cbox_date").get_attribute("data-value")
            comment_recomm = comment.find_element(By.CLASS_NAME, "u_cbox_tool").find_element(By.CLASS_NAME, "u_cbox_recomm_set").find_element(By.CLASS_NAME, "u_cbox_btn_recomm").find_element(By.TAG_NAME, "em").text
            comment_unrecomm = comment.find_element(By.CLASS_NAME, "u_cbox_tool").find_element(By.CLASS_NAME, "u_cbox_recomm_set").find_element(By.CLASS_NAME, "u_cbox_btn_unrecomm").find_element(By.TAG_NAME, "em").text
            self.data['comments'].append({'date':comment_date, 'likes':int(comment_recomm), 'dislikes':int(comment_unrecomm), 'text':comment_text})
            self.data['num_comments'] += 1
            if self.verbose:
                print(f"ㄴ   {comment_text}")

        return self.data

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='News Page (Naver) Parser')
    parser.add_argument('url', type=str)
    args = parser.parse_args()
    crawler = NewsPage(args.url)
    crawler.crawlin()