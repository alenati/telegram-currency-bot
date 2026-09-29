import requests
import xml.etree.ElementTree as ET
import psycopg2
from config import Config
from datetime import datetime, date
import calendar




def get_all_month_data(year, month):
    days_in_month = calendar.monthrange(year, month)[1]

    connection = psycopg2.connect(
            host = Config.PG_HOST,
            user = Config.PG_USER,
            password = Config.PG_PASSWORD,
            database = Config.PG_DB_NAME
        )

    for day in range(1, days_in_month+1):
        d = date(year, month,day)
        api_date = d.strftime("%d/%m/%Y")
        link = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={api_date}"

        resp = requests.get(link)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        date_value = root.attrib.get("Date")
        db_date = datetime.strptime(date_value, "%d.%m.%Y").date().isoformat()


        with connection.cursor() as cursor:

            for curr in root.findall("Valute"):
                currency_num = curr.findtext("NumCode")
                rate = curr.findtext("VunitRate")
                rate = float(rate.replace(",", "."))
                unit = curr.findtext("Nominal")
                insert_q = """ 
                    insert into currency_cost (currency_num,unit,rate,date)
                    values (%s,%s,%s,%s) 
                    on conflict do nothing
                    """
                new_line =[currency_num, unit, rate, db_date] 
                cursor.execute(insert_q,new_line)
                connection.commit()







# default = today
def get_one_day_data(d: date | None = None):

    if d is None:
        d = date.today()
    

    api_date = d.strftime("%d/%m/%Y")
    link = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={api_date}"

    try: 
        connection = psycopg2.connect(
                host = Config.PG_HOST,
                user = Config.PG_USER,
                password = Config.PG_PASSWORD,
                database = Config.PG_DB_NAME
            )
        resp = requests.get(link)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    
        date_value = root.attrib.get("Date")
        db_date = datetime.strptime(date_value, "%d.%m.%Y").date().isoformat()
    
    
        with connection.cursor() as cursor:
    
            for curr in root.findall("Valute"):
                currency_num = curr.findtext("NumCode")
                rate = curr.findtext("VunitRate")
                rate = float(rate.replace(",", "."))
                unit = curr.findtext("Nominal")
                insert_q = """ 
                    insert into currency_cost (currency_num,unit,rate,date)
                    values (%s,%s,%s,%s) 
                    on conflict do nothing
                    """
                new_line =[currency_num, unit, rate, db_date] 
                cursor.execute(insert_q,new_line)
        connection.commit()
    except Exception as ex:
      print("Error: ", ex)
    finally:
        if connection:
            connection.close()
            print("Connection Closed") 
    
    


    




#get_all_month_data(2026, 5)
#get_one_day_data(date(2020, 3,13))