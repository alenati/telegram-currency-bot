from urllib.request import urlopen #for opening urls
from urllib.error import HTTPError #for HTTP errors processing
from urllib.error import URLError #for URL errors processing
from bs4 import BeautifulSoup

try:
    html = urlopen("https://cbr.ru/currency_base/daily/")
except HTTPError as e:
    print(e)
except URLError as e:
    print(e)
else:
    bsObj = BeautifulSoup(html.read(), 'html.parser')
    #print(bsObj.tbody)
    meow = bsObj.find("td",string="EUR")
    if meow:
        parent = meow.find_parent('tr')
        print(parent)