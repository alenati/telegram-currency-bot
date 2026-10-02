from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import Config
import psycopg2

buttons = [
            [KeyboardButton(text="🇺🇸 USD Доллар США")],
            [KeyboardButton(text="🇪🇺 EUR Евро")],
            [KeyboardButton(text="🇨🇳 CNY Китайский юань")],
            [KeyboardButton(text="🇬🇧 GBP Фунт стерлингов")],
            [KeyboardButton(text="🇨🇭 CHF Швейцарский франк")],
            [KeyboardButton(text="🇯🇵 JPY Японская иена")],
            [KeyboardButton(text="🇰🇿 KZT Казахский тенге")],
            [KeyboardButton(text="🇧🇾 BYN Белорусский рубль")],
            [KeyboardButton(text="🇺🇦 UAH Украинская гривна")],
            [KeyboardButton(text="🇦🇲 AMD Армянский драм")],
            [KeyboardButton(text="🇬🇪 GEL Грузинский лари")],
            [KeyboardButton(text="🇺🇿 UZS Узбекский сум")],
            [KeyboardButton(text="🇦🇿 AZN Азербайджанский манат")],
            [KeyboardButton(text="🇰🇬 KGS Киргизский сом")],
            [KeyboardButton(text="🇹🇯 TJS Таджиксикй сомони")],
            [KeyboardButton(text="🇹🇷 TRY Турецкая лира")],
            [KeyboardButton(text="🇦🇪 AED Дирхам ОАЭ")],
            [KeyboardButton(text="🇹🇭 THB Тайский бат")],
            [KeyboardButton(text="🇮🇳 INR Индийская рупия")],
            [KeyboardButton(text="🇭🇰 HKD Гонконгский доллар")],
            [KeyboardButton(text="🇸🇬 SGD Сингапурский доллар")],
            [KeyboardButton(text="🇨🇦 CAD Канадский доллар")],
            [KeyboardButton(text="🇦🇺 AUD Австралийский доллар")],
            [KeyboardButton(text="🇳🇿 NZD Новозеландский доллар")],
            [KeyboardButton(text="🇿🇦 ZAR Южноафриканский рэнд")],
            [KeyboardButton(text="🇩🇰 DKK Датская крона")],
            [KeyboardButton(text="🇳🇴 NOK Норвежская крона")],
            [KeyboardButton(text="🇸🇪 SEK Шведская крона")],
            [KeyboardButton(text="🇷🇴 RON Румынский лей")],
            [KeyboardButton(text="🇧🇬 BGN Болгарский лев")],
            [KeyboardButton(text="🇭🇺 HUF Венгерский форинт")],
            [KeyboardButton(text="🇨🇿 CZK Чешская крона")],
            [KeyboardButton(text="🇵🇱 PLN Польский злотый")],
            [KeyboardButton(text="🇷🇸 RSD Сербский динар")],
            [KeyboardButton(text="🇮🇷 IRR Иранский риал")],
            [KeyboardButton(text="🇪🇹 ETB Эфиопский быр")],
            [KeyboardButton(text="🇧🇩 BDT Бангладешская така")],
            [KeyboardButton(text="🇲🇲 MMK Мьянманский кьят")],
            [KeyboardButton(text="🇩🇿 DZD Алжирский динар")],
            [KeyboardButton(text="🇧🇭 BHD Бахрейнский динар")],
            [KeyboardButton(text="🇧🇴 BOB Боливийский боливиано")],
            [KeyboardButton(text="🇧🇷 BRL Бразильсикий реал")],
            [KeyboardButton(text="🇰🇷 KRW Южнокорейская вона")],
            [KeyboardButton(text="🇻🇳 VND Вьетнамский донг")],
            [KeyboardButton(text="🇪🇬 EGP Египетский фунт")],
            [KeyboardButton(text="🇶🇦 QAR Катарский риал")],
            [KeyboardButton(text="🇨🇺 CUP Кубинское песо")],
            [KeyboardButton(text="🇲🇩 MDL Молдавский лей")],
            [KeyboardButton(text="🇳🇬 NGN Нигерийская найра")],
            [KeyboardButton(text="🇹🇲 TMT Туркменский манат")],
            [KeyboardButton(text="🇴🇲 OMR Оманский риал")],
            [KeyboardButton(text="🇮🇩 IDR Индонезийская рупия")],
            [KeyboardButton(text="🇸🇦 SAR Саудовский риял")],
            [KeyboardButton(text="🇺🇳 XDR СДР (специальные права заимствования)")]



        ]


def get_currencies():
    connection = psycopg2.connect(
                host = Config.PG_HOST,
                user = Config.PG_USER,
                password = Config.PG_PASSWORD,
                database = Config.PG_DB_NAME
            )
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                select currency_code, country_code from currency 
            """)
            return cursor.fetchall()
    finally:
        connection.close()


def country_code_to_flag(code: str) -> str:
    return "".join(
        chr(ord(char) + 127397)
        for char in code.upper()
    )

def create_currency_keyboard(currencies):
    buttons = []
    row = []
    for name, country_code in currencies:
        flag = country_code_to_flag(country_code)

        row.append(
            KeyboardButton(
                            text=f"{name} {flag}"
                        )
        )
        if len(row) == 3:
            buttons.append(row)
            row = []

        buttons.append([
            
        ])
    if row:
        buttons.append(row)

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
