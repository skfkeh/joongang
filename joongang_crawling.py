import sys
import requests
from bs4 import BeautifulSoup as bs
import re
from konlpy.tag import Okt
from collections import Counter, OrderedDict
import matplotlib
import matplotlib.pyplot as plt
import itertools
# from wordcloud import WordCloud
from datetime import datetime

URL_BEFORE_KEYWORD = "https://www.joongang.co.kr/search/news?keyword="
URL_BEFORE_PAGE_NUM = "&page="
font_path = 'Apple SD Gothic Neo'  # Windows는 Malgun Gothic
# font_path = '/Users/watsonjung/Downloads/나눔 글꼴/나눔고딕/NanumFontSetup_TTF_GOTHIC/NanumGothic.ttf'
now = datetime.now()


def get_link(subject, page_range):
    link = []

    for page in range(int(page_range)):
        current_page = 1 + page
        url = URL_BEFORE_KEYWORD + subject + URL_BEFORE_PAGE_NUM + str(current_page)

        response = requests.get(url)
        soup = bs(response.text, 'lxml')

        url_tag = soup.select("#container > section > div > section > ul > .card > .card_body > h2 > a")
        for url in url_tag:
            link.append(url['href'])

    return link


def get_article(link):
    i = 1
    t_list = []
    c_list = []

    for url2 in link:
        c_tmp = []
        response = requests.get(url2)
        soup = bs(response.text, 'lxml')

        title = soup.select('#container > section > article > header > h1')
        title = re.sub('<.+?>', '', str(title)).strip()
        t_list.append(title)

        content = soup.select('#article_body > p')
        for ct in content:
            c_tmp.append(ct.get_text())

        c_list.append(''.join(c_tmp))

    return t_list, c_list


def wordcount(t_list, c_list):
    engine = Okt()
    all_nouns = engine.nouns(''.join(t_list) + " " + ''.join(c_list))
    nouns = [n for n in all_nouns if len(n) > 1]

    global count, by_num

    count = Counter(nouns)
    by_num = OrderedDict(sorted(count.items(), key=lambda t: t[1], reverse=True))

    #     word = [i for i in by_num.keys()]
    #     number = [i for i in by_num.values()]

    #     for w, n in zip(word, number):
    #         final = f'{w}   {n}'
    return by_num


def full_vis_bar(by_num, top_n):
    for w, n in list(by_num.items()):
        if n <= 15:
            del by_num[w]

    my_dict = dict(itertools.islice(by_num.items(), top_n))
    print(my_dict)

    fig = plt.gcf()  # 현재 시각화 되는 객체에 접근할 필요성이 생길 때 사용
    fig.set_size_inches(20, 10)  # 출력할 때 전체 그래프의 크기를 설정
    matplotlib.rc('font', family=font_path, size=10)
    plt.title('기사에 나온 전체 단어 빈도 수', fontsize=30)
    plt.xlabel('기사에 나온 단어', fontsize=20)
    plt.ylabel('기사에 나온 단어의 개수', fontsize=20)
    plt.bar(my_dict.keys(), my_dict.values(), color='#6799FF')
    plt.xticks(rotation=90)
    plt.savefig('all_words.jpg')
    plt.show()


def main(argv):
    subject = input("중앙일보에서 검색할 내용을 입력해주세요 : ")
    page_range = input("몇 페이지를 크롤링하실 건가요 : ")
    if int(page_range) <= 0:
        print(f'1보다 작은 숫자를 입력할 수 없습니다.')
    else:
        link = get_link(subject, page_range)
        t, c = get_article(link)
        wc = wordcount(t, c)
        full_vis_bar(wc, 20)

if __name__ == '__main__':
    main(sys.argv)