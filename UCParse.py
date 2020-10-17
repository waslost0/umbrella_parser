import requests
import json
from bs4 import BeautifulSoup as BS
import time
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import datetime

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


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
        self.session = requests.Session()
        self.token = None
        self.promocode = None
        self.g_rec = recaptcha_response
        self.rucaptcha_key = rucaptcha_key
        self.timing_list = []

        self.payload = {
            'login': self.__username,
            'password': self.__password,
            'remember': 1,
            '_xfRedirect': '/',
            '_xfToken': ''
        }

    def load_timig_list(self):
        with open("times_data.txt", "r") as file:
            self.timing_list = file.read()
        self.timing_list = self.timing_list.split('\n') 

    def auth(self):
        r_auth = self.session.post('https://uc.zone/login/login', data=self.payload, verify=False)
        token_bs = BS(r_auth.text, 'html.parser')
        try:
            self.token = token_bs.select('input[name=_xfToken]')[0]['value']
        except IndexError as e:
            print("Check email and confirm account..or shit happend.\nYou can try to use VPN. It helps some times.")
            exit()
        return r_auth

    def get_curr_time(self):
        curr_time = datetime.datetime.now().strftime("%H:%M")
        curr_time_list = list(curr_time)
        curr_time_list[-1] = str(int(curr_time_list[-1]) + 1)
        return ''.join(curr_time_list) 

    def wait_new_promo(self):
        captcha_got = 0
        try:
            login_result = self.session.get("https://uc.zone/account/promocode", verify=False)
            token_bs = BS(login_result.text, 'html.parser')
            self.token = token_bs.select('input[name=_xfToken]')[0]['value']
        except Exception as e:
            print(e)
        self.load_timig_list()
        print(self.timing_list)

        while True:
            try:
                time.sleep(0.5)

                promo_html = self.session.get('https://uc.zone/cheat-statuses/games/DotA2/load-promocode', verify=False)
                promo_bs = BS(promo_html.content, 'html.parser')

                try:
                    current_promocode = promo_bs.select('.gamePromocodeItem.gamePromocode--promocode')[0].text.strip()
                except:
                    continue

                print(current_promocode)
                print(str(datetime.datetime.now().time()))
                current_minutes = str(datetime.datetime.now().time()).split(":")[1]

                curr_time = self.get_curr_time()
                if curr_time in self.timing_list and captcha_got != int(str(current_minutes)[1]):
                    self.g_rec = solve_captcha(self.rucaptcha_key, 'https://uc.zone/account/promocode')
                    captcha_got = int(str(current_minutes)[1])

                promo = promo_bs.find('div', {'class': 'gamePromocodeItem gamePromocode--promocode is-not-activated'})
                if promo:
                    self.promocode = promo.text.strip()
                    return True
            except Exception as e:
                raise e

    def activate_promo(self):
        try:
            promo_payload = {
                'promocode': self.promocode,
                'g-recaptcha-response': self.g_rec,
                '_xfToken': self.token,
                '_xfRequestUri': '/account/promocode'
            }
            print(promo_payload)

            promo_req = self.session.post('https://uc.zone/account/promocode', data=promo_payload)
            if 'errors' in promo_req.text:
                requests.post("http://rucaptcha.com/res.php?key=" + rucaptcha_key + "&action=reportbad&id=" + str(
                    self.recived_captcha_id))

            if "Вы не прошли проверку CAPTCHA должным образом." in promo_req.text:
                requests.post("http://rucaptcha.com/res.php?key=" + rucaptcha_key + "&action=reportbad&id=" + str(
                    self.recived_captcha_id))

            html_returned = BS(promo_req.content, 'html.parser')
            print(promo_req)
            #os.system('play --no-show-progress --null --channels 2 synth %s sine %f' %( 0.2, 400))
            return html_returned.select('.blockMessage')
        except Exception as e:
            raise e


def solve_captcha(rucaptcha_key, url):
    try:
        send_captcha = requests.get(
            "https://rucaptcha.com/in.php?key=" + rucaptcha_key + "&method=userrecaptcha&googlekey=" + "6LfY1TcUAAAAADxfJBcgupBVijeJO5v-81ZAEvOv" + "&pageurl=" + url)
    except Exception as e:
        raise e
    print(send_captcha.text)

    captcha_id = send_captcha.text.split("|")[1]


    print("rucaptcha id:" + captcha_id)
    time.sleep(15)
    while True:
        time.sleep(3)
        print("Ожидаю капчу")
        try:
            recived_captcha = requests.get(
                "https://rucaptcha.com/res.php?key=" + rucaptcha_key + "&action=get&id=" + captcha_id + "&json=1",
                timeout=20)
        except:
            continue
        if (recived_captcha.json()["request"] == "ERROR_CAPTCHA_UNSOLVABLE"):
            raise Exception("CaptchaUnsolvable")
        if recived_captcha.json()['status'] == 1:
            print(recived_captcha.json())
            return recived_captcha.json()['request']


if __name__ == '__main__':
    username, password, rucaptcha_key = load_data_from_file()
    print(rucaptcha_key)
    print(username + ":" + password)
    se = SessionUC(username, password, rucaptcha_key=rucaptcha_key)
    current_promocode = None

    login_result = se.auth()
    print('Waiting new promo')
    if se.wait_new_promo():
        print('Activating promocode')
        activate_result = se.activate_promo()
        print(activate_result)


    input()
