import os
import sys
import time
import string
import random, threading, requests, colorama
from colorama import init, Fore
from threading import Thread, active_count
from requests_futures.sessions import FuturesSession
from twocaptcha import TwoCaptcha
from AuthGG.client import Client
from os import path

def clear():
    if sys.platform == "linux" or sys.platform=="darwin":
        os.system("clear")
    else:
        os.system("cls")

#authgg shit
clear()
client = Client(api_key="BPMGYAWYEJGH", aid="40366", application_secret="fvMElFim0qfl11imG7aZT83oReAAFPrTi9g")
print("[Login]\nleave fields empty if you'd like to sign up\n____________________\n")

username = input("Username: ")
password = input("Password: ")
if username == "" and password== "":
    clear()
    email = input("Email: ")
    license_key = input("License: ")
    username = input("Username: ")
    password = input("Password: ")
    try:
	    client.register(email=email, username=username, password=password, license_key=license_key)
    except Exception as e:
	    print(e)
try:
	client.login(username, password)
	clear()
except Exception as e:
	print(e)
    time.sleep(10);quit()

######
filepaths = ['Proxies.txt','Accounts.txt','Tokens.txt']

for file in filepaths:
    if os.path.exists(file)!=True:
        open(file,'w')


init(autoreset=True)
lock = threading.Lock()

num = 0
proxies = []
session = FuturesSession()
debugmode=False
if debugmode==True:
    apikey="dev 2captcha api key"
if debugmode==True:
    pass
else:
    apikey=input("2captcha api key: ")

config={"apiKey":apikey,"defaultTimeout":600}
solver=TwoCaptcha(config["apiKey"])

def report_bad(id):
    r = requests.get(f"http://2captcha.com/res.php?key={config['apiKey']}&action=reportbad&id="+str(id))
    with lock:
        print(Fore.RED+r.text)
def report_good(id):
    r = requests.get(f"http://2captcha.com/res.php?key={config['apiKey']}&action=reportgood&id="+str(id))
    with lock:
        print(Fore.BLUE+r.text)


class Email:
    def Create(email):
        session.get(f'http://foreskin.market/api/{email}@foreskin.market')
        return f"{email}@foreskin.market"

class CaptchaSolver:
    def Create_Task():
        current_prxy = str(random.choice(proxies))
        #print("REQUESTING SOLUTION")
        result=requests.get(f"http://2captcha.com/in.php?key={config['apiKey']}&json=1&method=funcaptcha&publickey=E5554D43-23CC-1982-971D-6A2262A2CA24&pageurl=https://nojs-game3-prod-ap-southeast-1.arkoselabs.com/fc/api/nojs/?pkey=E5554D43-23CC-1982-971D-6A2262A2CA24",timeout=config["defaultTimeout"]).json()
        captcha_id = result['request']
        print(f"ID:{captcha_id}")
        while True:
            time.sleep(5)
            r=requests.get(f"""https://2captcha.com/res.php?key={config['apiKey']}&action=get&id={captcha_id}""")
            if r.text == "CAPCHA_NOT_READY":
                print("[#] Not Ready",end='\r')
            elif "OK|" in r.text:
                captcha=r.text.strip("OK|")
                print(f"{Fore.GREEN}[#] Solved {captcha_id}")
                break
            else:
                print(f"{Fore.RED}[#] Unknown Error: {r.text}")
                return None
        return (current_prxy, captcha,captcha_id)

    

class Twitch:

    def Save(name, data):
        with open(f"{name}.txt", "a+") as f:
            #print("SAVING")
            f.write(f"{data}\n")
            f.close()

    def Create(proxy,captcha,captchaid):
        global num
        try:
            username = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(10))
            email = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(12))
            email = Email.Create(email)
            password = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(15))
            json = {"username":username,"password":password,"email":f"{email}","birthday":{"day":15,"month":2,"year":2000},"client_id":"kimne78kx3ncx6brgo4mv6wki5h1ko","include_verification_code":True,"arkose":{"token":captcha}}
            r = session.post("https://passport.twitch.tv/register", json=json, proxies={"https": f"http://{proxy}"}, timeout=20).result()
            if "access_token" in r.text:
                token = r.json()["access_token"]
                report_good(captchaid)
                num += 1
                Twitch.Save("Accounts", f"{username}:{password}:{token}")
                Twitch.Save("Tokens", f"{token}")
            elif "Please complete the CAPTCHA correctly" in r.text:
                report_bad(captchaid)
        except requests.exceptions.ProxyError:
            proxies.pop(proxies.index(proxy))
            with lock:
                print(f"[$]{Fore.RED}PRXY ERROR",end='\r')
            Twitch.Create(str(random.choice(proxies)),captcha,captchaid)
        except requests.exceptions.ConnectTimeout:
            proxies.pop(proxies.index(proxy))
            with lock:
                print(f"[$]{Fore.RED}PRXY ERROR",end='\r')
            Twitch.Create(str(random.choice(proxies)),captcha,captchaid)
        except requests.exceptions.SSLError:
            with lock:
                print(f"[$]{Fore.RED}PRXY ERROR",end='\r')
            Twitch.Create(str(random.choice(proxies)),captcha,captchaid)
        except Exception as e:
            with lock:
                print(e)
            return

def Load_Proxy():
    for line in open('Proxies.txt'):
        proxies.append(line.replace('\n', ''))
    print(f"{Fore.BLUE}[$]{Fore.RESET} Loaded {len(proxies)} Proxies")
    if len(proxies)==0:
        print(Fore.RED+"Please fill Proxies.txt")
        time.sleep(5)
        quit()
def Task():
    try:
        output = CaptchaSolver.Create_Task()
        if output == None:
            return
        current_proxy = output[0];captcha = output[1];captcha_id = output[2]
        with lock:
            print(f"{Fore.BLUE}[$]{Fore.RESET} {current_proxy} : Creating Twitch Account")
        Twitch.Create(current_proxy,captcha,captcha_id)

    except Exception as e:   
        with lock:
            print(e)
            print("[@] Fatal Captcha Error.")

if __name__ == "__main__":
    clear()
    print(f"""{Fore.BLUE}
   .-') _               ('-.       .-') _  
  (  OO) )            _(  OO)     ( OO ) ) 
,(_)----.  ,----.    (,------.,--./ ,--,'  
|       | '  .-./-')  |  .---'|   \ |  |\  
'--.   /  |  |_( O- ) |  |    |    \|  | ) 
(_/   /   |  | .--, \(|  '--. |  .     |/  
 /   /___(|  | '. (_/ |  .--' |  |\    |   
|        ||  '--'  |  |  `---.|  | \   |   
`--------' `------'   `------'`--'  `--'   
{Fore.GREEN}[TWITCH GENERATOR - Zayd#1234]
""")
    Load_Proxy()
    print(f"{Fore.BLUE}[$]{Fore.RESET} Current Balance: {str(solver.balance())}")
    #Task()
    threadct=int(input("Thread Count: "))
    goal_amt = input("Amount To Generate (approximate): ")
    while True:
        if sys.platform!="darwin":
            os.system(f"""title, THREADS = {active_count()-1} > Current Balance: {str(solver.balance())} > CREATED: {num} """)
        time.sleep(.5)
        if active_count()-1 >=threadct:
            pass
        else:
            if num>=int(goal_amt):
                print("DONE CREATING ACCOUNTS... ALLOWING THREADS TO FINISH")
                print("You may need to close the program manually, give me a sec.")
                break
            else:
                try:
                    Thread(target=Task).start()
                except (KeyboardInterrupt, SystemExit):
                    sys.exit() 
