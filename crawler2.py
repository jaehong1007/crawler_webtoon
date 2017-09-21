import os

import pickle

import utils


class NaverWebtoonCrawler:
    def __init__(self, webtoon_id):
        self.webtoon_id = webtoon_id
        self.episode_list = list()
        # 객체 생성 시 'db/{webtoon_id}.txt' 파일이 존재하면
        # 바로 load()해오도록 설정
        self.load(init=True)

    @property
    def total_episode_count(self):
        """
        webtoon_id에 해당하는 실제 웹툰의 총 episode수를 리턴
        requests를 사용
        :return: 총 episode수 (int)
        """
        el = utils.get_webtoon_episode_list(self.webtoon_id)
        return int(el[0].no)

    @property
    def up_to_date(self):
        """
        현재 가지고있는 episode_list가 웹상의 최신 episode까지 가지고 있는지
        1. cur_episode_count = self.episode_list의 개수
        2. total_episode_count = 웹상의 총 episode 개수
        3. 위 두 변수의 값이 같으면 return True, 아니면 return False처리
        :return: boolean값
        """
        # 지금 가지고 있는 총 Episode의 개수
        #   self.episode_list에 저장되어있음
        #      -> list형 객체
        #      -> list형 객체의 길이를 구하는 함수(시퀀스형 객체는 모두 가능)
        #        -> 내장함수 len(s)
        # cur_episode_count = len(self.episode_list)

        # 웹상의 총 episode개수
        # total_episode_count = self.total_episode_count

        # 두 값이 같으면 True를, 아니면 False를 리턴
        # if cur_episode_count == total_episode_count:
        #     return True
        # return False
        # return cur_episode_count == total_episode_count
        return len(self.episode_list) == self.total_episode_count

    def update_episode_list(self, force_update=False):
        """
        1. recent_episode_no = self.episode_list에서 가장 최신화의 no
        2. while문 또는 for문 내부에서 page값을 늘려가며
            utils.get_webtoon_episode_list를 호출
            반환된 list(episode)들을 해당 episode의 no가
                recent_episode_no보다 클 때 까지만 self.episode_list에 추가
        self.episode_list에 존재하지 않는 episode들을 self.episode_list에 추가
        :param force_update: 이미 존재하는 episode도 강제로 업데이트
        :return: 추가된 episode의 수 (int)
        """
        recent_episode_no = self.episode_list[0].no if self.episode_list else 0
        print('- Update episode list start (Recent episode no: %s) -' % recent_episode_no)
        page = 1
        new_list = list()
        while True:
            print('  Get webtoon episode list (Loop %s)' % page)
            # 계속해서 증가하는 'page'를 이용해 다음 episode리스트들을 가져옴
            el = utils.get_webtoon_episode_list(self.webtoon_id, page)
            # 가져온 episode list를 순회
            for episode in el:
                # 각 episode의 no가 recent_episode_no보다 클 경우,
                # self.episode_list에 추가
                if int(episode.no) > int(recent_episode_no):
                    new_list.append(episode)
                    if int(episode.no) == 1:
                        break
                else:
                    break
            # break가 호출되지 않았을 때
            else:
                # 계속해서 진행해야 하므로 page값을 증가시키고 continue로 처음으로 돌아감
                page += 1
                continue
            # el의 for문에서 break가 호출될 경우(더 이상 추가할 episode없음
            # while문을 빠져나가기위해 break실행
            break

        self.episode_list = new_list + self.episode_list
        return len(new_list)

    def get_last_page_episode_list(self):
        el = utils.get_webtoon_episode_list(self.webtoon_id, 99999)
        self.episode_list = el
        return len(self.episode_list)

    def save(self, path=None):
        """
        현재폴더를 기준으로 db/<webtoon_id>.txt 파일에
        pickle로 self.episode_list를 저장
        1. 폴더 생성시
            os.path.isdir('db')
                path가 directory인지
            os.mkdir(path)
                path의 디렉토리를 생성
        2. 저장시
            pickle.dump(obj, file)
                obj -> Object (모든 객체 가능)
                file -> File object (파일 객체, bytes형식으로 write가능한)
        :return: None(없음)
        """
        # db폴더가 있는지 검사
        if not os.path.isdir('db'):
            # 없으면 폴더 생성
            os.mkdir('db')

        obj = self.episode_list
        path = 'db/%s.txt' % self.webtoon_id
        pickle.dump(obj, open(path, 'wb'))

    def load(self, path=None), init=False:
        """
        현재폴더를 기준으로 db/<webtoon_id>.txt 파일의 내용을 불러와
        pickle로 self.episode_list를 복원
        1. 만약 db폴더가 없으면 or db/webtoon_id.txt파일이 없으면
            -> "불러올 파일이 없습니다" 출력
        2. 있으면 복원
        :return: None(없음)
        """
        try:
            path = f'db/{self.webtoon_id}.txt'
            self.episode_list = pickle.load(open(path, 'rb'))
        except FileNotFoundError:
            if not init:
                print('파일이 없습니다')



