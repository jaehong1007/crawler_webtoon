# Episode = namedtuple('Episode', ['no', 'img_url', 'title', 'rating', 'created_date'])
import os
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
import pickle


class Episode:
    """
    namedtuple 'Episode'와 같은 역할을 할 수 있도록 생성
    """
    def __init__(self, webtoon, no, url_thumbnail, title, rating, created_date):
        self._webtoon = webtoon
        self._no = no
        self._url_thumbnail = url_thumbnail
        self._title = title
        self._rating = rating
        self._created_date = created_date
        self.image_dir = f'webtoon{self.webtoon.title_id}_images/{self.no}'
        self.thumbnail_dir = f'webtoon/{self.webtoon.title_id}_thumbnail'
        self.episode_dir = f'webtoon/{self.webtoon.title_id}/{self.no}.html'
        self.save_thumbnail()

    @property
    def webtoon(self):
        return self._webtoon

    @property
    def no(self):
        return self._no

    @property
    def url_thumbnail(self):
        return self._url_thumbnail

    @property
    def title(self):
        return self._title

    @property
    def rating(self):
        return self._rating

    @property
    def created_date(self):
        return self._created_date

    @property
    def has_thumbnail(self):
        """
        현재경로/webtoon/{self.webtoon.title_id}_thumbnail/{self.no}.jpg
          파일이 있는지 검사 후 리턴
        :return:
        """
        path = f'{self.thumbnail_dir}/{self.no}.jpg'
        return os.path.exists(path)

    def save_thumbnail(self, force_update=True):
        """
        Episode자신의 img_url에 있는 이미지를 저장한다
        :param force_update:
        :return:
        """
        if not self.has_thumbnail or force_update:
            # webtoon/{self.webtoon.title_id}에 해당하는 폴더 생성
            os.makedirs(self.thumbnail_dir, exist_ok=True)
            response = requests.get(self.url_thumbnail)
            filepath = f'{self.thumbnail_dir}/{self.no}.jpg'
            if not os.path.exists(filepath):
                with open(filepath, 'wb') as f:
                    f.write(response.content)

    def save_contents(self):
        """

        :return:
        """
    def _save_images(self):
        url_contents = 'http://comic.naver.com/webtoon/list.nhn?' \
                       + urlencode(params)
        params = {'titleId': self.webtoon.title_id, 'no': self.no}

        response = requests.get(url_contents, params=params)
        soup = BeautifulSoup(response.text, 'lxml')
        img_list = soup.select_one('div.wt_viewer').find_all('img')
        url_img_list= [img['src'] for img in img_list]

        for index, url in url_img_list:
            headers = {
                'Referer': url_contents
            }
            response = requests.get(url, headers=headers)
            with open(f'{self.image_dir}/{index + 1}.jpg', 'wb') as f:
                f.write(response.content)

    def _make_html(self):

        detail_html = open('html/detail_html.html', 'rt').read()
        detail_html.replace('*title*', '%s -%s' % (self.webtoon.title, self.title))
        img_list_html = ''
        for file in os.listdir(self.image_dir):
            cur_img_tag = '<img src="%s/%s">' % (self.image_dir, file)
            img_list_html += cur_img_tag

        detail_html.replace('*contents*', img_list_html)
        with open(f'webtoon/{self.webtoon.title_id}/{self.no}.html', 'wt')
            f.write(detail_html)


if __name__ == '__main__':
    el = pickle.load(open('db/697680.txt', 'rb'))
    e = el[0]
    e._save_images()



