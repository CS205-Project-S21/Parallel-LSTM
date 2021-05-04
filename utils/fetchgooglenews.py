'''
The following codes are developed based on https://github.com/Iceloof/GoogleNews under MIT LICENSE.
I made the following modifications:
1. Supprt more articles on one page (with a numperpage argument)
2. Remove unnecessary codes (remove get_news related codes, remove old version API, remove images in the output)
3. Add a failflag argument to indicate if last page retreive failed
4. Add a duplicate argument to copy the article twice, for open and close price
5. Kick out the articles not in date range 

Minhuan Li, May 2021
'''

__all__=['GoogleNews']

### MODULES
import re
import urllib.request
import dateparser, copy
from bs4 import BeautifulSoup as Soup, ResultSet
from dateutil.parser import parse

import datetime
from dateutil.relativedelta import relativedelta

### METHODS

def lexical_date_parser(date_to_check):
    if date_to_check=='':
        return ('',None)
    datetime_tmp=None
    date_tmp=copy.copy(date_to_check)
    count=0
    while datetime_tmp==None and count <= (len(date_to_check)-3):
        datetime_tmp=dateparser.parse(date_tmp)
        if datetime_tmp==None:
            date_tmp=date_tmp[1:]
        count+=1

    if datetime_tmp==None:
        date_tmp=date_to_check
    else:
        datetime_tmp=datetime_tmp.replace(tzinfo=None)

    if date_tmp[0]==' ':
        date_tmp=date_tmp[1:]
    return date_tmp,datetime_tmp


def define_date(date):
    months = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
    try:
        if ' ago' in date.lower():
            q = int(date.split()[-3])
            if 'hour' in date.lower():
                return datetime.datetime.now() + relativedelta(hours=-q)
            elif 'day' in date.lower():
                return datetime.datetime.now() + relativedelta(days=-q)
            elif 'week' in date.lower():
                return datetime.datetime.now() + relativedelta(days=-7*q)
            elif 'month' in date.lower():
                return datetime.datetime.now() + relativedelta(months=-q)
        else:
            for month in months.keys():
                if month.lower()+' ' in date.lower():
                    date_list = date.replace(',','').split()[-3:]
                    return datetime.datetime(day=int(date_list[1]), month=months[month], year=int(date_list[2]), hour=4)
    except:
        return float('nan')


### CLASSEs

class GoogleNews:

    def __init__(self,lang="en",period="",start="",end="",encode="utf-8", numperpage=50, duplicate=False):
        self.__texts = []
        self.__links = []
        self.__results = []
        self.__totalcount = 0
        #self.user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}
        self.__lang = lang
        self.__period = period
        self.__start = start
        self.__end = end
        self.__encode = encode
        self.__numperpage = numperpage
        self.__failflag = 0
        self.__duplicate = duplicate

    def set_lang(self, lang):
        self.__lang = lang

    def set_period(self, period):
        self.__period = period

    def set_time_range(self, start, end):
        self.__start = start
        self.__end = end

    def set_encode(self, encode):
        self.__encode = encode

    def search(self, key):
        """
        Searches for a term in google.com in the news section and retrieves the first page into __results.
        Parameters:
        key = the search term
        """
        self.__key = "+".join(key.split(" "))
        if self.__encode != "":
            self.__key = urllib.request.quote(self.__key.encode(self.__encode))
        self.get_page()

    def build_response(self):
        self.req = urllib.request.Request(self.url.replace("search?","search?hl=en&gl=en&"), headers=self.headers)
        self.response = urllib.request.urlopen(self.req)
        self.page = self.response.read()
        self.content = Soup(self.page, "html.parser")
        stats = self.content.find_all("div", id="result-stats")
        if stats and isinstance(stats, ResultSet):
            stats = re.search(r'\d+', stats[0].text)
            self.__totalcount = int(stats.group())
        else:
            #TODO might want to add output for user to know no data was found
            return
        result = self.content.find_all("div", id="search")[0].find_all("g-card")
        return result

    def page_at(self, page=1):
        """
        Retrieves a specific page from google.com in the news sections into __results.

        Parameter:
        page = number of the page to be retrieved
        """
        results = []
        self.__failflag = 0
        try:
            if self.__start != "" and self.__end != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},cdr:1,cd_min:{},cd_max:{},sbd:1&tbm=nws&start={}&num={}".format(self.__key,self.__lang,self.__lang,self.__start,self.__end,(self.__numperpage * (page - 1)), self.__numperpage)
                #self.url = "https://www.google.com/search?q={}&lr=lang_{}&rlz=1C5CHFA_enUS916US916&tbs=lr:lang_1{},cdr:1,cd_min:{},cd_max:{}&tbm=nws&ei=2CuPYPmKNo2P9PwPvYSqsAs&start={}&sa=N&ved=0ahUKEwj51rj2iazwAhWNB50JHT2CCrY4ZBDy0wMIwQM&biw=1761&bih=946&dpr=2&num={}".format(self.__key,self.__lang,self.__lang,self.__start,self.__end,(self.__numperpage * (page - 1)), self.__numperpage)
            elif self.__period != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},qdr:{},,sbd:1&tbm=nws&start={}&num={}".format(self.__key,self.__lang,self.__lang,self.__period,(self.__numperpage * (page - 1)),self.__numperpage) 
            else:
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},sbd:1&tbm=nws&start={}&num={}".format(self.__key,self.__lang,self.__lang,(self.__numperpage * (page - 1)), self.__numperpage)     
        except AttributeError:
            raise AttributeError("You need to run a search() before using get_page().")
        try:
            result = self.build_response()
            for item in result:
                try:
                    tmp_text = item.find("div", {"role" : "heading"}).text.replace("\n","")
                except Exception:
                    tmp_text = ''
                try:
                    tmp_link = item.find("a").get("href")
                except Exception:
                    tmp_link = ''
                try:
                    tmp_media = item.findAll("g-img")[1].parent.text
                except Exception:
                    tmp_media = ''
                try:
                    tmp_date = item.find("div", {"role" : "heading"}).next_sibling.findNext('div').findNext('div').text
                    tmp_date,tmp_datetime=lexical_date_parser(tmp_date)
                except Exception:
                    tmp_date = ''
                    tmp_datetime=None
                try:
                    tmp_desc = item.find("div", {"role" : "heading"}).next_sibling.findNext('div').text.replace("\n","")
                except Exception:
                    tmp_desc = ''
                #try:
                #    tmp_img = item.findAll("g-img")[0].find("img").get("src")
                #except Exception:
                #    tmp_img = ''
                if define_date(tmp_date).date() > datetime.datetime.strptime(self.__end, "%m/%d/%Y").date():
                    continue
                if define_date(tmp_date).date() < datetime.datetime.strptime(self.__start, "%m/%d/%Y").date():
                    continue  

                self.__texts.append(tmp_text)
                self.__links.append(tmp_link)
                #results.append({'title': tmp_text, 'media': tmp_media,'date': tmp_date,'datetime':define_date(tmp_date),'desc': tmp_desc, 'link': tmp_link,'img': tmp_img})
                if self.__duplicate:
                    results.append({'title': tmp_text, 'source': tmp_media,'date': tmp_date,'datetime':define_date(tmp_date),'desc': tmp_desc, 'link': tmp_link})
                    results.append({'title': tmp_text, 'source': tmp_media,'date': tmp_date,'datetime':define_date(tmp_date)+datetime.timedelta(hours=8),'desc': tmp_desc, 'link': tmp_link})
                else:
                    results.append({'title': tmp_text, 'source': tmp_media,'date': tmp_date,'datetime':define_date(tmp_date),'desc': tmp_desc, 'link': tmp_link})
            self.response.close()
        except Exception as e_parser:
            print(e_parser)
            self.__failflag = 1
            pass
        return results

    def get_page(self, page=1):
        """
        Retrieves a specific page from google.com in the news sections into __results.

        Parameter:
        page = number of the page to be retrieved 
        """
        self.__failflag = 0
        try:
            if self.__start != "" and self.__end != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},cdr:1,cd_min:{},cd_max:{},sbd:1&tbm=nws&start={}&num={}".format(self.__key,self.__lang,self.__lang,self.__start,self.__end,(self.__numperpage * (page - 1)), self.__numperpage)
                #self.url = "https://www.google.com/search?q={}&lr=lang_{}&rlz=1C5CHFA_enUS916US916&tbs=lr:lang_1{},cdr:1,cd_min:{},cd_max:{}&tbm=nws&ei=2CuPYPmKNo2P9PwPvYSqsAs&start={}&sa=N&ved=0ahUKEwj51rj2iazwAhWNB50JHT2CCrY4ZBDy0wMIwQM&biw=1761&bih=946&dpr=2&num={}".format(self.__key,self.__lang,self.__lang,self.__start,self.__end,(self.__numperpage * (page - 1)), self.__numperpage)
            elif self.__period != "":
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},qdr:{},,sbd:1&tbm=nws&start={}&num={}".format(self.__key,self.__lang,self.__lang,self.__period,(self.__numperpage * (page - 1)),self.__numperpage) 
            else:
                self.url = "https://www.google.com/search?q={}&lr=lang_{}&biw=1920&bih=976&source=lnt&&tbs=lr:lang_1{},sbd:1&tbm=nws&start={}&num={}".format(self.__key,self.__lang,self.__lang,(self.__numperpage * (page - 1)), self.__numperpage) 
        except AttributeError:
            raise AttributeError("You need to run a search() before using get_page().")
        try:
            result = self.build_response()
            for item in result:
                try:
                    tmp_text = item.find("div", {"role" : "heading"}).text.replace("\n","")
                except Exception:
                    tmp_text = ''
                try:
                    tmp_link = item.find("a").get("href")
                except Exception:
                    tmp_link = ''
                try:
                    tmp_media = item.findAll("g-img")[1].parent.text
                except Exception:
                    tmp_media = ''
                try:
                    tmp_date = item.find("div", {"role" : "heading"}).next_sibling.findNext('div').findNext('div').text
                    tmp_date,tmp_datetime=lexical_date_parser(tmp_date)
                except Exception:
                    tmp_date = ''
                    tmp_datetime=None
                try:
                    tmp_desc = item.find("div", {"role" : "heading"}).next_sibling.findNext('div').text.replace("\n","")
                except Exception:
                    tmp_desc = ''
                #try:
                #    tmp_img = item.findAll("g-img")[0].find("img").get("src")
                #except Exception:
                #    tmp_img = ''
                if define_date(tmp_date).date() > datetime.datetime.strptime(self.__end, "%m/%d/%Y").date():
                    continue
                if define_date(tmp_date).date() < datetime.datetime.strptime(self.__start, "%m/%d/%Y").date():
                    continue                
                self.__texts.append(tmp_text)
                self.__links.append(tmp_link)
                #self.__results.append({'title': tmp_text, 'media': tmp_media,'date': tmp_date,'datetime':define_date(tmp_date),'desc': tmp_desc, 'link': tmp_link,'img': tmp_img})
                
                if self.__duplicate:
                    self.__results.append({'title': tmp_text, 'source': tmp_media,'date': tmp_date,'datetime':define_date(tmp_date),'desc': tmp_desc, 'link': tmp_link})
                    self.__results.append({'title': tmp_text, 'source': tmp_media,'date': tmp_date,'datetime':define_date(tmp_date)+datetime.timedelta(hours=8),'desc': tmp_desc, 'link': tmp_link})
                else:
                    self.__results.append({'title': tmp_text, 'source': tmp_media,'date': tmp_date,'datetime':define_date(tmp_date),'desc': tmp_desc, 'link': tmp_link})
            self.response.close()
        except Exception as e_parser:
            print(e_parser)
            self.__failflag = 1
            pass

    def total_count(self):
        return self.__totalcount

    def failflag(self):
        return self.__failflag

    def results(self,sort=False):
        """Returns the __results.
        New feature: include datatime and sort the articles in decreasing order"""
        results=self.__results
        if sort:
            try:
                results.sort(key = lambda x:x['datetime'],reverse=True)
            except Exception as e_sort:
                print(e_sort)
                results=self.__results
        return results

    def get_texts(self):
        """Returns only the __texts of the __results."""
        return self.__texts

    def get_links(self):
        """Returns only the __links of the __results."""
        return self.__links

    def clear(self):
        self.__texts = []
        self.__links = []
        self.__results = []
        self.__totalcount = 0