from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
from utils import Webtoon

url = 'http://comic.naver.com/webtoon.nhn'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')
webtoon_list = set()

daily_all = soup.select_one('.list_area.daily_all')
days = daily_all.select('div.col')
for day in days:
    items = day.select('li')
    for item in items:
        img_url = item.select_one('div.thumb').a.img['src']
        title = item.select_one('a.title').get_text(strip=True)

        url_webtoon = item.select('a.title')['href']
        parse_result = urlparse(url_webtoon)
        queryset = parse_qs(parse_result.query)
        title_id = queryset['titleId'][0]

        webtoon = Webtoon(title_id=title_id,
                          img_url=img_url,
                          title=title)
        webtoon_list.add(webtoon)

webtoon_list = sorted(list(webtoon_list), key=lambda x: x.title)
for webtoon in webtoon_list:
    print(webtoon.title)





