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

cmd_exists = lambda x: any(os.access(os.path.join(path, x), os.X_OK) for path in os.environ["PATH"].split(os.pathsep))
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def safe_print(content):
    print "{0}\n".format(content),

def report_account(account):
	#initialize
	if account is None:
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
	data = {"i13":"0", "type":"11", "LoginOptions":"3", "lrt":"", "ps":"2", "psRNGCDefaultType":"", "psRNGCEntropy":"", "psRNGCSLK":"", "canary":"", "ctx":"", "PPFT":"", "PPSX":"", "NewUser":"1", "FoundMSAs":"", "fspost":"0", "i21":"0", "CookieDisclosure":"0", "i2":"1", "i17":"0", "i18":"__ConvergedLoginPaginatedStrings%7C1%2C__ConvergedLogin_PCore%7C1%2C", "i19":str(randint(14000, 38000))}
	proxies = {"http":proxy, "https":proxy}
	data["login"] = email
	data["loginfmt"] = email
	data["passwd"] = password

	wait_secs = random.randint(0,60)
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
		if oldPoints >= c.redeem_ready:
			redeem_ready = os.path.join(os.path.dirname(os.path.realpath(__file__)), "redeem_ready.txt")
			redeem_ready_text = open(redeem_ready,"a+")
			redeem_ready_text.write(str({email : {"total" : oldPoints}}) + "\n")
			redeem_ready_text.close()
		else:
			not_ready = os.path.join(os.path.dirname(os.path.realpath(__file__)), "not_ready.txt")
			not_ready_text = open(not_ready,"a+")
			not_ready_text.write(str({email : {"total" : oldPoints}}) + "\n")
			not_ready_text.close()
	except Exception, e:
		safe_print(traceback.format_exc())
		print "on " + email
		return

def search_account(account, retry=False, retries=0):
	#initialize
	if account is None:
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
	data = {"i13":"0", "type":"11", "LoginOptions":"3", "lrt":"", "ps":"2", "psRNGCDefaultType":"", "psRNGCEntropy":"", "psRNGCSLK":"", "canary":"", "ctx":"", "PPFT":"", "PPSX":"", "NewUser":"1", "FoundMSAs":"", "fspost":"0", "i21":"0", "CookieDisclosure":"0", "i2":"1", "i17":"0", "i18":"__ConvergedLoginPaginatedStrings%7C1%2C__ConvergedLogin_PCore%7C1%2C", "i19":str(randint(14000, 38000))}
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
		try:
			index = res.text.index("WindowsLiveId")
			cutText = res.text[index + 16:]
			loginURL = cutText[:cutText.index("\"")]
			loginURL = bytes(loginURL).encode("utf-8").decode("unicode_escape")
		except ValueError:
			loginURL = "https://login.live.com"
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
		if "post" not in postURL:
			safe_print("Failed to parse login page!")
			safe_print("Most likely slow connection")
			raise IndexError("Parse failure")
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
		if "NAP" not in res.content:
			safe_print("Failed to parse login page!")
			safe_print("Most likely slow connection")
			raise IndexError("Parse failure")
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
		try:
			oldPoints = int(finder.search(page.content).group(1))
		except AttributeError:
			safe_print(email + ": failed to login")
			raise IndexError("Failed to login")
		safe_print(email + ": current points: " + str(oldPoints))

		#parse rewards
		mobile_headers["User-Agent"] = c.mobile_ua
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
		bep_progress = re.compile("(\d+)/(\d+)")
		for reward in rewards:
			reward_text = reward.text.encode("utf-8")
			if not forbiddenwords.search(reward_text):
				if "PC search" in reward_text:
					pass
				elif "Mobile search" in reward_text:
					pass
				elif "Daily search" in reward_text:
					pass
				else:
					try:
						if ((int(progress.search(reward_text).group(1)) == 0 and int(progress.search(reward_text).group(2)) == 10) or (goodwords.search(reward_text)) and int(progress.search(reward_text).group(1)) != int(progress.search(reward_text).group(2))):
							extra_offers.append(str(reward.find("li",{"class" : "main"}).find("a")["href"]))
							print reward.find("li",{"class" : "main"}).find("a").text.encode("utf-8")
					except AttributeError:
						pass
		if proxy != "127.0.0.1:8080":
			page = requests.get("https://www.bing.com/rewardsapp/bepflyoutpage?style=modular", cookies=cookies, headers=mobile_headers, verify=False, proxies=proxies)
		else:
			page = requests.get("https://www.bing.com/rewardsapp/bepflyoutpage?style=modular", cookies=cookies, headers=mobile_headers, verify=False)
		soup = BS(page.content,"html.parser")
		#main flyout isnt refreshing
		details = soup.findAll("span",{"class" : "details"})
		mobile_searches = 0
		desktop_searches = 0
		desktop_left = int(bep_progress.search(details[1].text.encode("utf-8")).group(2)) / c.searchValue
		try:
			mobile_left = int(bep_progress.search(details[2].text.encode("utf-8")).group(2)) / c.searchValue
		except IndexError:
			mobile_left = 0
		rewards = soup.find("div",{"id" : "offers"}).findAll("a",{"class" : "cardItem"})
		for reward in rewards:
			reward_text = reward.find("div",{"class" : "title"}).text.encode("utf-8")
			if "bonus points" in reward_text or "welcome" in reward_text:
				extra_offers.append(reward["href"])
				print reward_text

		try:
			test = int(desktop_left + mobile_left)
			if test > 0:
				safe_print(email + ": desktop left: " + str(desktop_left))
				safe_print(email + ": mobile left: " + str(mobile_left))
			else:
				safe_print(email + ": searches done")
				return
		except UnboundLocalError:
			safe_print(email + ": failed to login/grab flyout")
			raise IndexError
		
		desktop_headers["Accept-Language"] = c.acceptLang[c.selectedLocale]
		for url in extra_offers:
			try:
				desktop_headers["User-Agent"] = desktop_ua
				print "performed extra offer!"
				if "https://" not in url:
					url = "https://bing.com" + url
				if proxy != "127.0.0.1:8080":
					requests.get(url, cookies=cookies, headers=desktop_headers, proxies=proxies, verify=False)
				else:
					requests.get(url, cookies=cookies, headers=desktop_headers, verify=False)
				time.sleep(random.randint(3,15))
			except Exception,e:
				pass

		#searches throughout the period of time 5.5-8.3 hours default
		querytime = random.randint(c.querytime_low,c.querytime_high)
		querysalt = 0
		while True:
			try:
				if desktop_left > 5 or mobile_searches > 5: 
					querysalt = random.randint(c.querysalt_low,c.querysalt_high)
				if desktop_left == 0:
					querytimes = random.sample(range(1,int(querytime)),int(querysalt + mobile_left) - 1)
					lasttype = "mobile"
				elif mobile_left == 0:
					querytimes = random.sample(range(1,int(querytime)),int(querysalt + desktop_left) - 1)
					lasttype = "desktop"
				else:
					querytimes = random.sample(range(1,int(querytime)),int(querysalt + desktop_left + mobile_left) - 1)
					lasttype = random.choice(["desktop","mobile"])
			except ValueError:
				pass
			else:
				break
		printed = False
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
				if oldPoints >= c.redeem_ready:
					redeem_ready = os.path.join(os.path.dirname(os.path.realpath(__file__)), "redeem_ready.txt")
					redeem_ready_text = open(redeem_ready,"a+")
					redeem_ready_text.write(str({email : {"earned" : newPoints - oldPoints, "total" : newPoints}}) + "\n")
					redeem_ready_text.close()
				else:
					not_ready = os.path.join(os.path.dirname(os.path.realpath(__file__)), "not_ready.txt")
					not_ready_text = open(not_ready,"a+")
					not_ready_text.write(str({email : {"earned" : newPoints - oldPoints, "total" : newPoints}}) + "\n")
					not_ready_text.close()
				return
			if i in querytimes:
				if mobile_searches >= mobile_left and desktop_searches >= desktop_left:
					pass
				elif desktop_searches >= desktop_left and mobile_searches <= mobile_left:
					lasttype = "mobile"
				elif desktop_searches <= desktop_left and mobile_searches >= mobile_left:
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
					try:
						gen = gt.queryGenerator(1)
					except Exception, e:
						gen = wiki.queryGenerator(1)
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
					query = query.replace("+"," ")
					safe_print(email + ": " + str(desktop_searches) + "/" + str(desktop_left) + ": " + lasttype + " search: " + query)
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
					safe_print(email + ": " + str(mobile_searches) + "/" + str(mobile_left) + ": " + lasttype + " search: " + query)
				printed = False
	except requests.exceptions.ProxyError:
		if retries < 5:
			safe_print("Caught ProxyError on: " + email + " retrying...")
			retries += 1
			search_account(account,retry=True, retries=retries)
		else:
			safe_print("Caught ProxyError on: " + email + " exiting...")
	except IndexError:
		if retries < 5:
			safe_print("Caught failed request on: " + email + " retrying...")
			retries += 1
			search_account(account,retry=True, retries=retries)
		else:
			safe_print("Caught failed request on: " + email + " exiting...")
	except Exception, e:
		e.traceback = traceback.format_exc()
		safe_print(e.traceback)
		return
if __name__ == "__main__":
	if cmd_exists("git.exe") and "--updated" not in sys.argv:
		print "Checking for updates..."
		local = os.popen("git rev-parse HEAD").read().strip()
		remote = requests.get("https://api.github.com/repos/zengfu94/MicrosoftRewards/commits/master").json()["sha"]
		if remote != local:
			print "Saving common.py values..."
			selectedLocale = c.selectedLocale
			redeem_ready = c.redeem_ready
			new_thread_low = c.new_thread_low
			new_thread_high = c.new_thread_high
			querytime_low = c.querytime_low
			querytime_high = c.querytime_high
			querysalt_low = c.querysalt_low
			querysalt_high = c.querysalt_high
			print "Peforming update..."
			os.popen("git reset --hard")
			os.popen("git pull").read()
			print "Configuring common.py"
			cmd = r'sed -i "s/^\(selectedLocale =\).*/\1 \"' + selectedLocale + '\"/" common.py'
			os.popen(cmd)
			cmd = r'sed -i "s/^\(redeem_ready =\).*/\1 ' + str(redeem_ready) + '/" common.py'
			os.popen(cmd)
			cmd = r'sed -i "s/^\(new_thread_high =\).*/\1 ' + str(new_thread_high) + '/" common.py'
			os.popen(cmd)
			cmd = r'sed -i "s/^\(new_thread_low =\).*/\1 ' + str(new_thread_low) + '/" common.py'
			os.popen(cmd)
			cmd = r'sed -i "s/^\(querytime_high =\).*/\1 ' + str(querytime_high) + '/" common.py'
			os.popen(cmd)
			cmd = r'sed -i "s/^\(querytime_low =\).*/\1 ' + str(querytime_low) + '/" common.py'
			os.popen(cmd)
			cmd = r'sed -i "s/^\(querysalt_high =\).*/\1 ' + str(querysalt_high) + '/" common.py'
			os.popen(cmd)
			cmd = r'sed -i "s/^\(querysalt_low =\).*/\1 ' + str(querysalt_low) + '/" common.py'
			os.popen(cmd)
			os.popen("del sed*")
			try:
				sys.argv[1]
				for arg in sys.argv:
					args += " " + arg
			except IndexError:
				args = ""
			args += " --updated"
			os.system("start cmd /K bing.py" + args)
			print "You can close this window now."
			os._exit(0)
	else:
		print "Git not found or updates disabled!"
	input = os.path.join(os.path.dirname(os.path.realpath(__file__)), "accounts.txt")
	if not os.path.isfile(input):
		input = os.path.join(os.getcwd(), "accounts.txt")
	if os.path.isfile(input):
		input_file = open(input,"r")
	else:
		safe_print("Did you remember to rename accounts.txt.dist to accounts.txt?")
		safe_print("Could not find accounts.txt")
	accounts = []
	for line in input_file:
		accounts.append(line)
	input_file.close()
	try:
		if sys.argv[1] == "--report":
			do_report = True
		else:
			do_report = False
	except IndexError:
		do_report = False
	if do_report:
		try:
			pool = Pool(processes=len(accounts))
			pool.map(report_account, accounts)
		except OSError:
			pass
	else:
		try:
			pool = Pool(processes=len(accounts))
			pool.map(search_account, accounts)
		except OSError:
			pass
	output = os.path.join(os.path.dirname(os.path.realpath(__file__)), "report.txt")
	output_file = open(output,"w+")
	redeem_ready = os.path.join(os.path.dirname(os.path.realpath(__file__)), "redeem_ready.txt")
	if not os.path.isfile(redeem_ready):
		redeem_ready = os.path.join(os.getcwd(), "redeem_ready.txt")
	if os.path.isfile(redeem_ready):
		output_file.write("---REDEEM READY---\n")
		redeem_ready_text = open(redeem_ready,"r")
		for line in redeem_ready_text:
			line = line.replace("{","")
			line = line.replace("}","")
			if "\n" not in line:
				output_file.write(line + "\n")
			else:
				output_file.write(line)
		redeem_ready_text.close()
		os.remove(redeem_ready)
	not_ready = os.path.join(os.path.dirname(os.path.realpath(__file__)), "not_ready.txt")
	if not os.path.isfile(not_ready):
		not_ready = os.path.join(os.getcwd(), "not_ready.txt")
	if os.path.isfile(not_ready):
		output_file.write("---NOT READY---\n")
		not_ready_text = open(not_ready,"r")
		for line in not_ready_text:
			line = line.replace("{","")
			line = line.replace("}","")
			if "\n" not in line:
				output_file.write(line + "\n")
			else:
				output_file.write(line)
		not_ready_text.close()
		os.remove(not_ready)
	output_file.close()
