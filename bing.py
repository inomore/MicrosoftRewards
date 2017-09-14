import sys
from pkgutil import iter_modules
modules = set(x[1] for x in iter_modules())

try:
	import requests
	from bs4 import BeautifulSoup as BS
except ImportError:
	bs4missing = False
	requestsmissing = False
	if "requests" not in modules:
		print "Missing package: requests"
		requestsmissing = True
	if "bs4" not in modules:
		print "Missing package: bs4"
		bs4missing = True
	print
	print "---Installing---"
	if requestsmissing and bs4missing:
		print "pip install bs4 requests"
	elif requestsmissing and not bs4missing:
		print "pip install requests"
	else:
		print "pip install bs4"
	sys.exit(1)

import googleTrends as gt
import wikipedia as wiki
import common as c
import random
import urllib
import time
import urllib3
import re
import os
from multiprocessing import Pool
from random import randint

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def safe_print(content):
    print "{0}\n".format(content),

def search_account(account):
	#initialize
	account = account.replace("\n","")
	email = account.split(">")[0]
	password = account.split(">")[1]
	desktop_ua = account.split(">")[2]
	mobile_ua = account.split(">")[3]
	try:
		proxy = account.split(">")[4]
	except IndexError:
		proxy = "127.0.0.1:8080"
	mobile_headers = c.headers
	mobile_headers["User-Agent"] = mobile_ua
	desktop_headers = c.headers
	desktop_headers["User-Agent"] = desktop_ua
	data = {"i13":"0", "type":"11", "LoginOptions":"3", "lrt":"", "ps":"2", "psRNGCDefaultType":"", "psRNGCEntropy":"", "psRNGCSLK":"", "canary":"", "ctx":"", "NewUser":"1", "FoundMSAs":"", "fspost":"0", "i21":"0", "i2":"1", "i17":"0", "i18":"__ConvergedLoginPaginatedStrings%7C1%2C__ConvergedLogin_PCore%7C1%2C", "i19":"2" + str(randint(0, 5000))}
	proxies = {"http":"127.0.0.1:8080", "https":"127.0.0.1:8080"}
	data["login"] = email
	data["loginfmt"] = email
	data["passwd"] = password

	#wait random amount before logging in
	wait_secs = random.randint(c.new_thread_low,c.new_thread_high)
	safe_print("sleeping for " + str(wait_secs) + " seconds")
	time.sleep(wait_secs)

	#login mobile and desktop
	if proxy != "127.0.0.1:8080":
		res = requests.get(c.hostURL, headers=desktop_headers, proxies=proxies)
	else:
		res = requests.get(c.hostURL, headers=desktop_headers)
	desktop_headers["Referer"] = res.url
	index = res.text.index("WindowsLiveId")
	cutText = res.text[index + 16:]
	loginURL = cutText[:cutText.index("\"")]
	loginURL = bytes(loginURL).encode("utf-8").decode("unicode_escape")
	desktop_headers["Host"] = c.loginHost
	if proxy != "127.0.0.1:8080":
		res = requests.get(loginURL, headers=desktop_headers, proxies=proxies)
	else:
		res = requests.get(loginURL, headers=desktop_headers)
	desktop_headers["Referer"] = res.url
	cookies = res.cookies
	cookies["CkTst"] = "G" + str(int(time.time() * 1000))
	index = res.text.index(c.loginPostURL)
	cutText = res.text[index:]
	postURL = cutText[:cutText.index("\'")]
	index = res.text.index("sFTTag")
	cutText = res.text[index:]
	PPFT = cutText[cutText.index("value=") + 7:cutText.index("\"/>")]
	data["PPFT"] = PPFT
	PPSX = 'PassportRN'[:-random.randint(0,9)]
	data["PPSX"] = PPSX
	cookies["wlidperf"] = "FR=L&ST=" + str(int(time.time() * 1000))
	if proxy != "127.0.0.1:8080":
		res = requests.post(postURL, cookies=cookies, data=data, headers=desktop_headers, proxies=proxies)
	else:
		res = requests.post(postURL, cookies=cookies, data=data, headers=desktop_headers)
	desktop_headers["Referer"] = res.url
	form = BS(res.content, "html.parser").findAll("form")[0]
	params = dict()
	for field in form:
		params[field["name"]] = field["value"]
	desktop_headers["Host"] = c.host
	if proxy != "127.0.0.1:8080":
		res = requests.post(form.get("action"), cookies=cookies, data=params, headers=desktop_headers, proxies=proxies)
	else:
		res = requests.post(form.get("action"), cookies=cookies, data=params, headers=desktop_headers)
	desktop_headers["Referer"] = res.url
	cookies = res.cookies
	safe_print(email + ": logged in")
	finder = re.compile("'(\d+)'")
	if proxy != "127.0.0.1:8080":
		page = requests.get("https://www.bing.com/rewardsapp/reportActivity", cookies=cookies, headers=desktop_headers, proxies=proxies)
	else:
		page = requests.get("https://www.bing.com/rewardsapp/reportActivity", cookies=cookies, headers=desktop_headers)
	oldPoints = int(finder.search(page.content).group(1))
	safe_print(email + ": current points: " + str(oldPoints))

	#parse rewards
	mobile_headers["User-Agent"] = mobile_ua
	if proxy != "127.0.0.1:8080":
		page = requests.get("http://www.bing.com/rewardsapp/flyoutpage/?style=v2", cookies=cookies, headers=mobile_headers, verify=False, proxies=proxies)
	else:
		page = requests.get("http://www.bing.com/rewardsapp/flyoutpage/?style=v2", cookies=cookies, headers=mobile_headers, verify=False)
	soup = BS(page.content,"html.parser")
	rewards = soup.findAll("ul",{"class" : "item"})
	extra_offers = []
	forbiddenwords = re.compile('quiz|redeem|goal|challenge|activate|earn more points', re.IGNORECASE)
	progress = re.compile("(\d+) of (\d+)")
	for reward in rewards:
		reward_text = reward.text.encode("utf-8")
		if not forbiddenwords.search(reward_text):
			if "PC search" in reward_text:
				desktop_left = (int(progress.search(reward_text).group(2)) / 5) - (int(progress.search(reward_text).group(1)) / 5)
				desktop_searches = (int(progress.search(reward_text).group(1)) / 5)
			elif "Mobile search" in reward_text:
				mobile_left = (int(progress.search(reward_text).group(2)) / 5) - (int(progress.search(reward_text).group(1)) / 5)
				mobile_searches = (int(progress.search(reward_text).group(1)) / 5)
			elif "Daily search" in reward_text:
				desktop_left = (int(progress.search(reward_text).group(2)) / 5) - (int(progress.search(reward_text).group(1)) / 5)
				desktop_searches = (int(progress.search(reward_text).group(1)) / 5)
				mobile_left = 0
				mobile_searches = 0
			else:
				for a in reward.findAll("a", href=True):
					if a["href"] != "javascript:void(0)":
						extra_offers.append(a["href"].encode("utf-8"))
	try:
		test = int(desktop_left + mobile_left)
	except UnboundLocalError:
		safe_print(email + ": failed to login")
		return

	#searches throughout the period of time 5.5-8.3 hours default
	querytime = random.randint(c.querytime_low,c.querytime_high)
	querysalt = random.randint(c.querysalt_low,c.querysalt_high)
	querytimes = random.sample(range(1,int(querytime)),int(desktop_left + mobile_left + querysalt + len(extra_offers)) - 1)
	printed = False
	lasttype = random.choice(["desktop","mobile"])
	for i in range(0,int(querytime)+1):
		time.sleep(1)
		try:
			if not printed:
				safe_print(email + ": next search in: " + str(min(filter(lambda x: x > i,querytimes)) - i) + " seconds")
				printed = True
		except ValueError:
			safe_print(email + ": searches done")
			desktop_headers["User-Agent"] = desktop_ua
			if proxy != "127.0.0.1:8080":
				page = requests.get("https://www.bing.com/rewardsapp/reportActivity", cookies=cookies, headers=desktop_headers, proxies=proxies)
			else:
				page = requests.get("https://www.bing.com/rewardsapp/reportActivity", cookies=cookies, headers=desktop_headers)
			newPoints = int(finder.search(page.content).group(1))
			safe_print(email + ": points earned: " + str(newPoints - oldPoints))
			safe_print(email + ": total points: " + str(newPoints))
			if newPoints >= c.redeem_ready:
				redeem_ready = open("redeem_ready.txt","a+")
				redeem_ready.write(str({email : {"earned" : newPoints - oldPoints, "total" : newPoints}}))
				redeem_ready.close()
			else:
				not_ready = open("not_ready.txt","a+")
				not_ready.write(str({email : {"earned" : newPoints - oldPoints, "total" : newPoints}}))
				not_ready.close()
			return
		if i in querytimes:
			if mobile_searches > mobile_left and desktop_searches > desktop_left and len(extra_offers) > 0:
				offer = random.choice(extra_offers)
				extra_offers.remove(offer)
				if proxy != "127.0.0.1:8080":
					requests.get("https://bing.com" + offer, cookies=cookies, headers=desktop_headers, proxies=proxies)
				else:
					requests.get("https://bing.com" + offer, cookies=cookies, headers=desktop_headers)
			elif desktop_searches > desktop_left and mobile_searches < mobile_left:
				lasttype = "mobile"
			elif desktop_searches < desktop_left and mobile_searches > mobile_left:
				lasttype = "desktop"
			types = []
			num = int(c.last_type_chance * 10)
			count = 0
			while count != num:
				types.append(lasttype)
				count += 1
			count = 0
			num = int((1 - c.last_type_chance) * 10)
			while count != num:
				if "desktop" in lasttype:
					types.append("mobile")
				else:
					types.append("desktop")
				count += 1
			lasttype = random.choice(types)
			num = randint(0,10)
			if num < 4:
				gen = wiki.queryGenerator(1)
				url = c.searchURL + str(gen.generateQueries(1,set()).pop())
			elif num < 9:
				gen = gt.queryGenerator(1)
				url = c.searchURL + str(gen.generateQueries(1,set()).pop())
			else:
				desktop_headers["User-Agent"] = desktop_ua
				if proxy != "127.0.0.1:8080":
					page = requests.get("https://bing.com/hpm?", headers=desktop_headers, proxies=proxies)
				else:
					page = requests.get("https://bing.com/hpm?", headers=desktop_headers)
				hrefs = []
				soup = BS(page.content,"html.parser")
				for a in soup.findAll("a"):
					if a["href"] != "javascript:void(0)" and "QUIZ" not in a["href"]:
						hrefs.append(a["href"])
				url = "https://bing.com" + str(random.choice(hrefs))
				hpm = True
			if "desktop" in lasttype:
				desktop_searches += 1
				desktop_headers["User-Agent"] = desktop_ua
				if hpm:
					desktop_headers["Referer"] = "https://bing.com"
					hpm = False
				if proxy != "127.0.0.1:8080":
					requests.get(url, cookies=cookies, headers=desktop_headers, proxies=proxies)
				else:
					requests.get(url, cookies=cookies, headers=desktop_headers)
			if "mobile" in lasttype:
				mobile_searches += 1
				mobile_headers["User-Agent"] = mobile_ua
				if hpm:
					desktop_headers["Referer"] = "https://bing.com"
					hpm = False
				if proxy != "127.0.0.1:8080":
					requests.get(url, cookies=cookies, headers=mobile_headers, proxies=proxies)
				else:
					requests.get(url, cookies=cookies, headers=mobile_headers)
			safe_print(email + ": " + lasttype + " search: " + query)
			printed = False
if __name__ == "__main__":
	if os.path.isfile("accounts.txt"):
		safe_print("Found accounts.txt")
		input_file = open("accounts.txt","r")
	else:
		safe_print("Did you remember to rename accounts.txt.dist to accounts.txt?")
		safe_print("Could not find accounts.txt")
	accounts = []
	for line in input_file:
		accounts.append(line)
	input_file.close()
	pool = Pool(processes=len(accounts))
	pool.map(search_account, accounts)
	output_file = open("report.txt","w+")
	output_file.write("---REDEEM READY---\n")
	redeem_ready = open("redeem_ready.txt","r")
	for line in redeem_ready:
		output_file.write(line + "\n")
	output_file.write("---NOT READY---\n")
	not_ready = open("not_ready.txt","r")
	for line in not_ready:
		output_file.write(line + "\n")
	output_file.close()
	redeem_ready.close()
	not_ready.close()
	os.remove("not_ready.txt")
	os.remove("redeem_ready.txt")
