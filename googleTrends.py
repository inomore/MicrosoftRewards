import urllib2
import random
import common
from xml.etree import ElementTree
from urllib import quote_plus
import time

TRENDSURL = common.trendsURLs[common.selectedLocale]
SUGGESTURL = "http://suggestqueries.google.com/complete/search?output=toolbar&hl=en&q="
TRENDS_XML = None
LAST_TREND_CHECK = 0
MAX_QUERY_LEN = 50

class queryGenerator:

    def __init__(self, br):
        self.br = br
        self.allQueries = self.__pullAll()
        self.unusedQueries = self.allQueries.copy()

    def __pullAll(self):
        result = self.__trendQueries()
        tmp = result.copy()
        for term in tmp:
            suggestSet = self.__suggestQueriesSingle(term)
            result.update(suggestSet)
        return result.copy()
    
    def __readXML(self,URL):
		if SUGGESTURL in URL:
			response = urllib2.urlopen(URL)
			try:
				tree = ElementTree.parse(response)
			except:
				return None
			return tree
		if LAST_TREND_CHECK = 0 or (int(time.time()) - LAST_TREND_CHECK > 1000):
			response = urllib2.urlopen(URL)
			LAST_TREND_CHECK = int(time.time())
			TRENDS_XML = response
		try:
			tree = ElementTree.parse(TRENDS_XML)
		except:
			return None
		return tree

    def __trendQueries(self):
        generated = set()
        tree = self.__readXML(TRENDSURL)
        if tree is None: raise TypeError("trend could not parse XML")

        for item in tree.iter("item"):
            title = item.find('title').text
            desc = item.find('description').text
            generated.add(title.strip().lower())
            if desc:
                subDesc = desc.split(',')
                subDesc = subDesc if len(subDesc) <= 10 else random.sample(subDesc, 10)
                for item in subDesc:
                    generated.add(item.strip().lower())
        return generated

    def __suggestQueriesSingle(self,term):
        suggestions = set()
        formatted = quote_plus(term.encode('utf-8')) #term.replace(" ","+").encode('ascii', 'ignore')
        URL = SUGGESTURL+formatted
        tree = self.__readXML(URL)
        if tree is not None: 
            for item in tree.iter("suggestion"):
                suggestions.add(item.get('data').lower())
        return suggestions

    def generateQueries(self, queriesToGenerate, history, maxQueryLen = MAX_QUERY_LEN):
        """
        parses Google Trends top trends and generates a set of unique queries. If the number
        of queries is not >= the requested number, a google suggestion will be called on all
        terms in the query set.  These suggestions will be added to the set as well.
        param queriesToGenerate the number of queries to return
        param history a set of previous searches
        """
        if queriesToGenerate <= 0: raise ValueError("queriesToGenerate should be more than 0, but it is %d" % queriesToGenerate)
        if history is None or not isinstance(history, set): raise ValueError("history is not set or not an instance of set")

        removedHistory = self.unusedQueries.intersection(history)
        self.unusedQueries -= history
        if queriesToGenerate > len(self.unusedQueries):
            self.unusedQueries = self.__pullAll()
            if queriesToGenerate > len(self.unusedQueries): raise ValueError("to many queries requested")

        final = random.sample(self.unusedQueries, queriesToGenerate)
        finalSet = set(final)
        self.unusedQueries -= finalSet
        self.unusedQueries.update(removedHistory)
        return finalSet.copy()