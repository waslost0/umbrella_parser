import datetime
from UCParse import SessionUC, load_data_from_file
from bs4 import BeautifulSoup as BS
import re


def get_timing_to_new_promo_generated(promocodes_to_be_generated):
    return int(round((1075 / promocodes_to_be_generated), 2))


def get_promocodes_generated(session):
    response = se.session.get('https://uc.zone/')
    bs = BS(response.content, 'html.parser')
    promocodes_to_be_generated_text = bs.select_one(
        'div[class="gamePromocodeItem gamePromocode--extraInfo"]').ul.li.text
    result = re.findall(r'\d+', promocodes_to_be_generated_text)[0]
    promocodes_to_be_generated = int(result)
    return promocodes_to_be_generated


if __name__ == '__main__':
    username, password, rucaptcha_key = load_data_from_file()
    se = SessionUC(username=username, password=password, rucaptcha_key=rucaptcha_key)
    se.auth()

    promo_counts = get_promocodes_generated(se.session)
    minutes = get_timing_to_new_promo_generated(promo_counts)
    timing_list = []

    time = datetime.datetime(year=2021, month=1, day=1, hour=6, minute=minutes)
    timing_list.append(time.strftime("%H:%M"))

    for i in range(promo_counts - 1):
        time += datetime.timedelta(minutes=minutes)
        timing_list.append(time.strftime("%H:%M"))

    with open('times_data.txt', 'w') as f:
        f.write('\n'.join(timing_list))