from bs4 import BeautifulSoup
import requests as req
from argparse import ArgumentParser
from datetime import datetime
from crawler import Crawlin, argparser

class NaverNews (Crawlin):
    def __init__(self, arg) -> None:
        super().__init__()
        self.data['title'] = "Naver News"
        self.data['date_from'] = arg.ds
        self.data['date_to'] = arg.de
        self.data['keywords'] = arg.keywords
        self.data['maxpages'] = arg.maxpages
        self.data['result'] = []

    def crawlin(self)->list:

        for keyword in self.data['keywords']:

            addr = []
            print(f"Searching Keyword: {keyword} ...")
            
            page = 0
            last_page = -1

            while True:

                if last_page == -1:
                    print(f"Searching page {page+1}...")
                else:
                    print(f"Searching page {page}/{last_page}...")

                base_url = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query={keyword}&sort=0&photo=0&field=0&pd=3&ds={self.data['date_from']}&de={self.data['date_to']}&cluster_rank=267&mynews=0&office_type=0&office_section_code=0&news_office_checked=&start={page}1"
                
                try:
                    src_page = req.get(base_url)
                except:
                    print(f"Cannot get HTML page from page {page+1}")
                    continue

                chicken_soup = BeautifulSoup(src_page.text, 'html.parser')
                news_tits = chicken_soup.find_all('a', {'class':'news_tit'})
                sub_tits = chicken_soup.find_all('a', {'class':'sub_tit'})

                for tit in news_tits:
                    print(tit.text)

                addr += [add['href'] for add in news_tits]
                addr += [add['href'] for add in sub_tits]

                last_page = self.check_last_page(chicken_soup)

                if page == last_page or page == self.data['maxpages'] - 1:
                    break

                page += 1

            print(f"Searching Keyword Completed: {keyword} ({len(addr)} found)")
            self.data['result'].append({'keyword':keyword, 'addresses':addr})

        return addr

    def check_last_page(self, soup:BeautifulSoup)->int:
        if soup.find_all('a', {'class':'btn_next'}, href=True):
            return -1
        else:
            btns = soup.find_all_next('a', {'class':'btn'})
            return int(btns[-1].text) - 1

def naver_argparser ()->ArgumentParser:
    parser = argparser()
    subparser = parser.add_subparsers(title='Naver News Crawler')
    naverparser = subparser.add_parser('navernews')
    naverparser.add_argument('ds', type=lambda s: datetime.strptime(s, '%Y.%m.%d').strftime('%Y.%m.%d'), help='date when searching starts')
    naverparser.add_argument('de', type=lambda s: datetime.strptime(s, '%Y.%m.%d').strftime('%Y.%m.%d'), help='date when searching ends')
    naverparser.add_argument('-k', '--keywords', type=str, nargs='+')
    naverparser.add_argument('-p', '--maxpages', type=int, default=0)
    return parser

if __name__ == '__main__':
	args = naver_argparser().parse_args()
	nn = NaverNews(args)
	nn.crawlin()
	nn.dump('json', args.output_path)