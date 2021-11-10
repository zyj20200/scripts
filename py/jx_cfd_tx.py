import re
import os
import json
import time
import random
import requests
import datetime
import threading
# from ping3 import ping

class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid

    def get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': self.CORPID,
                  'corpsecret': self.CORPSECRET,
                  }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def send_text(self, message, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {
                "content": message
            },
            "safe": "0"
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [
                    {
                        "title": title,
                        "thumb_media_id": media_id,
                        "author": "Author",
                        "content_source_url": "",
                        "content": message.replace('\n', '<br/>'),
                        "digest": message
                    }
                ]
            }
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]


# 企业微信 APP 推送
def wecom_app(title, content):
    QYWX_AM = os.getenv("QYWX_AM")
    try:
        if not QYWX_AM:
            print("QYWX_AM 并未设置！！\n取消推送")
            return
        QYWX_AM_AY = re.split(',', QYWX_AM)
        if 4 < len(QYWX_AM_AY) > 5:
            print("QYWX_AM 设置错误！！\n取消推送")
            return
        corpid = QYWX_AM_AY[0]
        corpsecret = QYWX_AM_AY[1]
        touser = QYWX_AM_AY[2]
        agentid = QYWX_AM_AY[3]
        try:
            media_id = QYWX_AM_AY[4]
        except:
            media_id = ''
        wx = WeCom(corpid, corpsecret, agentid)
        # 如果没有配置 media_id 默认就以 text 方式发送
        if not media_id:
            message = title + '\n\n' + content
            response = wx.send_text(message, touser)
        else:
            response = wx.send_mpnews(title, content, media_id, touser)
        if response == 'ok':
            print('推送成功！')
        else:
            print('推送失败！错误信息如下：\n', response)
    except Exception as e:
        print(e)



def get_cks():
    try:
        ckfile = '/ql/config/env.sh'
        # ckfile = 'env.sh'
        with open(ckfile, "r", encoding="utf-8") as f:
            cks = f.read()
            f.close()
        if 'pt_key=' in cks and 'pt_pin=' in cks:
            r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
            cks = r.findall(cks)
    except Exception as e:
        print(e)
        cks = []
    return cks

def get_msg(response):
    response_str = response.content.decode()
    str = response_str.replace("jsonpCBKUUU(", "").replace(")", "")
    msg = json.loads(str)['sErrMsg']
    print(datetime.datetime.now(), msg)

def get_url(cfd_tx_money):
    dwLvl,ddwPaperMoney = get_tx_code(cfd_tx_money)
    now_str = "".join(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f').split("-"))[:-3]
    url = "https://m.jingxi.com/jxbfd/user/ExchangePrize?strZone=jxbfd&bizCode=jxbfd&source=jxbfd&dwEnv=7&_cfd_t={}"\
        "&ptag=7155.9.47&dwType=3&dwLvl={}&ddwPaperMoney={}&strPoolName=jxcfd2_exchange_hb_202111&strPgtimestamp={}&"\
        "strPhoneID=3636d114be09065903a87cac850664cfa6d22727&strPgUUNum=cff01be11c4a4129e33deb03100901f0&"\
        "_stk=_cfd_t%2CbizCode%2CddwPaperMoney%2CdwEnv%2CdwLvl%2CdwType%2Cptag%2Csource%2CstrPgUUNum%2CstrPgtimestamp%2CstrPhoneID%2CstrPoolName%2CstrZone&"\
        "_ste=1&h5st={}%3B1238631108179162%3B10032%3Btk01wc9c71d4730n4jYtF4cdKYvFjoZoeAm0w2vr0aXASaCbXDglkXQ7wvakIOqBTDNERhtcdUcCtrsq1"\
        "iMv6Zkdu%2FQe%3Bfde2d1e0f4e3a6e31d22ccd8ac15429cf41465462a392e4e70af1f1a6c91c5e2&"\
        "_=1636004948570&sceneval=2&g_login_type=1&callback=jsonpCBKI&g_ty=ls".format(int(time.time()*1000)-2, dwLvl, ddwPaperMoney, int(time.time()*1000), now_str)
    return url

def get_tx_code(cfd_tx_money):
    cfd_tx_money_dict = {"1111元":{"dwLvl":1, "ddwPaperMoney":1111000}, "111元":{"dwLvl":2, "ddwPaperMoney":111000}, 
                        "100元":{"dwLvl":3, "ddwPaperMoney":100000}, "0.1元":{"dwLvl":8, "ddwPaperMoney":100}, 
                        "0.2元":{"dwLvl":7, "ddwPaperMoney":200}, "0.5元":{"dwLvl":6, "ddwPaperMoney":500}, 
                        "1元":{"dwLvl":5, "ddwPaperMoney":1000}, "11元":{"dwLvl":4, "ddwPaperMoney":11000}}
    
    dwLvl = cfd_tx_money_dict[cfd_tx_money]["dwLvl"]
    ddwPaperMoney = cfd_tx_money_dict[cfd_tx_money]["ddwPaperMoney"]
    return dwLvl,ddwPaperMoney


def run(cookie, cfd_tx_money):
    
    headers = {"Sec-Fetch-Mode": "no-cors",
               "User-Agent": ua,
               "Accept": "*/*", "X-Requested-With": "com.jd.pingou", "Sec-Fetch-Site": "same-site",
               "Referer": "https://st.jingxi.com/",
               "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
               "Connection": "close",
               "Cookie": cookie}

    response = requests.get(get_url(cfd_tx_money), headers=headers)
    response_str = response.content.decode()
    print(cookie.split(";")[1])
    print(response_str)
    if "strName" in response_str:
        mark_name = pt_pin_to_mark_name.get(cookie.split(";")[1], cookie.split(";")[1])
        wecom_app(mark_name, cfd_tx_money)

USER_AGENTS = [
    "jdapp;android;10.0.2;10;network/wifi;Mozilla/5.0 (Linux; Android 10; ONEPLUS A5010 Build/QKQ1.191014.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045230 Mobile Safari/537.36",
    "jdapp;iPhone;10.0.2;14.3;network/4g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;android;10.0.2;9;network/4g;Mozilla/5.0 (Linux; Android 9; Mi Note 3 Build/PKQ1.181007.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045131 Mobile Safari/537.36",
    "jdapp;android;10.0.2;10;network/wifi;Mozilla/5.0 (Linux; Android 10; GM1910 Build/QKQ1.190716.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045230 Mobile Safari/537.36",
    "jdapp;android;10.0.2;9;network/wifi;Mozilla/5.0 (Linux; Android 9; 16T Build/PKQ1.190616.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044942 Mobile Safari/537.36",
    "jdapp;iPhone;10.0.2;13.6;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;iPhone;10.0.2;13.6;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 13_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;iPhone;10.0.2;13.5;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;iPhone;10.0.2;14.1;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;iPhone;10.0.2;13.3;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;iPhone;10.0.2;13.7;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 13_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;iPhone;10.0.2;14.1;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;iPhone;10.0.2;13.3;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;iPhone;10.0.2;13.4;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 13_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;iPhone;10.0.2;14.3;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;android;10.0.2;9;network/wifi;Mozilla/5.0 (Linux; Android 9; MI 6 Build/PKQ1.190118.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044942 Mobile Safari/537.36",
    "jdapp;android;10.0.2;11;network/wifi;Mozilla/5.0 (Linux; Android 11; Redmi K30 5G Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045511 Mobile Safari/537.36",
    "jdapp;iPhone;10.0.2;11.4;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15F79",
    "jdapp;android;10.0.2;10;;network/wifi;Mozilla/5.0 (Linux; Android 10; M2006J10C Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045230 Mobile Safari/537.36",
    "jdapp;android;10.0.2;10;network/wifi;Mozilla/5.0 (Linux; Android 10; M2006J10C Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045230 Mobile Safari/537.36",
    "jdapp;android;10.0.2;10;network/wifi;Mozilla/5.0 (Linux; Android 10; ONEPLUS A6000 Build/QKQ1.190716.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045224 Mobile Safari/537.36",
    "jdapp;android;10.0.2;9;network/wifi;Mozilla/5.0 (Linux; Android 9; MHA-AL00 Build/HUAWEIMHA-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044942 Mobile Safari/537.36",
    "jdapp;android;10.0.2;8.1.0;network/wifi;Mozilla/5.0 (Linux; Android 8.1.0; 16 X Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044942 Mobile Safari/537.36",
    "jdapp;android;10.0.2;8.0.0;network/wifi;Mozilla/5.0 (Linux; Android 8.0.0; HTC U-3w Build/OPR6.170623.013; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/044942 Mobile Safari/537.36",
    "jdapp;iPhone;10.0.2;14.0.1;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;android;10.0.2;10;network/wifi;Mozilla/5.0 (Linux; Android 10; LYA-AL00 Build/HUAWEILYA-AL00L; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045230 Mobile Safari/537.36",
    "jdapp;iPhone;10.0.2;14.2;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;iPhone;10.0.2;14.3;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;iPhone;10.0.2;14.2;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;android;10.0.2;8.1.0;network/wifi;Mozilla/5.0 (Linux; Android 8.1.0; MI 8 Build/OPM1.171019.026; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045131 Mobile Safari/537.36",
    "jdapp;android;10.0.2;10;network/wifi;Mozilla/5.0 (Linux; Android 10; Redmi K20 Pro Premium Edition Build/QKQ1.190825.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045227 Mobile Safari/537.36",
    "jdapp;iPhone;10.0.2;14.3;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;iPhone;10.0.2;14.3;network/4g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdapp;android;10.0.2;11;network/wifi;Mozilla/5.0 (Linux; Android 11; Redmi K20 Pro Premium Edition Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045513 Mobile Safari/537.36",
    "jdapp;android;10.0.2;10;network/wifi;Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045227 Mobile Safari/537.36",
    "jdapp;iPhone;10.0.2;14.1;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
    "jdpingou;iPhone;5.9.0;15.1;3636d114be09065903a87cac850664cfa6d22727;network/4g;model/iPhone13,2;appBuild/100739;ADID/;supportApplePay/1;hasUPPay/0;pushNoticeIsOpen/0;hasOCPay/0;supportBestPay/0;session/517;pap/JA2019_3111789;brand/apple;supportJDSHWK/1;Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
]

pt_pin_to_mark_name = {"pt_pin=ZYJ20200":"zz", "pt_pin=jd_QHcpFcPfKVzJ":"zz22", "pt_pin=jd_nlxwonzEBJYv":"zky", 
                       "pt_pin=jd_4450c542568dc":"yw", "pt_pin=18211674289_p":"sjk", "pt_pin=%E8%B5%B5%E4%B8%96%E9%B9%8Fzsp":"zsp", 
                       "pt_pin=xiaodan0325":"cxd", "pt_pin=jd_644bf4a972545":"qjm", "pt_pin=jd_66d8bddc6cc40":"wcy", "pt_pin=jd_PRwkxeCtPUdB":"ay", 
                       "pt_pin=jd_68dd714132250":"lj", "pt_pin=jd_4fdaf5d8e9764":"xly", "pt_pin=jd_NZePTpJCuoNX":"yys", "pt_pin=jd_5835301b1d9b1":"lj-gf", 
                       "pt_pin=jd_44c2e27a5b5fa":"gzw", "pt_pin=ZY%E9%A2%96%E5%AD%9041":"sjk-gf"}

ua = random.choice(USER_AGENTS)

## 请求次数
cfd_get_num = 2
## 提现金额
cfd_tx_money = os.getenv('cfd_tx_money')
## 跑脚本用户
cfd_tx_run_pin = os.getenv('cfd_tx_run_pin', "").split("&")
## 获取cookie
cks = get_cks()
## 跑脚本的ck
run_cks = []

if cfd_tx_run_pin[0] != "":
  for i in cfd_tx_run_pin:
      for j in cks:
          if i in j:
              run_cks.append(j)
              break

thread_list = []
for i in range(cfd_get_num):
  for cookie in run_cks:
      thread_cfd = threading.Thread(target=run, args=(cookie, cfd_tx_money))
      thread_list.append(thread_cfd)
for t in thread_list:
    t.setDaemon(True)  # 把子线程设置为守护线程，该线程不重要，主线程结束，子线程结束
    t.start()
for thread in thread_list:
    thread.join()

