import requests as req
from selenium import webdriver
from selenium.webdriver.common.by import By

class NewsPage (Crawlin):

    insert_index = 39

    def __init__(self, url:str, **kwargs) -> None:
        super().__init__(**kwargs)

        self.driver = webdriver.Firefox()
        try:
            self.driver.get(url)
        except:
            raise ValueError("Invalid URL")

        if "네이버" not in self.driver.title:
            raise ValueError(f"Not a Naver News URL: {url}")

        self.data['url'] = url
        self.data['title'] = self.driver.find_element(by=By.CLASS_NAME, value="media_end_head_headline").
        self.data['summary'] = self.soup.find('strong', "media_end_summary").text
        self.data['article'] = self.soup.find('div', id="dic_area").text
        self.data['author'] = self.soup.find('span', "byline_s").text
        self.data['date'] = self.soup.find('span', "_ARTICLE_DATE_TIME")['data-date-time']
        temp = self.soup.find('span', "_ARTICLE_MODIFY_DATE_TIME")
        if temp :
            self.data['modify_date'] = temp['data-modify-date-time']
        self.data['press'] = self.soup.find('img', "media_end_head_top_logo_img")['title']
        self.data['press_addr'] = self.soup.find('a', "media_end_head_top_logo")['href']
        self.data['comments'] = {'num':0, 'contents':[]}

    def crawlin(self)->dict: # Crawlin comments
        
        comments = []
        comment_url = self.data['url'][:self.insert_index] + 'comment/' + self.data['url'][self.insert_index:]
        try:
            comment_page = req.get(comment_url)
        except:
            raise ValueError(f"Not a Naver news page URL : {self.data['url']}")

        soup = BeautifulSoup(comment_page, 'html.parser')
        # Get comments here

        self.data['comments']['num'] = len(comments)
        self.data['comments']['contents'] += comments
        return comments