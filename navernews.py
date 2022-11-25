from bs4 import BeautifulSoup
import requests as req
from argparse import ArgumentParser
from datetime import datetime, date, timedelta
from crawler import Crawlin, argparser
from naverarticle import NewsPage

class NaverNews (Crawlin):

    def __init__(self, arg, **kwargs) -> None:
        super().__init__(**kwargs)
        self.data['title'] = "Crawlius"
        self.data['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.data['date_from'] = arg.ds.strftime('%Y.%m.%d')
        self.data['date_to'] = arg.de.strftime('%Y.%m.%d')
        self.data['keywords'] = arg.keywords
        self.data['maxpages'] = arg.maxpages
        self.data['total_articles'] = 0
        self.data['total_comments'] = 0
        self.data['result'] = []

        self.sorting = arg.sort
        self.silent = arg.silent
        
        if (arg.de - arg.ds).days > 7:
            d7 = timedelta(days=7)
            ts = arg.ds
            te = arg.ds + timedelta(days=6)
            
            self.date_range = []
            while True:
                if te > arg.de:
                    te = arg.de
                    self.date_range.append((ts.strftime('%Y.%m.%d'), te.strftime('%Y.%m.%d')))
                    break
                self.date_range.append((ts.strftime('%Y.%m.%d'), te.strftime('%Y.%m.%d')))
                ts = ts + d7
                te = te + d7                
        else:
            self.date_range = [(self.data['date_from'], self.data['date_to'])]

    def crawlin(self)->list:

        for keyword in self.data['keywords']:

            res = []
            print(f"Searching Keyword: {keyword}")
            
            for (date_from, date_to) in self.date_range:

                page = 0
                last_page = -1

                print(f"Searching from {date_from} to {date_to}...")

                while True:

                    if last_page == -1:
                        print(f"Searching page {page+1}...           \r")
                    else:
                        print(f"Searching page {page+1}/{last_page+1}... \r")

                    base_url = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query={keyword}&sort={self.sorting}&photo=0&field=0&pd=3&ds={date_from}&de={date_to}&cluster_rank=267&mynews=0&office_type=0&office_section_code=0&news_office_checked=&start={page}1"
                    
                    try:
                        src_page = req.get(base_url)
                    except:
                        print(f"Cannot get HTML page from page {page+1}")
                        continue

                    chicken_soup = BeautifulSoup(src_page.text, 'html.parser')
                    naver_news_urls = chicken_soup.find_all('a', "sub_txt",string="네이버뉴스")

                    for tit in naver_news_urls:
                        print(tit.parent.parent.find('a', {'class':['news_tit', 'sub_tit']})['title'])

                    for addr in naver_news_urls:
                        try: page_crawler = NewsPage(addr['href'])
                        except:
                            print("Not supported HTML doc") 
                            continue
                        pd = page_crawler.crawlin()
                        self.data['total_articles'] += 1
                        self.data['total_comments'] += pd['num_comments']
                        res.append(page_crawler.data)

                    last_page = self.check_last_page(chicken_soup)

                    if page == last_page or page == self.data['maxpages'] - 1:
                        break

                    page += 1

            print(f"Searching Keyword Completed: {keyword} ({len(naver_news_urls)} found)")
            self.data['result'].append({'keyword':keyword, 'page':res})

        return 

    def check_last_page(self, soup:BeautifulSoup)->int:
        if soup.find_all('a', {'class':'btn_next'}, href=True):
            return -1
        else:
            btns = soup.find_all('a', {'class':'btn'})
            return int(btns[-1].text) - 1

def naver_argparser ()->ArgumentParser:
    parser = argparser()
    subparser = parser.add_subparsers(title='Naver News Crawler')
    naverparser = subparser.add_parser('navernews')
    naverparser.add_argument('ds', type=lambda s: datetime.strptime(s, '%Y.%m.%d').date(), help='date when searching starts')
    naverparser.add_argument('de', type=lambda s: datetime.strptime(s, '%Y.%m.%d').date(), help='date when searching ends')
    naverparser.add_argument('-k', '--keywords', type=str, nargs='+')
    naverparser.add_argument('-p', '--maxpages', type=int, default=0)
    naverparser.add_argument('-s', '--sort', type=int, default=0, choices=range(3))
    return parser

if __name__ == '__main__':
	args = naver_argparser().parse_args()
	nn = NaverNews(args)
	nn.crawlin()
	nn.dump('json', args.output_path)