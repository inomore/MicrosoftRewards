#!/usr/bin/env python
import sys
from pkgutil import iter_modules
modules = set(x[1] for x in iter_modules())

try:
	import requests
	from bs4 import BeautifulSoup as BS
except ImportError:
	missing = " "
	if "requests" not in modules:
		print "Missing package: requests"
		missing = missing + "requests "
	if "bs4" not in modules:
		print "Missing package: bs4"
		missing = missing + "bs4"
	print
	print "---Installing---"
	print "pip install" + missing
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
import traceback
from multiprocessing import Pool
from random import randint

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def safe_print(content):
    print "{0}\n".format(content),

def search_account(account, retry=False):
	#initialize
	if account == None:
		return
	try:
		account = account.replace("\n","")
		email = account.split(">")[0]
		password = account.split(">")[1]
		desktop_ua = account.split(">")[2]
		mobile_ua = account.split(">")[3]
		try:
			proxy = account.split(">")[4]
		except IndexError:
			proxy = "127.0.0.1:8080"
	except IndexError:
		safe_print("Failed to parse: ") + account
	mobile_headers = c.headers
	mobile_headers["User-Agent"] = mobile_ua
	desktop_headers = c.headers
	desktop_headers["User-Agent"] = desktop_ua
	data = {"i13":"0", "type":"11", "LoginOptions":"3", "lrt":"", "ps":"2", "psRNGCDefaultType":"", "psRNGCEntropy":"", "psRNGCSLK":"", "canary":"", "ctx":"", "NewUser":"1", "FoundMSAs":"", "fspost":"0", "i21":"0", "i2":"1", "i17":"0", "i18":"__ConvergedLoginPaginatedStrings%7C1%2C__ConvergedLogin_PCore%7C1%2C", "i19":"2" + str(randint(0, 5000))}
	proxies = {"http":proxy, "https":proxy}
	data["login"] = email
	data["loginfmt"] = email
	data["passwd"] = password

	#wait random amount before logging in
	if not retry:
		wait_secs = random.randint(c.new_thread_low,c.new_thread_high)
		safe_print("sleeping for " + str(wait_secs) + " seconds")
		time.sleep(wait_secs)

	#login mobile and desktop
	try:
		if proxy != "127.0.0.1:8080":
			res = requests.get(c.hostURL, headers=desktop_headers, proxies=proxies, verify=False)
		else:
			res = requests.get(c.hostURL, headers=desktop_headers, verify=False)
		desktop_headers["Referer"] = res.url
		index = res.text.index("WindowsLiveId")
		cutText = res.text[index + 16:]
		loginURL = cutText[:cutText.index("\"")]
		loginURL = bytes(loginURL).encode("utf-8").decode("unicode_escape")
		desktop_headers["Host"] = c.loginHost
		if proxy != "127.0.0.1:8080":
			res = requests.get(loginURL, headers=desktop_headers, proxies=proxies, verify=False)
		else:
			res = requests.get(loginURL, headers=desktop_headers, verify=False)
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
			res = requests.post(postURL, cookies=cookies, data=data, headers=desktop_headers, proxies=proxies, verify=False)
		else:
			res = requests.post(postURL, cookies=cookies, data=data, headers=desktop_headers, verify=False)
		desktop_headers["Referer"] = res.url
		form = BS(res.content, "html.parser").findAll("form")[0]
		params = dict()
		for field in form:
			params[field["name"]] = field["value"]
		desktop_headers["Host"] = c.host
		if proxy != "127.0.0.1:8080":
			res = requests.post(form.get("action"), cookies=cookies, data=params, headers=desktop_headers, proxies=proxies, verify=False)
		else:
			res = requests.post(form.get("action"), cookies=cookies, data=params, headers=desktop_headers, verify=False)
		desktop_headers["Referer"] = res.url
		cookies = res.cookies
		safe_print(email + ": logging in")
		finder = re.compile("'(\d+)'")
		if proxy != "127.0.0.1:8080":
			page = requests.get("https://www.bing.com/rewardsapp/reportActivity", cookies=cookies, headers=desktop_headers, proxies=proxies, verify=False)
		else:
			page = requests.get("https://www.bing.com/rewardsapp/reportActivity", cookies=cookies, headers=desktop_headers, verify=False)
		oldPoints = int(finder.search(page.content).group(1))
		safe_print(email + ": current points: " + str(oldPoints))

		#parse rewards
		mobile_headers["User-Agent"] = mobile_ua
		if proxy != "127.0.0.1:8080":
			page = requests.get("https://www.bing.com/rewardsapp/flyoutpage/?style=v2", cookies=cookies, headers=mobile_headers, verify=False, proxies=proxies)
		else:
			page = requests.get("https://www.bing.com/rewardsapp/flyoutpage/?style=v2", cookies=cookies, headers=mobile_headers, verify=False)
		soup = BS(page.content,"html.parser")
		rewards = soup.findAll("ul",{"class" : "item"})
		extra_offers = []
		forbiddenwords = re.compile('quiz|redeem|goal|challenge|activate|earn more points|edge|wallpaper', re.IGNORECASE)
		goodwords = re.compile('claim|bonus points|free|', re.IGNORECASE)
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
					if ((int(progress.search(reward_text).group(1)) == 0 and int(progress.search(reward_text).group(2)) == 10) or (goodwords.search(reward_text)) and int(progress.search(reward_text).group(1)) != int(progress.search(reward_text).group(2))):
						extra_offers.append(reward.find("li",{"class" : "main"}).find("a")["href"])
						print reward.find("li",{"class" : "main"}).find("a").text.encode("utf-8")
		try:
			test = int(desktop_left + mobile_left)
		except UnboundLocalError:
			safe_print(email + ": failed to login")
			return
		if proxy != "127.0.0.1:8080":
			page = requests.get("https://www.bing.com/rewardsapp/bepflyoutpage?style=modular", cookies=cookies, headers=mobile_headers, verify=False, proxies=proxies)
		else:
			page = requests.get("https://www.bing.com/rewardsapp/bepflyoutpage?style=modular", cookies=cookies, headers=mobile_headers, verify=False)
		soup = BS(page.content,"html.parser")
		rewards = soup.find("div",{"id" : "offers"}).findAll("a",{"class" : "cardItem"})
		for reward in rewards:
			reward_text = reward.find("div",{"class" : "title"}).text.encode("utf-8")
			if "bonus points" in reward_text:
				extra_offers.append(reward["href"])
				print reward_text

		#searches throughout the period of time 5.5-8.3 hours default
		querytime = random.randint(c.querytime_low,c.querytime_high)
		querysalt = random.randint(c.querysalt_low,c.querysalt_high)
		querytotal = int(desktop_left + mobile_left + querysalt + len(extra_offers))
		offer_priority = False
		if (querytotal - (desktop_left + mobile_left + len(extra_offes))):
			offer_priority = True
		querytimes = random.sample(range(1,int(querytime)),querytotal - 1)
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
					page = requests.get("https://www.bing.com/rewardsapp/reportActivity", cookies=cookies, headers=desktop_headers, proxies=proxies, verify=False)
				else:
					page = requests.get("https://www.bing.com/rewardsapp/reportActivity", cookies=cookies, headers=desktop_headers, verify=False)
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
						requests.get("https://bing.com" + offer, cookies=cookies, headers=desktop_headers, proxies=proxies, verify=False)
					else:
						requests.get("https://bing.com" + offer, cookies=cookies, headers=desktop_headers, verify=False)
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
				hpm = False
				referer = False
				forms = c.forms
				if "Firefox" in desktop_ua or "Firefox" in mobile_ua:
					forms.append(c.ff_forms)
				elif "Chrome" in desktop_ua or "Chrome" in mobile_ua and "Edge" not in desktop_ua:
					forms.append(c.ch_forms)
				elif "Edge" in desktop_ua and lasttype != "mobile":
					forms.append(c.ed_forms)
				form = random.choice(forms)
				add_query = False
				if "QBRE&sp=" in form:
					form = form + str(random.randint(1, 5))
				if "pq=" in form:
					add_query = True
				if num < 4:
					gen = wiki.queryGenerator(1)
					query = str(gen.generateQueries(1,set()).pop()).replace(" ","+")
					url = c.searchURL + query + form
					if add_query:
						url = url + query
					referer = True
				elif num < 9:
					gen = gt.queryGenerator(1)
					query = str(gen.generateQueries(1,set()).pop()).replace(" ","+")
					url = c.searchURL + query + form
					if add_query:
						url = url + query
					referer = True
				else:
					desktop_headers["User-Agent"] = desktop_ua
					if proxy != "127.0.0.1:8080":
						page = requests.get("https://bing.com/hpm?", headers=desktop_headers, proxies=proxies, verify=False)
					else:
						page = requests.get("https://bing.com/hpm?", headers=desktop_headers, verify=False)
					hrefs = []
					soup = BS(page.content,"html.parser")
					for a in soup.findAll("a"):
						if a["href"] != "javascript:void(0)" and "QUIZ" not in a["href"]:
							hrefs.append(a["href"])
					url = "https://bing.com" + str(random.choice(hrefs))
					query = "popular now"
					hpm = True
				if "desktop" in lasttype:
					desktop_searches += 1
					desktop_headers["User-Agent"] = desktop_ua
					if hpm:
						desktop_headers["Referer"] = "https://bing.com"
						hpm = False
					if referer:
						desktop_headers["Referer"] = "https://bing.com"
					if proxy != "127.0.0.1:8080":
						requests.get(url, cookies=cookies, headers=desktop_headers, proxies=proxies, verify=False)
					else:
						requests.get(url, cookies=cookies, headers=desktop_headers, verify=False)
				if "mobile" in lasttype:
					mobile_searches += 1
					mobile_headers["User-Agent"] = mobile_ua
					if hpm:
						desktop_headers["Referer"] = "https://bing.com"
						hpm = False
					if referer:
						mobile_headers["Referer"] = "https://bing.com"
					if proxy != "127.0.0.1:8080":
						requests.get(url, cookies=cookies, headers=mobile_headers, proxies=proxies, verify=False)
					else:
						requests.get(url, cookies=cookies, headers=mobile_headers, verify=False)
				query = query.replace("+"," ")
				safe_print(email + ": " + lasttype + " search: " + query)
				printed = False
	except requests.exceptions.ProxyError:
		safe_print("Caught ProxyError on: " + email + " retrying...")
		search_account(account,retry=True)
	except IndexError:
		safe_print("Caught failed request on: " + email + " retrying...")
		search_account(account,retry=True)
	except Exception, e:
		e.traceback = traceback.format_exc()
		safe_print(e.traceback)
		return
if __name__ == "__main__":
	input = os.path.join(os.path.dirname(os.path.realpath(__file__)), "accounts.txt")
	if not os.path.isfile(input):
		input = os.path.join(os.getcwd(), "accounts.txt")
	if os.path.isfile(input):
		safe_print("Found accounts.txt")
		input_file = open(input,"r")
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
	redeem_ready = os.path.join(os.path.dirname(os.path.realpath(__file__)), "redeem_ready.txt")
	if not os.path.isfile(redeem_ready):
		redeem_ready = os.path.join(os.getcwd(), "redeem_ready.txt")
	if os.path.isfile(redeem_ready):
		output_file.write("---REDEEM READY---\n")
		redeem_ready_text = open(redeem_ready,"r")
		for line in redeem_ready_text:
			output_file.write(line + "\n")
	not_ready = os.path.join(os.path.dirname(os.path.realpath(__file__)), "not_ready.txt")
	if not os.path.isfile(not_ready):
		not_ready = os.path.join(os.getcwd(), "not_ready.txt")
	if os.path.isfile(not_ready):
		output_file.write("---NOT READY---\n")
		not_ready_text = open(not_ready,"r")
		for line in not_ready_text:
			output_file.write(line + "\n")
	output_file.close()
	try:
		redeem_ready_text.close()
		not_ready_text.close()
	except NameError:
		pass
	try:
		os.remove("not_ready.txt")
		os.remove("redeem_ready.txt")
	except OSError:
		pass