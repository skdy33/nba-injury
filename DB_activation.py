from injury_data_crawling import crawler_nba

crawler = crawler_nba()

# injury DB 초기화
DB = crawler.injury_from_to('2010-01-01','2015-12-01')
DB.to_csv("injury_data.csv",index=None)