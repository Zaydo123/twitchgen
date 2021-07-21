import os
import sys
import time
import string
import random, threading, requests, colorama
from colorama import init, Fore
from threading import Thread, active_count
from requests_futures.sessions import FuturesSession
from twocaptcha import TwoCaptcha

init(autoreset=True)
lock = threading.Lock()
if sys.platform == "linux":
    clear = lambda: os.system("clear")
else:
    clear = lambda: os.system("cls")

num = 0
proxies = []
session = FuturesSession()

config={"apiKey":'put ur mf api key here',"defaultTimeout":600}
solver = TwoCaptcha(**config)


def report_bad(id):
    r = requests.get(f"http://2captcha.com/res.php?key={config['apiKey']}&action=reportbad&id="+str(id))
    with lock:
        print(Fore.RED+r.text)
def report_good(id):
    r = requests.get(f"http://2captcha.com/res.php?key={config['apiKey']}&action=reportgood&id="+str(id))
    with lock:
        print(Fore.BLUE+r.text)


class Email:

    def Get_Code(email):
        r = session.get(f"http://foreskin.market/api/latest/{email}?no-reply@twitch.tv").result()
        if "verify_code" in r.text:
            code = r.text.split('vertical-align:top;word-wrap:break-word;border-radius:2px;overflow:hidden"><a href="')[1].split("\"")[0]
            return code
        else:
            time.sleep(5)
            print(r.text)
            return False

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
                report_bad(captcha_id)
                return None
        return (current_prxy, captcha,captcha_id)

    

class Twitch:

    def Save(name, data):
        with open(f"{name}.txt", "a+") as f:
            #print("SAVING")
            f.write(f"{data}\n")
            f.close()

    def Send_Code(token):
        headers = {
            "Authorization": f"OAuth {token}"
        }
        json = [{"operationName":"CoreAuthCurrentUser","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"bc444c5b28754cb660ed183236bb5fe083f2549d1804a304842dad846d51f3ee"}}},{"operationName":"VerficationCodeUser","variables":{},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"77d945a4cee34ec9008cc61a978d7baeabce0631f2aa0076977ba13ac409dda2"}}}]
        print("sending code")
        r = session.post("https://gql.twitch.tv/gql", json=json, headers=headers).result()
        print("sent code",r.text)

    def Verify(token, opaqueID):
        headers = {
            "Authorization": f"OAuth {token}",
            "Client-Id": "kimne78kx3ncx6brgo4mv6wki5h1ko"
        }
        json = [{"operationName":"VerifyEmail","variables":{"input":{"opaqueID":opaqueID}},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"4d3cbb19003b87567cb6f59b186e989c69b0751ecdd799be6004d200014258f1"}}}]
        r = session.post("https://gql.twitch.tv/gql", json=json, headers=headers).result()
        print("verifying email")
        if r.json()[0]["data"]["verifyContactMethod"]["isSuccess"]:
            return True
        else:
            return False

    def Create(proxy,captcha,captchaid):
        global num
        try:
            username = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(10))
            email = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(12))
            email = Email.Create(email)
            password = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(15))
            #print(email,'\n',username,password)
            json = {"username":username,"password":password,"email":f"{email}","birthday":{"day":15,"month":2,"year":2000},"client_id":"kimne78kx3ncx6brgo4mv6wki5h1ko","include_verification_code":True,"arkose":{"token":captcha}}
            r = session.post("https://passport.twitch.tv/register", json=json, proxies={"https": f"http://{proxy}"}, timeout=20).result()
            #print("CREATED ACCOUNT")
            if "access_token" in r.text:
                token = r.json()["access_token"]
                #print(token)
                report_good(captchaid)
                num += 1
                #Twitch.Send_Code(token)
                #while True:
                #    verify_code = Email.Get_Code(email)
                #    print(verify_code)
                #    if verify_code == False:
                #        continue
                #    else:
                #        break
                #opaqueID = verify_code.split("email-verification/")[1].split("?")[0]
                #if Twitch.Verify(token, opaqueID):
                #    print(f"[\x1b[38;5;199m$\x1b[0m] Successfully Created Verified Account \x1b[38;5;199m#\x1b[0m{num} [\x1b[38;5;199m{username}:{password}\x1b[0m]")
                Twitch.Save("Accounts", f"{username}:{password}:{token}")
                Twitch.Save("Tokens", f"{token}")
            elif "Please complete the CAPTCHA correctly" in r.text:
                report_bad(captchaid)
        except requests.exceptions.ProxyError:
            proxies.remove(proxy)
            with lock:
                print(f"[$]{Fore.RED}PRXY ERROR",end='\r')
            Twitch.Create(str(random.choice(proxies)),captcha,captchaid)
        except requests.exceptions.ConnectTimeout:
            proxies.remove(proxy)
            with lock:
                print(f"[$]{Fore.RED}PRXY ERROR",end='\r')
            Twitch.Create(str(random.choice(proxies)),captcha,captchaid)
        except requests.exceptions.SSLError:
            with lock:
                print(f"[$]{Fore.RED}PRXY ERROR",end='\r')
            Twitch.Create(str(random.choice(proxies)),captcha,captchaid)
        except Exception as e:
            if str(e).find("list.remove")!=-1:
                return
            print(e)
            return

def Load_Proxy():
    for line in open('Proxies.txt'):
        proxies.append(line.replace('\n', ''))
    print(f"{Fore.MAGENTA}[$]{Fore.RESET} Loaded {len(proxies)} Proxies")

def Task():
    try:
        output = CaptchaSolver.Create_Task()
        if output == None:
            return
        #print(str(output))
        current_proxy = output[0];captcha = output[1];captcha_id = output[2]
        print(f"{Fore.MAGENTA}[$]{Fore.RESET} {current_proxy} : Creating Twitch Account")
        Twitch.Create(current_proxy,captcha,captcha_id)

    except Exception as e:   
        print(f"{e}\n\n")
        print("[@] Fatal Captcha Error.")

if __name__ == "__main__":
    clear()
    print("""
\x1b[38;5;199m.▄▄ · ▄▄▌ ▐ ▄▌ ▄▄▄· ▄▄▄▄▄▄▄▄▄▄▄▄▄ .·▄▄▄▄  
▐█ ▀. ██· █▌▐█▐█ ▀█ •██  •██  ▀▄.▀·██▪ ██ 
▄▀▀▀█▄██▪▐█▐▐▌▄█▀▀█  ▐█.▪ ▐█.▪▐▀▀▪▄▐█· ▐█▌
▐█▄▪▐█▐█▌██▐█▌▐█ ▪▐▌ ▐█▌· ▐█▌·▐█▄▄▌██. ██ 
 ▀▀▀▀  ▀▀▀▀ ▀▪ ▀  ▀  ▀▀▀  ▀▀▀  ▀▀▀ ▀▀▀▀▀• \x1b[0mTwitch
""")
    Load_Proxy()
    print(f"{Fore.MAGENTA}[$]{Fore.RESET} Current Balance: {str(solver.balance())}")
    #Task()
    threadct=int(input("How many threads: "))
    while True:
        os.system(f"""title, Threadcount = {threading.activeCount()} // Current Balance: {str(solver.balance())} // Successful:{num} """)
        time.sleep(.5)
        if active_count() >=threadct:
            pass
        else:
            try:
                Thread(target=Task).start()
            except (KeyboardInterrupt, SystemExit):
                sys.exit() 
