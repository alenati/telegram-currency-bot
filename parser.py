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

    date = bsObj.find("button", {"class":"datepicker-filter_button"}).get_text(strip=True)

    table = bsObj.tbody
    rows = table.find_all('tr')
    lines = []
    for row in rows:
        cells = [cell.get_text(strip=True) for cell in row.find_all(['th','td'])]
        new_cells = []
        new_cells.append(cells[0])
        new_cells.append(cells[2])
        new_cells.append(cells[4][:-5]+"."+cells[4][-4:])
        new_cells.append(date)
        if cells:
            lines.append(new_cells)

    lines = lines[1:]
