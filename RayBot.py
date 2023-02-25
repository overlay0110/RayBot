import telegram
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters

import requests

import json

from googletrans import Translator

from urllib.request import urlopen
from bs4 import BeautifulSoup

def call_api(url, para, head = {}):
    res = requests.post(url, para )
    # print(res.text)
    return json.loads(res.text)

def linkStr(link):
    return "https://movie.naver.com"+link

def getMovie(cnt = 10):
	html = urlopen("https://movie.naver.com/movie/running/current.nhn?order=reserve")
	bsObj = BeautifulSoup(html, "html.parser")

	ul = bsObj.find("ul",{"class":"lst_detail_t1"}).findAll("li")
	datas = []

	for li in ul[0:cnt]:
		img = li.find("img")['src']
		title = li.find("dt",{"class":"tit"}).find("a").get_text()
		score = li.find("div",{"class":"star_t1"}).find("a").find("span",{"class":"num"}).get_text()
		link = li.find("dt",{"class":"tit"}).find("a")['href']
		concent = getConcent(link)
		datas.append({
			"img":img,
			"title":title,
			"score":score,
			"link": linkStr(link),
			"concent":concent[:55]
		})
		#print(len(datas))
	return datas
    
def getConcent(link):
    html = urlopen("https://movie.naver.com"+link)
    bsObj = BeautifulSoup(html, "html.parser")
    
    try:
        return  bsObj.find("p",{"class","con_tx"}).get_text()
    except AttributeError:
        return "줄거리없음"

def getNewGame(cnt = 10):
	baseUrl = "https://www.gamemeca.com"
	html = urlopen(baseUrl+"/news.php")
	bsObj = BeautifulSoup(html, "html.parser")

	ul = bsObj.find("ul",{"class":"list_news"}).findAll("li")
	datas = []

	for li in ul[0:cnt]:
		img = li.find("a",{"class":"static-thumbnail"}).find("img")['src']
		link = baseUrl + li.find("a",{"class":"static-thumbnail"})['href']
		
		if(li.find("div",{"class":"cont_thumb_h"}) == None):
			title = li.find("div",{"class":"cont_thumb"}).get_text()
		else:
			title = li.find("div",{"class":"cont_thumb_h"}).get_text()

		if(li.find("div",{"class":"desc_thumb_h"}) == None):
			concent = li.find("div",{"class":"desc_thumb"}).get_text()
		else:
			concent = li.find("div",{"class":"desc_thumb_h"}).get_text()

		datas.append({
			"img":img,
			"link":link,
			"title":title,
			"concent":concent[:55]
		})

	return datas

def getNewTech(cnt = 10):
	baseUrl = "https://www.itworld.co.kr"
	html = urlopen(baseUrl+"/t/55815/%EB%94%94%EC%A7%80%ED%84%B8%20%EB%94%94%EB%B0%94%EC%9D%B4%EC%8A%A4")
	bsObj = BeautifulSoup(html, "html.parser")

	ul = bsObj.find("div",{"class":"node-list"}).findAll("div", {"class":"card"})
	datas = []

	for li in ul[0:cnt]:
		img = baseUrl + li.find("div").find("div",{"class":"thumb"}).find("a").find("img")['src']
		link = baseUrl + li.find("div").find("div",{"class":"thumb"}).find("a")['href']
		title = li.find("div").find("div",{"class":"col"}).find("div").find("h5",{"class":"card-title"}).get_text()
		concent = li.find("div").find("div",{"class":"col"}).find("div").find("p",{"class":"crop-text-2"}).get_text()

		datas.append({
			"img":img,
			"link":link,
			"title":title,
			"concent":concent[:55]
		})

	return datas

print('chat_bot_start')

tran = Translator()
help_msg = """
pwcre or 비번생성/{search}/{email} -> res : { copy link }
pw or 비번/{search} -> res : { copy link }
pwk or 비번키 -> res : { for search }

tran or 번역/{text} -> res :  {result text or catch msg}
tran2 or 번역2/{lan}/{text} -> res :  {result text or catch msg}

game or 게임/{count -> d 10(MAX 10)}
new or 신제품/{count -> d 10(MAX 10)}
movie or 영화/{count -> d 10(MAX 10)}

log or 기록/{text}
now or 오늘 -> res : {date for rowid. text }
del or 기록삭제/{rowid} -> res : {success or fail msg}
all or 전체 -> res : {link}

fcm or fcmp/{MESSSGE}/{TOKEN}/{key(optional)} -> res : { firebase res value }
"""

api_token = ""
chat_id = ""

my_server_url = ""

bot = telegram.Bot(token=api_token)

updater = Updater(token=api_token, use_context=True)
dispatcher = updater.dispatcher
updater.start_polling()

qna_datas = {
    "안녕":"o.o/",
	"안녕하세요":"\(o.o)/",
}

def handler(update, context):
	user_text = update.message.text

	if(user_text == '/help' or user_text == 'help'):
		bot.send_message(chat_id=chat_id, text=help_msg)
		return

	piece = user_text.split('/')

	if(piece[0] == 'pwcre' or piece[0] == '비번생성'):
		res = call_api(my_server_url, { 'para' : 'ray_bot_pwcre', 'search' : piece[1], 'email' : piece[2] })

		bot.send_message(chat_id=chat_id, text="Password : [copy]("+res['result']+")", parse_mode=telegram.ParseMode.MARKDOWN)
		return

	if(piece[0] == 'pw' or piece[0] == '비번'):
		res = call_api(my_server_url, { 'para' : 'ray_bot_pw', 'search' : piece[1],  })

		bot.send_message(chat_id=chat_id, text="Password : [copy]("+res['result']+")", parse_mode=telegram.ParseMode.MARKDOWN)
		return

	if(piece[0] == 'pwk' or piece[0] == '비번키'):
		res = call_api(my_server_url, { 'para' : 'ray_bot_pwk'  })
		result = ''
		for data in res['result']:
			result += data+'\n'

		bot.send_message(chat_id=chat_id, text=result)
		return

	if(piece[0] == 'tran' or piece[0] == '번역'):
		lan='en'
		set_value = user_text.replace(piece[0]+'/','')

		res = tran.translate(piece[1], dest=lan)

		bot.send_message(chat_id=chat_id, text=res.text)
		return

	if(piece[0] == 'tran2' or piece[0] == '번역2'):
		lan='en'

		if len(piece) > 1:
			lan = piece[1]

		set_value = user_text.replace(piece[0]+'/'+piece[1]+'/','')

		res = tran.translate(set_value, dest=lan)

		bot.send_message(chat_id=chat_id, text=res.text)
		return

	if(piece[0] == 'game' or piece[0] == '게임'):
		bot.send_message(chat_id=chat_id, text='Loading...')
		
		if len(piece) > 1:
			res = getNewGame(int(piece[1]))
		else: 
			res = getNewGame()

		for data in res:
			try:
				bot.sendPhoto(chat_id=chat_id, photo=data['img'], caption=data['title']+"\n"+data['concent'], reply_markup={
					"inline_keyboard": [
						[
							{ "text": "Link", "url": data['link'] },
						]
				]})
			except Exception as e:
				bot.send_message(chat_id=chat_id, text='Error : '+str(e))
				bot.send_message(chat_id=chat_id, text='Link : '+str(data['link']))
		return

	if(piece[0] == 'new' or piece[0] == '신제품'):
		bot.send_message(chat_id=chat_id, text='Loading...')
		
		if len(piece) > 1:
			res = getNewTech(int(piece[1]))
		else: 
			res = getNewTech()

		for data in res:
			try:
				bot.sendPhoto(chat_id=chat_id, photo=data['img'], caption=data['title']+"\n"+data['concent'], reply_markup={
					"inline_keyboard": [
						[
							{ "text": "Link", "url": data['link'] },
						]
				]})
			except Exception as e:
				bot.send_message(chat_id=chat_id, text='Error : '+str(e))
				bot.send_message(chat_id=chat_id, text='Link : '+str(data['link']))
		return

	if(piece[0] == 'movie' or piece[0] == '영화'):
		bot.send_message(chat_id=chat_id, text='Loading...')
		
		if len(piece) > 1:
			res = getMovie(int(piece[1]))
		else: 
			res = getMovie()

		for data in res:
			try:
				bot.sendPhoto(chat_id=chat_id, photo=data['img'], caption=data['title']+"\n"+data['concent'], reply_markup={
					"inline_keyboard": [
						[
							{ "text": "Link", "url": data['link'] },
						]
				]})
			except Exception as e:
				bot.send_message(chat_id=chat_id, text='Error : '+str(e))
				bot.send_message(chat_id=chat_id, text='Link : '+str(data['link']))
		return

	if(piece[0] == 'log' or piece[0] == '기록'):
		set_value = user_text.replace(piece[0]+'/','')
		res = call_api(my_server_url, { 'para' : 'ray_bot_log_add', 'value' : set_value  })

		bot.send_message(chat_id=chat_id, text=res['result'])
		return

	if(piece[0] == 'now' or piece[0] == '오늘'):
		res = call_api(my_server_url, { 'para' : 'ray_bot_log_now_list'  })
		result = ''

		result += res['now']+'\n'

		for data in res['result']:
			result += data['rowid']+'. '+data['message']+'\n'

		bot.send_message(chat_id=chat_id, text=result)
		return

	if(piece[0] == 'del' or piece[0] == '기록삭제'):
		res = call_api(my_server_url, { 'para' : 'ray_bot_log_del', 'value' : piece[1]  })

		bot.send_message(chat_id=chat_id, text=res['result'])
		return

	if(piece[0] == 'all' or piece[0] == '전체'):
		res = call_api(my_server_url, { 'para' : 'ray_bot_log_all'  })

		bot.send_message(chat_id=chat_id, text="All List : [Link]("+res['result']+")", parse_mode=telegram.ParseMode.MARKDOWN)
		return

	if(piece[0] == 'fcm'):
		res = call_api(my_server_url, { 
			'para' : 'ray_bot_fcm_push',
			'mode' : 'v1',
			'msg' : piece[1],
			'token' : piece[2],
		})

		bot.send_message(chat_id=chat_id, text=res['result'])
		return

	if(piece[0] == 'fcmp'):
		res = call_api(my_server_url, { 
			'para' : 'ray_bot_fcm_push',
			'mode' : 'pmode',
			'msg' : piece[1],
			'token' : piece[2],
		})

		bot.send_message(chat_id=chat_id, text=res['result'])
		return

	if user_text in qna_datas: 
		bot.send_message(chat_id=chat_id, text=qna_datas[user_text])
	else:
		bot.send_message(chat_id=chat_id, text='Command does not exist.')
 
echo_handler = MessageHandler(Filters.text, handler)
dispatcher.add_handler(echo_handler)