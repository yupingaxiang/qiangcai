#coding=utf-8
import requests
import json
import time
from urllib import quote
from urllib import unquote

import sys
reload(sys)
sys.setdefaultencoding('utf-8') 

headers = {
    'Host': 'maicai.api.ddxq.mobi',
    'Connection': 'keep-alive',
    'Content-Length': '',
    'content-type': 'application/x-www-form-urlencoded',
    'ddmc-city-number': '',
    'ddmc-build-version': '2.83.0',
    'ddmc-device-id': '',
    'ddmc-station-id': '',
    'ddmc-channel': 'applet',
    'ddmc-os-version': '',
    'ddmc-app-client-id': '4',
    'Cookie': '',
    'ddmc-ip': '',
    'ddmc-longitude': '',
    'ddmc-latitude': '',
    'ddmc-api-version': '9.50.0',
    'ddmc-uid': '',
    'Accept-Encoding': 'gzip,compress,br,deflate',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.18(0x1800123c) NetType/WIFI Language/zh_CN',
    'Referer': 'https://servicewechat.com/wx1e113254eda17715/421/page-frame.html'
}

url = "https://maicai.api.ddxq.mobi/order/addNewOrder"

# 一个下单时间即可
datas = [
""
]

def toKv(data):
    strData = ""
    for key in data:
        if key == "package_order":
            strData = strData + "&" + key+"="+quote(json.dumps(data[key]))
        else:
            strData = strData + "&" + key+"="+data[key]

    strData = strData[1:]
    return strData

jsonDatas = []

for data in datas:
    dataArry = data.split('&')
    jsonData = {}
    for da in dataArry:
        s = da.split('=')
        if s[0] == "package_order":
            jsonData[s[0]] = json.loads(unquote(s[1]))
        else:
            jsonData[s[0]] = s[1]
    jsonData["package_order"]["payment_order"]["reserved_time_start"] = 1680123600
    jsonData["package_order"]["payment_order"]["reserved_time_end"] = 1680188400
    jsonData["package_order"]["packages"][0]["reserved_time_start"] = 1680123600
    jsonData["package_order"]["packages"][0]["reserved_time_end"] = 1680188400
    jsonDatas.append(jsonData)

def main():
    while True:
        for data in jsonDatas:
            # try:
            r = requests.post(url, headers = headers,data = toKv(data))
            # print(r.text)
            if r.status_code == 200:
                jsondata = json.loads(r.text)
                print("code: "+str(jsondata.get("code")))
                if jsondata.get("success") == True or jsondata.get("code") == 0:
                    print(u"下单成功")
                    return
                if jsondata.get("code") == 5001:
                    backdata = jsondata.get("data")
                    data["package_order"]["payment_order"]["price"] = backdata["order"]["total_money"]
                    data["package_order"]["packages"][0]["total_money"] = backdata["order"]["total_money"]
                    # data["package_order"]["packages"][0]["total_origin_money"] = backdata["order"]["total_money"]
                    data["package_order"]["packages"][0]["goods_real_money"] = backdata["order"]["total_money"]

                    newdata = []
                    for old in data["package_order"]["packages"][0]["products"]:
                        add = True
                        for new in backdata["stockout_products"]:
                            if new["id"] == old["id"]:
                                add = False
                                break
                        if add:
                            newdata.append(old)

                    sort = 1
                    for value in newdata:
                        value["order_sort"] = sort
                        sort = sort + 1

                    oldCount = data["package_order"]["packages"][0]["total_count"]
                    data["package_order"]["packages"][0]["products"] = newdata

                    data["package_order"]["packages"][0]["total_count"] = len(newdata)#len(backdata["package_order"]["packages"][0])
                    data["package_order"]["packages"][0]["cart_count"] = len(newdata)#len(backdata["package_order"]["packages"][0])
                    print(u"自动删除商品:"+ str(oldCount - len(newdata)))
                elif jsondata.get("code") == 5003:
                    backdata = jsondata.get("data")
                    data["package_order"]["payment_order"]["parent_order_sign"] = backdata["package_order"]["payment_order"]["parent_order_sign"]
                    data["package_order"]["payment_order"]["address_id"] = backdata["package_order"]["payment_order"]["address_id"]
                    data["package_order"]["payment_order"]["user_ticket_id"] = backdata["package_order"]["payment_order"]["user_ticket_id"]
                # elif jsondata.get("code") == 5004:
                #     print(u"您选择的送达时间已经失效了")
                if len(jsondata.get("msg")) > 0:
                    print("msg: " + jsondata.get("msg"))
                elif jsondata.get("tips").get("limitMsg") != None:
                    print("msg: " + jsondata.get("tips").get("limitMsg"))
            # except:
            #     print(u"请求异常")

        time.sleep(0.1)

if __name__ == '__main__':
   main()
