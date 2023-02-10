import time
import requests
import re
from urllib.parse import quote
import os

sno_count = []
try:
    if os.environ.get('GITHUB_RUN_ID', None):
        sno_count = os.environ.get('students','').split('\n')
    else:
        sno_count = ['212006165 福建省 福州市 闽侯县 阳康']
except:
    print('配置环境出错')

def daka():
    for info in sno_count:
        student_info = info.split(' ')
        sno = student_info[0]
        sheng = student_info[1]
        shi = student_info[2]
        qu = student_info[3]
        txwz = sheng+shi+qu
        zt = student_info[4]
        if zt != '阳康' and zt != '未阳' and zt != '阳了':
            print('状态错误')
            return 1
        url = 'http://dw10.fdzcxy.edu.cn/datawarn/ReportServer?formlet=app/sjkrb.frm&op=h5&userno='+sno+'#/form'
        pattern = re.compile('([a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12})')
        headers = {
            '__device__': 'android',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'clientType': 'mobile/h5_5.0',
            'Connection': 'keep-alive',
            'deviceType': 'android',
            'Host': 'dw10.fdzcxy.edu.cn',
            'Referer': 'http://dw10.fdzcxy.edu.cn/datawarn/ReportServer?formlet=app/sjkrb.frm&op=h5&userno='+sno,
            'terminal': 'H5',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36 Edg/108.0.1462.54',
        }



        #获取sessionId和cookie
        res = requests.get(url,headers=headers)
        res.encoding = res.apparent_encoding
        sessionID = re.search(pattern,res.text)[0]
        url = 'http://dw10.fdzcxy.edu.cn/datawarn/decision/view/form?sessionID='+sessionID+'&op=fr_form&cmd=load_content&toVanCharts=true&fine_api_v_json=3&widgetVersion=1'
        cookie = 'JSESSIONID=' + requests.utils.dict_from_cookiejar(res.cookies)['JSESSIONID']
        #sessionID每次都会变化要取寻找sessionID再请求地址

        #获取JsconfId，CallbackConfId,name同上
        params = {
            'op':
                'fr_form',
            'cmd':
                'load_content_mobile',
            'toVanCharts':
                'true',
            'dynamicHyperlink':
                'true',
            'pageIndex':
                '1',
            'sessionID':
                sessionID,
            'fine_api_v_json':
                   '3',
            'widgetName':
                'REPORT0'
        }
        res = requests.get(url, headers=headers, params=params)
        source = res.json()
        items = source['items'][0]['el']['items']
        name = items[2]['value']
        for i in items:
            if i['widgetName'] == 'SUBMIT':
                submit = i['listeners'][0]['action']
                break
        # print(submit)
        JsConfId = pattern.findall(submit)[0]  # 拿到两个验证码
        CallbackConfId = pattern.findall(submit)[1]

        def post_form(JsConfId,CallbackConfId,now_time,cookie,sessionID,sno,name,sheng,shi,qu,txwz):
            headers = {
                '__device__': 'android',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'Cache-Control': 'no-cache',
                'clientType': 'mobile/h5_5.0',
                'Connection': 'keep-alive',
                'Content-Length': '4403',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Cookie': cookie,
                'deviceType': 'android',
                'Host': 'dw10.fdzcxy.edu.cn',
                'Origin': 'http://dw10.fdzcxy.edu.cn',
                'Referer': 'http://dw10.fdzcxy.edu.cn/datawarn/ReportServer?formlet=app/sjkrb.frm&op=h5&userno='+sno,
                'sessionID': sessionID,
                'terminal': 'H5',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36 Edg/108.0.1462.76'
            }
            print(sheng,shi,qu,sno,name,txwz,now_time,zt)
            data = {
                'op': 'dbcommit',
                '__parameters__': quote(
                '{"jsConfId":"'+JsConfId+'","callbackConfId":"'+CallbackConfId+'","'
                    'LABEL2":"  每日健康上报","XH":"'+sno+'","XM":"'+name+'","LABEL12":"","LABEL0":"'
                    '1. 目前所在位置:","SHENG":"'+sheng+'","SHI":"'+shi+'","QU":"'+qu+'","'
                    'LABEL11":"2.填报时间:","SJ":"'+now_time+'",'
                    '"LABEL1":"3. 今日体温是否正常？(体温小于37.3为正常)","TWZC":"正常","LABEL6":"目前体温为：","TW":"0",'
                    '"TXWZ":"'+txwz+'","LABEL3":"4. 今日健康状况？","JK":["健康"],"JKZK":"","QTB":"请输入具体症状：","QT":" ","'
                    'LABEL4":"5. 目前新冠感染情况？","XGGRQK":"'+zt+'","LABEL5":"6.目前已接种新冠疫苗接种针数？","JZYMZS":"3","'
                    'LABEL7":"* 本人承诺以上所填报的内容全部真实，并愿意承担相应责任。","CHECK":true,"WZXXXX":"2","DWWZ":{},"SUBMIT":"提交信息"}')
            }
            #""是对，与:操作的不是对汉字--> "," ":" 替换时候应注意保留 如填写位置那里
            url = 'http://dw10.fdzcxy.edu.cn/datawarn/decision/view/form'
            res = requests.post(url,headers = headers,data = data)


        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
            post_form(JsConfId,CallbackConfId,now_time,cookie,sessionID,sno,name,sheng,shi,qu,txwz)
            print('{0}你自动填报的时间是:{1}'.format(name,now_time))
        except:
            print("填报错误请再次试试")

daka()
