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
		print(totalp)
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
		#14-15 season만
		#일단 2010-11 시즌부터
		#season = season.ix[0:5,:]
		
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
	def player_tracking_data(self,fr,to): 
		it_num = int(to)-int(fr)+1 # fr의 경우 iteration하면서 값이 변화한다. 따라서 write 할때를 위해서 iteration 숫자를 남겨둔다.
		title=["CatchShoot","Defense",'Drives','Passing','Possessions','PullUpShot','Rebounding','Efficiency','SpeedDistance','ElbowTouch','PostTouch','PaintTouch']
		
		for it in range(0,int(to)-int(fr)+1):
			vars()['DB'+str(it)]=pd.DataFrame()

			for i in range(0,len(title)):
				base_url1="http://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=PerGame&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType="
				measure_type=title[i]
				base_url2="&Season="
				to = str(int(fr[2:4])+1)[0:2]
				if len(to)==1:
					to ='0'+to
				season = fr + '-' + to # yyyy-yy 형태.

				base_url3 = "&SeasonSegment=&SeasonType=Regular+Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
				url=base_url1+measure_type+base_url2+season+base_url3
				data = json.loads(requests.get(url).text)
				tmp = pd.DataFrame(data['resultSets'][0]['rowSet'],columns = data['resultSets'][0]['headers'])

				#SpeedDistance 때문에 MIN 을 int 화 해줘야 한다.
				if title[i] == 'SpeedDistance':
					tmp = tmp.drop('MIN',1)
					tmp = tmp.drop('MIN1',1)
					vars()['DB'+str(it)] = pd.merge(vars()['DB'+str(it)],tmp,how='left',on=['PLAYER_ID','TEAM_ABBREVIATION','PLAYER_NAME','TEAM_ID','GP','W','L'])
					print(title[i])
					continue
				if i == 0 :
					vars()['DB'+str(it)]=(vars()['DB'+str(it)]).append(tmp)
					vars()['DB'+str(it)].insert(0,'season',season)
				else :
					vars()['DB'+str(it)]=pd.merge(vars()['DB'+str(it)],tmp,how='left')
				print (title[i])
			fr = str(int(fr)+1)
			
		#concat DBs 

		frame = []
		print('DBs : ',it_num)
		for it in range(0,it_num):
			frame.append(vars()['DB'+str(it)])
		DB = pd.concat(frame)


		return DB
	def player_cumulative_GPT(self,fr,to):

		DB = pd.DataFrame() # 빈 DB 만들기.

		for i in range(0,int(to)-int(fr)+1):
			base_url1 = "http://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season="
			to = str(int(fr[2:4])+1)[0:2]
			if len(to)==1:
				to ='0'+to
			season = fr + '-' + to # yyyy-yy 형태.
			base_url2 = "&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight="
			data = json.loads(requests.get(base_url1 + season + base_url2).text)
			
			#저장할 dataset
			tmp = pd.DataFrame(data['resultSets'][0]['rowSet'],columns = data['resultSets'][0]['headers'])
			tmp['season']=season
			DB = DB.append(tmp)

			print(fr)
			print(base_url1 + season + base_url2)
			fr = str(int(fr)+1)

			

		return DB

	def add_position_in_bios(self,DB):
		url1= "http://stats.nba.com/stats/commonplayerinfo?LeagueID=00&PlayerID="
		url2 = "&SeasonType=Regular+Season"
		DB['position'] = 0
		for i in range(0,len(DB)):
			ID = DB.ix[i,'PLAYER_ID']
			url = url1 + str(ID) + url2
			data = json.loads(requests.get(url).text)
			DB.ix[i,'position']=pd.DataFrame(data['resultSets'][0]['rowSet'],columns = data['resultSets'][0]['headers'])['POSITION'][0]
			print (DB.ix[i,'PLAYER_NAME'])
		return DB

	def add_birthdate_in_bios(self,DB):
		url1= "http://stats.nba.com/stats/commonplayerinfo?LeagueID=00&PlayerID="
		url2 = "&SeasonType=Regular+Season"
		DB['BIRTHDATE'] = 0
		for i in range(0,len(DB)):
			ID = DB.ix[i,'PLAYER_ID']
			url = url1 + str(ID) + url2
			data = json.loads(requests.get(url).text)
			DB.ix[i,'BIRTHDATE']=pd.DataFrame(data['resultSets'][0]['rowSet'],columns = data['resultSets'][0]['headers'])['BIRTHDATE'][0]
			print (DB.ix[i,'PLAYER_NAME'])
		return DB


