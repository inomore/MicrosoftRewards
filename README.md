# MicrosoftRewards
## About
MicrosoftRewards is an automated point earning script that works with bing.com to earn points that can be redeemed for giftcards.

## How this differs from sealemar/BingRewards
1. Easier setup for many accounts, just a line with user agents to accounts.txt.
2. Updated to relavent code, urllib2 vs requests == more readable and user friendly.
3. Many instances of out of date data being posted to Bing in sealemar's, while it did work, it would be easy to detect.
4. Human-like searching algorithim:
	- Searches throughout the specified time period, currently about 6-8 hours (25000-30000 seconds).
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
## Config

### General


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
