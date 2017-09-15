# MicrosoftRewards
## About
MicrosoftRewards is an automated point earning script that works with bing.com to earn points that can be redeemed for giftcards.

## How this differs from sealemar/BingRewards
1. Easier setup for many accounts, just a line with user agents to accounts.txt.
2. Updated to relavent code, urllib2 vs requests == more readable and user friendly.
3. Many instances of out of date data being posted to Bing in sealemar's, while it did work, it would be easy to detect.
4. Human-like searching algorithim:
	- Searches throughout the specified time period, currently about 5.5-8.3 hours (20000-30000 seconds).
	- How it determines when to search:
		- First it gets the amount of searches needed and adds the salt.
		- Then gets this number of random numbers between 0 and specified end time.
		- Lastly loops until it hits one of these magic numbers and does a search.
			- Example: Next search in 328 seconds. Desktop search. Next search in 1290 seconds. etc.
	- Not so random switching between desktop and mobile, based on the last search type.
	- Randomly switching between desktop and mobile would result in very unhumanlike results, because who does that?
		- Example: Search phone then five seconds later search mobile. 
	- While this could happen once or twice, constantly is a red flag.
	- Switching query generators on the fly, using the same query generator for every account causes most of the same stuff to be searched on all accounts.
	- Performs the two bonus 10 point searches, normal and the one for Edge.
5. Multi-threads for scaling purposes and waits in between logins.
6. User agent defining is mandatory per account because who really switches browsers/pc's every day?
7. Proxy per account for scaling purposes as well.

## Requirements
python 2.7

pip (found in C:\Python27\Scripts\pip.py usually if installed)

pip installer if you don't have it: https://bootstrap.pypa.io/get-pip.py
```
> python get-pip.py
> cd to installation dir
> python -m pip install -U bs4 requests setuptools pip
```

## Running The Script
Copy *accounts.txt.dist* to *accounts.txt*  

Linux/Mac
```bash
$ cd path/to/microsoftrewards
$ ./bing.py
```
Windows
```
> cd path\to\microsoftrewards
> python bing.py
```

Extra Args
```python
> python bing.py --report 
#logs into all accounts and gets point totals
```

## Config

### General
```python
#common.py for editing these values, low and high means random value in between the two
redeem_ready = 5000 #point value at which an account goes in redeem ready section of report
last_type_chance = 0.8 #chance that searching algorithim will use last type search
new_thread_low = 0 #low for waiting time to login
new_thread_high = 1800 #high for waiting time to login
querytime_low = 20000 #low for searching time
querytime_high = 30000 #high for searching time
querysalt_low = -5 #low for amount of less/extra searches
querysalt_high = 20 #high for amount of less/extra searches
```

### Accounts
You can have as many accounts as you need, one account per line in *accounts.txt*. 
**Note**: Proxies are optional and are on a per account basis. 
**Note**: User-Agent fields are NOT optional.
**Note**: Two-Factor Authentication (2FA) is not supported.
```
email>password>desktop_ua>mobile_ua>proxy
```

### Query Generators
- googleTrends
- wikipedia
