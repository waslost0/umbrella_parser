import requests
import json
from bs4 import BeautifulSoup as BS
import time
import sys
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning

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

    except KeyError as error:
        print('Cannot find: %s', error.args[0])
    except Exception as error:
        raise error
    else:
        return result['username'], result['password']

class SessionUC:
    
    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        self.session = requests.Session()
        self.token = None
        self.promocode = None

        self.payload = {
            'login': self.__username,
            'password': self.__password,
            'remember': 1,
            '_xfRedirect': '',
        }

    def auth(self):
        r_auth = self.session.post('https://uc.zone/login/login', data=self.payload, verify=False)
        token_bs = BS(r_auth.text, 'html.parser')
        try:
            self.token = token_bs.select('input[name=_xfToken]')[0]['value']
        except IndexError as e:
            print("Check email and confirm account..or shit happend")
        return r_auth

    def wait_new_promo(self):
        try:
            while True:
                time.sleep(3)
                promo_html = self.session.get('https://uc.zone/cheat-statuses/games/DotA2/load-promocode')
                promo_bs = BS(promo_html.content, 'html.parser')
             
                current_promocode = promo_bs.select('.gamePromocodeItem.gamePromocode--promocode')[0].text.strip()
                print(current_promocode)

                if promo_bs.select('.is-not-activated'):
                    self.promocode = promo_bs.select('.gamePromocodeItem.gamePromocode--promocode.is-not-activated')[0]\
                        .text.strip()
                    return True
        except Exception as e:
            current_promocode = promo_bs.select('.gamePromocode.gamePromocode--empty')[0].text.strip()
            print(e)
            print(current_promocode)
            return False
            

    def activate_promo(self):
        promo_payload = {
            'promocode': self.promocode,
            '_xfToken': self.token
        }
        print(promo_payload)

        promo_req = self.session.post('https://uc.zone/account/promocode', data=promo_payload)
        html_returned = BS(promo_req.content, 'html.parser')

        #os.system('play --no-show-progress --null --channels 2 synth %s sine %f' %( 0.2, 400))
        return html_returned.select('.p-body-pageContent')[0].text.strip()


if __name__ == '__main__':
    
<<<<<<< HEAD
    username, password = load_data_from_file()
    se = SessionUC(username, password)
=======
    se = SessionUC("USERNAME", "PASSWORD")
>>>>>>> 1445462dc0f8570011dfe08493c53a170fef7719

    login_result = se.auth()
    print(login_result.url)
    print(login_result.history)
    if not login_result.history:
        print("Invalid email or password")
        sys.exit()

    print(se.token)

    print('Waiting new promo')
    if se.wait_new_promo():
        print('Activating promocode')
        activate_result = se.activate_promo()

        print(activate_result)
    input()





