from datetime import datetime
from bs4 import BeautifulSoup
from time import mktime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import codecs
import os
import time
import re

style.use("dark_background")
path = '/Users/michaelgu/Documents/scikit-learn-investing/data'

def Key_Stats(gather="Total Debt/Equity (mrq)"):
		statspath = path+'/_KeyStats'
		stock_list = [x[0] for x in os.walk(statspath)]
		df = pd.DataFrame(columns = ['Date',
									 'Unix',
									 'Ticker',
									 'DE Ratio',
									 'Price',
									 'stock_p_change',
									 'SP500',
							         'sp500_p_change',
							         'Difference'])

		sp500_df = pd.DataFrame.from_csv("YAHOO-INDEX_GSPC.csv")
		ticker_list = []

		for each_dir in stock_list[1:]:
			each_file = os.listdir(each_dir)
			ticker = each_dir.split("_KeyStats/")[1]
			ticker_list.append(ticker)

			starting_stock_value = False
			starting_sp500_value = False

			if len(each_file) > 0:
				for file in each_file:
					date_stamp = datetime.strptime(file, '%Y%m%d%H%M%S.html')
					unix_time = time.mktime(date_stamp.timetuple())
					full_file_path = each_dir+'/'+file
					# open html file for scraping
					source = codecs.open(full_file_path,'r', 'utf-8').read()
					try:
						value = float(source.split(gather+':</td><td class="yfnc_tabledata1">')[1].split('</td>')[0])
						# get SP500 value 
						try:
							sp500_date = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d')
							row = sp500_df[(sp500_df.index == sp500_date)]
							sp500_value = float(row["Adj Close"])
						except: 
							sp500_date = datetime.fromtimestamp(unix_time-259200).strftime('%Y-%m-%d')
							row = sp500_df[(sp500_df.index == sp500_date)]
							sp500_value = float(row["Adj Close"])
						# scrape stock price 
						soup = BeautifulSoup(source,'lxml')
						for tag in soup.findAll('b'):
							if tag.parent.name == 'big':
								if tag.text != "Key Statistics":
									stock_price = float(tag.text) 	


						if not starting_stock_value:
								starting_stock_value = stock_price
						if not starting_sp500_value:
								starting_sp500_value = sp500_value

						stock_p_change = ((stock_price - starting_stock_value)/starting_stock_value)*100
						sp500_p_change = ((sp500_value - starting_sp500_value)/starting_sp500_value)*100

						# append to panda dataframe
						df = df.append({'Date':date_stamp,
										'Unix':unix_time,
										'Ticker':ticker,
										'DE Ratio':value,
										'Price':stock_price,
										'stock_p_change':stock_p_change,
										'SP500':sp500_value,
										'sp500_p_change':sp500_p_change,
										'Difference':stock_p_change-sp500_p_change}, ignore_index = True)
					except Exception as e:
						pass
			print('indexed data for:', each_dir)

		# plot the data
		for each_ticker in ticker_list:
			try:
				plot_df = df[(df['Ticker'] == each_ticker)]
				plot_df = plot_df.set_index(['Date'])
				plot_df['Difference'].plot(label=each_ticker)
				plt.legend()
			except:
				pass
		plt.show()

		save = gather.replace(' ','').replace(')','').replace('(','').replace('/','')+('.csv')
		print(save)
		df.to_csv(save)

Key_Stats()