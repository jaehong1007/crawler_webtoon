import os

import pickle

import requests

import utils


class NaverWebtoonCrawler:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self.episode_list = list()

    @property
    def total_episode_count(self):

        el = utils.get_webtoon_episode_list(self.webtoon_id)
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

    def update_episode_list(self, force_update=False):

        recent_episode_no = self.episode_list[0].no if self.episode_list else 0
        print('- Update episode list start (Recent episode no: %s) -' % recent_episode_no)
        page = 1
        new_list = list()
        while True:
            print('  Get webtoon episode list (Loop %s)' % page)
            el = utils.get_webtoon_episode_list(self.webtoon_id, page)
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
        el = utils.get_webtoon_episode_list(self.webtoon_id, 99999)
        self.episode_list = el
        return len(self.episode_list)

    def save(self, path=None):

        if not os.path.isdir('db'):
            os.mkdir('db')

        obj = self.episode_list
        path = 'db/%s.txt' % self.webtoon_id
        pickle.dump(obj, open(path, 'wb'))

    def load(self, path=None):

        try:
            path = f'db/{self.webtoon_id}.txt'
            self.episode_list = pickle.load(open(path, 'rb'))
        except FileNotFoundError:
            print('파일이 없습니다')

    def save_list_thumbnail(self):
        """

        webtoon/{webtoon_id}_thumbnail/<episode_no>.jpg
        1. webtoon/{webtoon_id}_thumbnail이라는 폴더가 존재하는지 확인 후 생성
        2. self.episode_list를 순회하며 각 episode의 img_url경로의 파일을 저장
        :return: 저장한 thumbnail개수
        """
        thumbnail_dir = f'webtoon/{self.webtoon_id}_thumbnail'
        os.makedirs(thumbnail_dir, exist_ok=True)
        for episode in self.episode_list:
            response = requests.get(episode.img_url)
            filepath = f'{thumbnail_dir}/{episode.no}.jpg'
            if not os.path.exists(filepath):
                with open(filepath, 'wb') as f:
                    f.write(response.content)
# headers = {'Referer': '주소'}
# response = requests.get(url, headers=headers)

    def make_list_html(self):
        if not os.path.isdir('webtoon'):
            os.mkdir('webtoon')
        filename = f'webtoon/{self.webtoon_id}.html'
        with open(filename, 'wt') as f:
            # HTML 앞부분 작성
            f.write(utils.LIST_HTML_HEAD)

            # episode_list순회하며 나머지 코드 작성
            for e in self.episode_list:
                f.write(utils.LIST_HTML_TR.format(
                    img_url=f'./{self.webtoon_id}_thumbnail/{e.no}.jpg',
                    title=e.title,
                    rating=e.rating,
                    created_date=e.created_date
                ))
            # HTML 뒷부분 작성
            f.write(utils.LIST_HTML_TAIL)
        return filename

if __name__ == '__main__':
    crawler = NaverWebtoonCrawler(697654)
    crawler.update_episode_list()
    crawler.save()
    crawler.save_list_thumbnail()
    crawler.make_list_html()


