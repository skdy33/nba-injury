import pandas as pd
import numpy as np
import datetime

#먼저 부상 기간을 저장해야해. 그니까 activated 가 나은거라고 판단하고, activated 에서 바로 그 전 relinquished까지의 기간을 새로운 변수로 넣으면 되는거야.

#season and end frame  
#season and end frame  
season = ['2015-16','2014-15','2013-14','2012-13','2011-12','2010-11','2009-10']
regular_season_end = [datetime.datetime(2016,4,13),datetime.datetime(2015,4,15),datetime.datetime(2014,4,16),datetime.datetime(2013,4,17),datetime.datetime(2012,4,26),datetime.datetime(2011,4,13),datetime.datetime(2010,4,14)]
db = pd.DataFrame()
db['season']=season
db['regular_season_end']=regular_season_end


DB = pd.read_csv('./nba-injury/nba-injury/injury_data.csv')
#먼저 date class 로 만든다.
DB['Date'] = pd.to_datetime(DB['Date'])
#season data 붙일 곳
DB['season']= 0
for j in range(0,len(DB)):
    for i in range(0,len(db)):
        if ((db['regular_season_end'][i]-DB.ix[j,'Date']).days>0) & ((db['regular_season_end'][i]-DB.ix[j,'Date']).days<300):
            DB.ix[j,'season'] =  db.ix[i,'season']
            break



#이제 각 부상별로 시즌아웃이나 outlier -1, 나머지는 기간으로 넣는 CODE 


DB['injury_period'] = -1 # -1은 seasonout 혹은 없어진? 그런식으로 일단 정의

for ply in range(len(DB)):
    if DB.ix[ply,'Relinquished'] == ' ':
        continue
    for i in range(len(DB[((DB['Acquired'].apply(lambda x : x == DB.ix[ply,'Relinquished'])) & (DB['season'].apply(lambda x : x == DB.ix[ply,'season'])))])):

        if (DB[((DB['Acquired'].apply(lambda x : x == DB.ix[ply,'Relinquished'])) & (DB['season'].apply(lambda x : x == DB.ix[ply,'season'])))].iloc[i,0]-DB.ix[ply,'Date']).days>0:
            minimum = (DB[((DB['Acquired'].apply(lambda x : x == DB.ix[ply,'Relinquished'])) & (DB['season'].apply(lambda x : x == DB.ix[ply,'season'])))].iloc[i,0]-DB.ix[ply,'Date']).days
            continue
        minimum = -1
        
    DB.ix[ply,'injury_period'] = minimum
    print(DB.ix[ply,'Relinquished'],DB.ix[ply,'injury_period'])
        

#generating season_out data
data = pd.read_csv('injury_before_cluster.csv')
data = data[data['Relinquished'].apply(lambda x : x!= ' ')]
season_out = data[data['Notes'].apply(lambda x : 'out for season' in x)]
season_out[season_out['injury_period'].apply(lambda x : x==-1)]
season_out.to_csv('season_out.csv',encoding='euc-kr',index=None)