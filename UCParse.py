import requests
import json
from bs4 import BeautifulSoup as BS
import time
import sys
import os
import random
import pickle
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
        if 'rucaptcha_key' in data:
            result['rucaptcha_key'] = data['rucaptcha_key']

    except KeyError as error:
        print('Cannot find: %s', error.args[0])
    except Exception as error:
        raise error
    else:
        return result['username'], result['password'], result['rucaptcha_key']

class SessionUC:
    
    def __init__(self, username, password, recaptcha_response=None):
        self.__username = username
        self.__password = password
        self.session = requests.Session()
        self.token = None
        self.promocode = None
        self.g_rec = recaptcha_response

        self.payload = {
            'login': self.__username,
            'password': self.__password,
            'remember': 1,
            '_xfRedirect': '/',
            '_xfToken': ''
        }

    def auth(self):
        if os.path.isfile("cookies"):
            with open('cookies', 'rb') as file:
                self.session.cookies.update(pickle.load(file))
          
        promo_html = se.session.get('https://uc.zone/cheat-statuses/games/DotA2/load-promocode', verify=False)
        promo_bs = BS(promo_html.content, 'html.parser')
        current_promocode = None
        r_auth = None
        try:
            current_promocode = promo_bs.select('.gamePromocodeItem.gamePromocode--promocode')[0].text.strip()
        except IndexError as e:
            print("Login unsucc")
        
        if not current_promocode:
            print("Trying to login")
            if self.g_rec is None:
                r_auth = self.session.post('https://uc.zone/login/login', data=self.payload, verify=False)
            else:
                data = {
                    'login': self.__username,
                    'password': self.__password,
                    'g-recaptcha-response': self.g_rec,
                    'remember': 1,
                    '_xfRedirect': '/',
                    '_xfToken': ''
                }
                r_auth = self.session.post('https://uc.zone/login/login', data=data, verify=False)
            login_result = self.session.get("https://uc.zone/", verify=False)
            token_bs = BS(login_result.text, 'html.parser')
        else:
            login_result = self.session.get("https://uc.zone/", verify=False)
            token_bs = BS(login_result.text, 'html.parser')
        try:
            print(token_bs.select('input[name=_xfToken]'))
            self.token = token_bs.select('input[name=_xfToken]')[0]['value']                
                
        except IndexError as e:
            print("Captcha shit")
            
        else:
            with open('cookies', 'wb') as file:
                pickle.dump(self.session.cookies, file)
        return r_auth

    def wait_new_promo(self):
        try:
            while True:
                time.sleep(0.5)
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
            

    def activate_promo(self, captcha_token):
        promo_payload = {
            'promocode': self.promocode,
            'g-recaptcha-response': captcha_token,
            '_xfToken': self.token
        }
        print(promo_payload)

        promo_req = self.session.post('https://uc.zone/account/promocode', data=promo_payload)
        html_returned = BS(promo_req.content, 'html.parser')

        #os.system('play --no-show-progress --null --channels 2 synth %s sine %f' %( 0.2, 400))
        return html_returned.select('.p-body-pageContent')[0].text.strip()

def solve_captcha(rucaptcha_key, url):
        print(url)
        try:
            send_captcha = requests.get(
                "https://rucaptcha.com/in.php?key=" + rucaptcha_key + "&method=userrecaptcha&googlekey=" + "6LfY1TcUAAAAADxfJBcgupBVijeJO5v-81ZAEvOv" + "&pageurl=" + url)
        except Exception as e:
            raise e
        print(send_captcha.text)
        captcha_id = send_captcha.text.split("|")[1]
        print(captcha_id)
     
        print("rucaptcha id:" + captcha_id)
        while True:
            time.sleep(5)
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
                recived_captcha_id = captcha_id
                return recived_captcha.json()['request']

if __name__ == '__main__':


    username, password, rucaptcha_key = load_data_from_file()
    print(rucaptcha_key)
    print(username + ":" + password)
    se = SessionUC(username, password)
    current_promocode = None
   
    login_result = se.auth()
    
    try:
        promo_html = se.session.get('https://uc.zone/cheat-statuses/games/DotA2/load-promocode')
        promo_bs = BS(promo_html.content, 'html.parser')
        current_promocode = promo_bs.select('.gamePromocodeItem.gamePromocode--promocode')[0].text.strip()
        print(current_promocode)
    except Exception as e:
        print(e)
    
    if not current_promocode:
        print("Captcha")
        recaptcha_response = solve_captcha(rucaptcha_key, 'https://uc.zone/login/login')
        print(recaptcha_response)
        
        se = SessionUC(username, password, recaptcha_response)
        login_result = se.auth()
        print(login_result.url)
        print(login_result.history)
        

    print(se.token)

    print('Waiting new promo')
    if se.wait_new_promo():
        print('Activating promocode')
        recaptcha_response = solve_captcha(rucaptcha_key, 'https://uc.zone/account/promocode')
        activate_result = se.activate_promo(recaptcha_response)

        print(activate_result)
    input()





