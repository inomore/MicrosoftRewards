host = "www.bing.com"
hostURL = "https://www.bing.com/"
searchURL = "https://www.bing.com/search?q="
loginHost = "login.live.com"
loginPostURL = "https://login.live.com/ppsecure/post.srf"
ua = "Mozilla/5.0 (X11; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0"
mobile_ua = "Mozilla/5.0 (Android 4.4; Mobile; rv:41.0) Gecko/41.0 Firefox/41.0"
accept = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
acceptLang = "en-US,en;q=0.5"
connection = "close"
headers = {"Host" : host, "User-Agent" : ua, "Accept" : accept, "Accept-Language" : acceptLang, "Connection" : connection}
mobileHeaders = {"Host" : host, "User-Agent" : mobile_ua, "Accept" : accept, "Accept-Language" : acceptLang, "Connection" : connection}
forms = ["&PC=U316&FORM=CHROMN", #when searching bing thru chrome omnibox
		"&qs=n&form=QBLH&sp=-1&pq=", #when searching through search box
		"&qs=SS&FORM=QBRE&sp=", #when you use search autocomplete on search box
		"&pc=MOZB&FORM=MOZMBA" ] #when searching bing thru firefox omnibox
redeem_ready = 5000
last_type_chance = 0.8
new_thread_low = 0
new_thread_high = 1800
querytime_low = 20000
querytime_high = 30000
querysalt_low = -5
querysalt_high = 20