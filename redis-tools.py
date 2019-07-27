import redis
# Redis に接続します
r = redis.Redis(host='narou-redis', db=0)
r2 = redis.Redis(host='narou-redis', db=1)

url = 'https://ncode.syosetu.com/n6621fl/'

# ハッシュを取得します
man1 = r.hgetall(url)
print(man1['novel_title'.encode()].decode())
print(man1['novel_url'.encode()].decode())
print(man1['novel_teller'.encode()].decode())

man2 =r.hgetall('https://ncode.syosetu.com/n9187eo/')
print(man2['novel_title'.encode()].decode())

name = r2.smembers('https://ncode.syosetu.com/n6093en/')
print([i for i in name])
name2 = r2.smembers('https://mypage.syosetu.com/272086/')
print([i for i in name2])