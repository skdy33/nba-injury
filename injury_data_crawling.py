import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup as BS
import json # stats.nba 에서 network 에 오가는 json 훔쳐오기.
import datetime

class crawler_nba : 
	def injury_from_to(self,fr,to):
		base_url = "http://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate="
		start_url = "&EndDate="
		end_url = "&ILChkBx=yes&Submit=Search&start="
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

	def player_BIOS(self,fr,to): #regular season 임을 명심해라.
		
		DB = pd.DataFrame() # 빈 DB 만들기.

		for i in range(0,int(to)-int(fr)+1):
			base_url1 = "http://stats.nba.com/stats/leaguedashplayerbiostats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&Season="
			season = fr + '-' + str(int(fr[2:4])+1) # yyyy-yy 형태.
			base_url2 = "&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
			data = json.loads(requests.get(base_url1 + season + base_url2).text)
			
			#저장할 dataset
			tmp = pd.DataFrame(data['resultSets'][0]['rowSet'],columns = data['resultSets'][0]['headers'])
			tmp['season']=season
			DB = DB.append(tmp)

			print(fr)
			fr = str(int(fr)+1)

			

		return DB
		
	def player_sortable_stat(self):
		#여기서 season start end csv 를 불러오고, default 롤 2010부터 시작하게 짜놨어.
		season = pd.read_csv('season_start_end.csv',encoding='euc-kr')
		season['regular season start'] = pd.to_datetime(season['regular season start'])
		season['regular season end'] = pd.to_datetime(season['regular season end'])
		#2015년 12월 1일이 마지막으로 잡아놨어.
		season.ix[0,2] = datetime.date(2015,12,1)
		#일단 2010-11 시즌부터
		season = season.ix[0:5,:]
		#define url
		base_url = "http://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom="
		url2 = '&DateTo='
		url3 = '&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season='
		url4 = "&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="

		#DB
		DB = pd.DataFrame()

		#adder
		add = datetime.timedelta(days = 1)

		for i in range(len(season)):
		    regular_season = season.ix[i,1]
		    
		    while 1 : 

		        #search date
		        date = str(regular_season.month) + "%2F" + str(regular_season.day) + "%2F" + str(regular_season.year)
		        url = base_url + date + url2 + date + url3 + season.ix[i,0] + url4
		        rq = requests.get(url).text
		        tmp = pd.DataFrame(json.loads(rq)['resultSets'][0]['rowSet'],columns = json.loads(rq)['resultSets'][0]['headers'])
		        tmp['season'] = season.ix[i,'season']
		        tmp['date'] = regular_season

		        DB = DB.append(tmp,ignore_index=True)
		        regular_season += add

		        print(regular_season.year,regular_season.month,regular_season.day)

		        if regular_season == season.ix[i,'regular season end']:
		            break

		return DB
	def player_tracking_data(self): # 2014-15 season 만을 가져온다.
		title=["CatchShoot","Defense",'Drives','Passing','Possessions','PullUpShot','Rebounding','Efficiency','SpeedDistance','ElbowTouch','PostTouch','PaintTouch']
		DB=pd.DataFrame()
		DB.insert(0,'season','2014-15')

		for i in range(0,len(title)):
		    base_url1="http://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=PerGame&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType="
		    measure_type=title[i]
		    base_url2="&Season=2014-15&SeasonSegment=&SeasonType=Regular+Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
		    url=base_url1+measure_type+base_url2
		    data = json.loads(requests.get(url).text)
		    tmp = pd.DataFrame(data['resultSets'][0]['rowSet'],columns = data['resultSets'][0]['headers'])
		    if i == 0 :
		        DB=DB.append(tmp)
		    else :
		        DB=pd.merge(DB,tmp,how='inner')
		    print (i)

		return DB


