import requests
import json
from bs4 import BeautifulSoup as BS
import time
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import datetime
import urllib3
import winsound

# import cfscrape

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def load_data_from_file():
    result = {}
    try:
        if not os.path.exists('data.txt'):
            with open('data.txt', 'w') as f:
                f.write('{ "username":"", "password":""}')

        with open('data.txt') as json_file:
            data = json.load(json_file)

        if 'username' in data:
            result['username'] = data['username']
        if 'password' in data:
            result['password'] = data['password']
        if 'rucaptcha_key' in data:
            result['rucaptcha_key'] = data['rucaptcha_key']

    except KeyError as error:
        print('Cannot find: %s', error.args[0])
    except Exception as error:
        raise error
    else:
        return result['username'], result['password'], result['rucaptcha_key']


class SessionUC:
    def __init__(self, username, password, rucaptcha_key, recaptcha_response=None):
        self.__username = username
        self.__password = password
        # self.session = cfscrape.create_scraper()
        self.session = requests.Session()
        self.token = None
        self.promocode = None
        self.timing_list = []
        self.session.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'}

        self.payload = {
            'login': self.__username,
            'password': self.__password
        }

    def auth_uczone(self):
        token_get = self.session.get('https://uc.zone/login/login')
        token_bs = BS(token_get.text, 'html.parser')
        token_bs = token_bs.select_one('input[name="_xfToken"]')

        self.payload['_xfToken'] = token_bs.get('value')
        self.payload['remember'] = '1'
        r_auth = self.session.post('https://uc.zone/login/login', data=self.payload, verify=False)
        try:
            soup = BS(r_auth.text, 'html.parser')
            print(soup.select('span[class="p-navgroup-linkText"]')[0].text)
        except IndexError as error:
            print("Check email and confirm account..or shit happend.\nYou can try to use VPN. It helps some times.")
            print(error)
            exit()
        return r_auth

    def auth_dota(self):

        r_auth = self.session.post('https://dota-cheats.ru/api/v1/auth',
                                   data={
                                       'password': self.__password,
                                       'username': self.__username
                                   }, verify=False).json()
        if not r_auth['success']:
            print("Check email and confirm account..or shit happend.\nYou can try to use VPN. It helps some times.")
            exit()
        self.session.headers.update({'Authorization': 'Bearer ' + r_auth['token']})
        return r_auth

    def wait_new_promo(self):
        while True:
            try:
                time.sleep(0.5)
                promo_html = self.session.get('https://uc.zone/cheat-statuses/games/DotA2/load-promocode', verify=False)
                promo_bs = BS(promo_html.content, 'html.parser')
                try:
                    current_promocode = promo_bs.select('.gamePromocodeItem.gamePromocode--promocode')[0].text.strip()
                except:
                    continue
                print(current_promocode, end=' ')
                print(str(datetime.datetime.now().time()))
                promo = promo_bs.find('div', {'class': 'gamePromocodeItem gamePromocode--promocode is-activated'})

                if promo:
                    self.promocode = promo.text.strip()
                    return True
            except Exception as e:
                raise e

    def activate_promo(self):
        try:
            promo_req = self.session.post('https://dota-cheats.ru/api/v1/user/set-promocode',
                                          data={
                                              'promocode': self.promocode
                                          }).json()
            if 'errors' in promo_req:
                print(promo_req['errors'][0]['message'])
            print(promo_req)

            winsound.Beep(1000, 1000)
            # os.system('play --no-show-progress --null --channels 2 synth %s sine %f' %( 0.2, 400))
        except Exception as e:
            raise e


if __name__ == '__main__':
    username, password, rucaptcha_key = load_data_from_file()
    print(rucaptcha_key)
    print(username + ":" + password)
    se = SessionUC(username, password, rucaptcha_key=rucaptcha_key)
    se.auth_dota()
    se.auth_uczone()
    print('Waiting new promo')
    if se.wait_new_promo():
        print('Activating promocode')
        se.activate_promo()
    input()
