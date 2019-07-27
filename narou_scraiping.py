# coding:utf-8
import urllib3
from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup
import redis

# アクセスするURL
# url = 'https://ncode.syosetu.com/n6621fl/'
mypage_url = 'https://mypage.syosetu.com/'
headers = {
	"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0",
}

redis_novel_info = redis.Redis(host='narou-redis', db=0)
redis_set_data = redis.Redis(host='narou-redis', db=1)

KEY_URL = 'novel_url'
KEY_TITLE = 'novel_title'
KEY_TELLER = 'novel_teller'

# APIから呼び出される
def get_recommend_novel(url):
    set_url(url)
    ret_data = get_data_redis(url)
    print(ret_data)
    if (ret_data != None and len(ret_data) == 0):
        scraping_main(url)
        ret_data = get_data_redis(url)
    return ret_data


def set_url(url):
    url = url

redis_novel = redis.Redis(host='narou-redis', db=0)
redis_user = redis.Redis(host='narou-redis', db=1)
# redis_novel = redis.Redis(host='localhost', port=16379, db=0)
# redis_user = redis.Redis(host='localhost', port=16379, db=1)

def get_href_soup_one(soup_origin, tag_selector):
    href_text = soup_origin.select(tag_selector)[0].get('href')
    req = urllib.request.Request(url=href_text, headers=headers)
    res = urllib.request.urlopen(req)
    soup = BeautifulSoup(res, 'html.parser')
    return soup

# ユーザ用soup取得
def get_href_soup_user(soup_origin, tag_selector):
    href_text = soup_origin.select(tag_selector)[0].get('href')
    req = urllib.request.Request(url=href_text, headers=headers)
    res = urllib.request.urlopen(req)
    soup = BeautifulSoup(res, 'html.parser')
    return soup, href_text

def get_href_soup_userfav(soup_origin, tag_selector):
    tag = soup_origin.select(tag_selector)
    if len(tag) == 0:
        return None
    href_text = soup_origin.select(tag_selector)[0].get('href')
    req = urllib.request.Request(url=mypage_url + href_text, headers=headers)
    res = urllib.request.urlopen(req)
    soup = BeautifulSoup(res, 'html.parser')
    return soup

# ユーザからお気に入り情報を取得
def get_user_favorite_novel(soup_user, user_url):
    soup_user_favorite = get_href_soup_userfav(soup_user, '#favnovel > div > a')
    if soup_user_favorite == None:
        return None
    fav_title_list = soup_user_favorite.select('.title > a')
    ret = []
    for user_fav_title in fav_title_list:
        fav_title_url = user_fav_title.get('href')
        fav_title = user_fav_title.get_text()
        redis_user.sadd(fav_title_url, user_url)
        redis_user.sadd(user_url, fav_title_url)
        redis_novel.hset(fav_title_url, 'novel_url', fav_title_url)
        redis_novel.hset(fav_title_url, 'novel_title', fav_title)
        print(user_url)
        print(fav_title + '：' + fav_title_url)
        ret_novel = {'title': fav_title, 'url': fav_title_url}
        ret.append(ret_novel)
    return ret

def scraping_main(url):
    # 小説情報の取得
    main_request = urllib.request.Request(url=url, headers=headers)
    main = urllib.request.urlopen(main_request)
    soup_novel_main = BeautifulSoup(main, 'html.parser')
    novel_title = soup_novel_main.select('#novel_color > p')[0].get_text()
    teller_name = soup_novel_main.select('#novel_color > div.novel_writername')[0].get_text().strip().strip('作者：')

    # 作者情報の取得
    # teller_url_tag = soup_novel_main.select('#novel_footer > ul > li:nth-of-type(1) > a')
    # teller_url = teller_url_tag[0].get('href')

    # redisへデータを格納
    redis_novel.hset(url,'novel_title' ,novel_title)
    redis_novel.hset(url,'novel_url' ,url)
    redis_novel.hset(url,'novel_teller' ,teller_name)

    # 感想の取得
    soup_feelings = get_href_soup_one(soup_novel_main, '#head_nav > li:nth-of-type(3) > a')
    for i in range(len(soup_feelings.select('.waku'))):
        soup_user, user_url = get_href_soup_user(soup_feelings, '#contents_main > div:nth-of-type(' + str(i + 2) + ') > div.comment_user > a')
        if soup_user == None:
            continue
        get_user_favorite_novel(soup_user, user_url)
        
    # レビューの取得
    soup_review = get_href_soup_one(soup_novel_main, '#head_nav > li:nth-of-type(4) > a')
    for i in range(len(soup_review.select('.review_user'))):
        soup_user, user_url = get_href_soup_user(soup_review, '#contents_main > div:nth-of-type(' + str(i + 1) + ') > div > div.review_user > a')
        if soup_user == None:
            continue
        get_user_favorite_novel(soup_user, user_url)

def get_data_redis(novel_url):
    try:
        check_novel = redis_novel_info.hgetall(novel_url)
        check_novel[KEY_TELLER.encode()]
    except KeyError:
        print('err')
        return []


    novel_fav_usr = redis_set_data.smembers(novel_url)
    novel_url_set = set()
    for usr in novel_fav_usr:
        usr_fav_novel = redis_set_data.smembers(usr.decode())
        for novel in usr_fav_novel:
            novel_url_set.add(novel.decode())
    novel_url_list = list(novel_url_set)
    ret_list = []
    for r in novel_url_list:
        novel_info = redis_novel_info.hgetall(r)
        if novel_info == {}:
            continue
        tmp = {
            KEY_TITLE: novel_info[KEY_TITLE.encode()].decode(),
            # KEY_TELLER: novel_info[KEY_TELLER.encode()].decode(),
            KEY_URL: novel_info[KEY_URL.encode()].decode()
        }
        ret_list.append(tmp)
    return ret_list



    #### 別APIで小説内容の取得、AXIOSによる非同期表示 ####



if __name__ == "__main__":
    url = 'https://ncode.syosetu.com/n6621fl/'
    get_recommend_novel(url)

