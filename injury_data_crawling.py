import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup as BS


class crawler_nba : 
	def injury_from_to(self,fr,to):
		base_url = "http://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate="
		start_url = "&EndDate="
		end_url = "&ILChkBx=yes&Submit=Search&start"
		idx = 0 # 이건 페이지가 넘어가면서 25를 더해야해

		#먼저 페이지가 몇개가 있는지 알 필요가 있어 totalp
		url = base_url+fr+start_url+to+end_url+str(idx)
		bs = BS(requests.get(url).text,'html.parser')
		totalp = len(bs.select('[class~=bodyCopy]')[2].select('a'))+1

		#pandas에 작성할 헤더 header
		header = ['Date','Team','Acquired','Relinquished','Notes']

		# return 할 DB
		DB = pd.DataFrame([],columns=header)

		for i in range(0,totalp):
			url = base_url+fr+start_url+to+end_url+str(idx)
			bs = BS(requests.get(url).text,'html.parser')

			for player in bs.select('[align~=left]'):
				player_data = pd.DataFrame()
				player_data[header[0]] = [player.select('td')[0].text]
				player_data[header[1]] = [player.select('td')[1].text]
				player_data[header[2]] = [player.select('td')[2].text.replace(" â\x80¢ ","")] # 쩜 지우기
				player_data[header[3]] = [player.select('td')[3].text.replace(" â\x80¢ ","")] # 쩜 지우기
				player_data[header[4]] = [player.select('td')[4].text]
				DB = DB.append(player_data,ignore_index=True)

			#몇페이지 긁었니
			print(i)

			#다음 페이지로 넘어가기
			idx+=25

		return DB



