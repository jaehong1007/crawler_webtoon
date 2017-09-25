import os

import pickle
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

import utils


class NaverWebtoonCrawler:
    def __init__(self, webtoon_title=None):
        webtoon_search_results = self.find_webtoon(webtoon_title)

        while not webtoon_search_results:
            search_title = input('검색할 웹툰명을 입력해주세요 ')
            webtoon_search_results = self.find_webtoon(search_title)
        if len(webtoon_search_results) == 1:
            self.webtoon = webtoon_search_results[0]
        elif len(webtoon_search_results) >= 2:
            while True:
                print('웹툰을 선택해주세요')
                for index, webtoon in enumerate(webtoon_search_results):
                    print('{}.{}'.format(index + 1, webtoon.title))
                try:
                    selected_index = int(input('-선택: '))
                    self.webtoon = webtoon_search_results[selected_index - 1]
                    break
                except IndexError:
                    print(' {}번 이하의 숫자를 선택해주세요\n'.format(
                        len(webtoon_search_results)))
                except ValueError:
                    print(' 해당 웹툰의 숫자를 입력해주세요\n')

        self.episode_list = list()
        self.load(init=True)
        print('- 현재 웹툰: %s' % self.webtoon.title)
        print('- 로드된 Episode수: %s' % len(self.episode_list))

    @property
    def total_episode_count(self):

        el = utils.get_webtoon_episode_list(self.webtoon.title_id)
        return int(el[0].no)

    @property
    def up_to_date(self):

        # cur_episode_count = len(self.episode_list)
        # total_episode_count = self.total_episode_count

        # if cur_episode_count == total_episode_count:
        #     return True
        # return False
        # return cur_episode_count == total_episode_count
        return len(self.episode_list) == self.total_episode_count

    def find_webtoon(self, title):

        """
        title에 주어진 문자열로 get_webtoon_list로 받아온 웹툰 목록에서
        일치하거나 문자열이 포함되는 Webtoon목록을 리턴
        :param title: 찾을 웹툰 제목
        :return:
        """

        return [webtoon for webtoon in
                self.get_webtoon_list()
                if title in webtoon.title]

    def get_webtoon_list(self):
        url = 'http://comic.naver.com/webtoon/weekday.nhn'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        webtoon_list = set()

        daily_all = soup.select_one('.list_area.daily_all')
        days = daily_all.select('div.col')
        for day in days:
            items = day.select('li')
            for item in items:
                url_thumbnail = item.select_one('div.thumb').a.img['src']
                title = item.select_one('a.title').get_text(strip=True)

                url_webtoon = item.select_one('a.title')['href']
                parse_result = urlparse(url_webtoon)
                queryset = parse_qs(parse_result.query)
                title_id = queryset['titleId'][0]

                webtoon = utils.Webtoon(title_id=title_id, url_thumbnail=url_thumbnail, title=title)
                webtoon_list.add(webtoon)

        webtoon_list = sorted(list(webtoon_list), key=lambda webtoon: webtoon.title)
        return webtoon_list

    def update_episode_list(self, force_update=False):

        recent_episode_no = self.episode_list[0].no if self.episode_list else 0
        print('- Update episode list start (Recent episode no: %s) -' % recent_episode_no)
        page = 1
        new_list = list()
        while True:
            print(' Get webtoon episode list (Loop %s)' % page)
            el = utils.get_webtoon_episode_list(self.webtoon.title_id, page)
            for episode in el:

                if int(episode.no) > int(recent_episode_no):
                    new_list.append(episode)
                    if int(episode.no) == 1:
                        break
                else:
                    break
            else:
                page += 1
                continue

            break

        self.episode_list = new_list + self.episode_list
        return len(new_list)

    def get_last_page_episode_list(self):
        el = utils.get_webtoon_episode_list(self.webtoon.title_id, 99999)
        self.episode_list = el
        return len(self.episode_list)

    def get_episode_detail(self, episode):
        """
        주어진 Episode의 상세페에지를 크롤링
            1. 상세페이지를 파싱해서 img태그들의 src속성들을 가져옴
            2.
        :param episode:
        :return:
        """

    def save(self, path=None):

        if not os.path.isdir('db'):
            os.mkdir('db')

        obj = self.episode_list
        path = 'db/%s.txt' % self.webtoon.title_id
        pickle.dump(obj, open(path, 'wb'))

    def load(self, path=None, init=False):

        try:
            path = f'db/{self.webtoon.title_id}.txt'
            self.episode_list = pickle.load(open(path, 'rb'))
        except FileNotFoundError:
            print('파일이 없습니다')

# headers = {'Referer': '주소'}
# response = requests.get(url, headers=headers)

    def make_list_html(self):
        if not os.path.isdir('webtoon'):
            os.mkdir('webtoon')
        filename = f'webtoon/{self.webtoon.title_id}.html'
        with open(filename, 'wt') as f:
            # HTML 앞부분 작성
            f.write(open('html/list_html_head.html', 'rt').read())

            # episode_list순회하며 나머지 코드 작성
            for e in self.episode_list:
                list_html_tr = open('html/list_html_head.html', 'rt').read()
                f.write(list_html_tr.format(
                    url_thumbnail=f'./{self.webtoon.title_id}_thumbnail/{e.no}.jpg',
                    title=e.title,
                    rating=e.rating,
                    created_date=e.created_date
                ))
            # HTML 뒷부분 작성
            list_html_tail = open('html/list_html_tail.html', 'rt').read()
            f.write(list_html_tail)
        return filename

if __name__ == '__main__':
    crawler = NaverWebtoonCrawler('선천적')
    crawler.update_episode_list()


