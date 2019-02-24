
# How to get all NASDAQ end-of-day Stock Prices—literally all

How many lines of python code are required to download the end-of-day stock prices of **all companies** quoted on NASDAQ? Less than 50 lines of pure code! (Well, about 100 if you count in comments.)

Let's see how you can get this done:

## Step 1: Get NASDAQ stock symbols

First of all, we need the stock symbol of every company that is listed on NASDAQ. For example, the stock symbol of `Apple` or `Facebook` is `APPL`/`FB` respectively. Since it is the 21st century, we would like to get this list without copy-pasting the stock symbols of every single company (of which there are more than 3000!). Luckily, NASDAQ publishes a `.txt` file lists all quoted companies. [Click here to check it out yourself.](ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt) So how do we get this `.txt` file on our computer to make use of it later on? In short, we'll use the `ftp` module of `python 3` to extract the relevant information.

``` Python
### get all stock symbols of NASDAQ

#load relevant modules
from ftplib import FTP
import urllib.request

#define how every line of txt file should be parsed
def parser(s):
	'''
	This function returns, for every line of the symbols txt file, the stock symbol
	and name of the corresponding company.
	
	Arguments:
	----------
	- s: line of txt file
	
	Returns:
	--------
	Python dictionary with stock symbol and company name
	'''
	### do not load data of test stocks
	if "Symbol" in s or "NASDAQ TEST STOCK" in s or "File Creation Time" in s or "Pilot Test" in s:
		pass
	else:
		general_split = s.split(" - ", )[0]
		symbol = general_split.split("|")[0]
		company_name = general_split.split("|")[1]
		### global var as callback in ftp.retrlines does not accept arguments
		nasdaq_dict.append({'symbol': symbol, 'name': company_name})

#define empty dictionary, global variable used in parser()
nasdaq_dict = []

#execute FTP request
ftp = FTP("ftp.nasdaqtrader.com")
ftp.login()
ftp.retrlines("RETR /symboldirectory/nasdaqlisted.txt", callback=parser)
ftp.quit()
```

Overall, the important part of this block of code is to define how every single line of the `.txt` file should be read in, which I've defined in `parser(s)`. This function basically extracts from, say, `ABIO|ARCA biopharma, Inc. - Common Stock|S|N|D|100|N|N` the stock symbol `ABIO` and the company name `ARCA biopharma, Inc.`. This information is saved in a python dictionary, which is, more or less, a `JSON`-like object.

## Step 2: Download Data

Now, after having downloaded all stock symbols of NASDAQ, we'll need an API to download the actual stock data. Unfortunately, [quandl.com](https://www.quandl.com/) moved the NASDAQ API to their premium services, and the API of [Alpha Vantage](https://www.alphavantage.co/) has a daily API quota of 500 for non-paying users (at time of writing, it is Frugal February, so I can clearly not pay for an API :P ). Fortunately, there is also an API of [Investor Exchange](https://iextrading.com/); book-aholics among you may know this company from [Flash Boys](https://en.wikipedia.org/wiki/Flash_Boys). Fortunately, this company is not only 'the good guy' in the book, and their API is completely free, does not require registration, and does not impose strict API quota.

Therefore, we can now simply iterate over the cached stock symbols we downloaded before, and retrieve the end-of-year stock prices for the past 5 years. (This is probably the only drawback of the IEX API, it only allows you to pull info from the past 5 years. If you want to get the entire timeline, the next-best free alternative is to use the API of Alpha Vantage and run it for 1 week).

To pull data from the IEX API, you just need to combine `https://api.iextrading.com/1.0/stock/` + **your stock symbol** + `/chart/5y`. [Click here to get the stock data for Apple](`https://api.iextrading.com/1.0/stock/AAPL/chart/5y`). The code below saves all stock data as `.csv` files in the folder `stockdata`, using the stock symbol as the filename.


``` Python
#iterate over each element of stock symbol dictionary, 
#and dump 5-year end-of-day stock prices in the folder 'stockdata'

def stock_pull(stock_symbol, link, target_folder):
	'''
	This function will i) download file from url, ii) convert downloaded file into
	a pandas dataframe, and iii) save the file as a csv, where the numeric index will
	not be saved.
	
	Arguments:
	----------
	
	- stock_symbol: stock symbol
	- link: url from which stock data can be downloaded
	- target_folder: folder in which data should be saved
	
	Returns:
	--------
	None
	'''
	#load required packages
	import urllib.request
	import pandas as pd
	
	#download file from url
	with urllib.request.urlopen(link) as url:
		data = json.loads(url.read().decode())
	#convert into pandas dataframe
	df = pd.DataFrame(data)
	#save file, don't save numeric index
	filepath = os.path.join(target_folder, stock_symbol + ".csv")
	with open(filepath, 'w') as f:
		df.to_csv(f, index = False)
		
	return None

### define some parameters for subsequent loop
target_folder = "stockdata"
url_prefix = "https://api.iextrading.com/1.0/stock/"
url_suffix = "/chart/5y"

#for every nasday stock symbol that was cached
for index, nasdaq_stock in enumerate(nasdaq_dict):
	# retrieve symbol
	stock_symbol = nasdaq_stock['symbol']
	#build url
	url = url_prefix + stock_symbol + url_suffix
	#call function
	stock_pull(stock_symbol = stock_symbol, link = url, target_folder = target_folder)
	
	#since it takes a while to pull data of > 3000 stocks, 
	#a progress update wouldn't hurt
	if index % 100 == 0:
		print("Working on {}/{}" .format(index+1, len(nasdaq_dict)))
```

### Morale of the story

* One reason why I really like python is that it allows you to do things very quickly, using ~50 lines of code to download entire NASDAQ empitomises this pretty weel.
* While you can get a one-off pull of entire NASDAQ pretty easyily, the true challenge is writing a script that automatically updates your stock data while handling events such as new companies getting listed on NASDAQ or companies being removed from the index. Moreover, the code above is not very pythonic in the way it's written, so you would also need to think about how you want to implement everything in an objective-oriented way. For this reason, my actual DIY fintech scripts have some additional lines of code ;)