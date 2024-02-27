import csv
import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import requests
import re
'''
这是基础版本，本来想法是打算通过github的repositories实现自动打卡，但是首先是workflows的yml配置我不知道我写的对不对

第二是使用该代码是用chromedriver实现自动打卡，一是目录很难找到虽然我后来通过github上的actions报错找到了github上python文件的目录
二是我cp命令复制chromedriver过去后依然报错，我猜测是因为没有浏览器，然后我通过上传文件发现github上的代码仓库无法上传大的文件也就无法上传浏览器
最后我的想法是通过post方法来实现表单打卡，但是我也不知道在我写完这个基础版本后复习完还有没有时间在截止时间之前完成自动打卡的程序，所以我先上传这个基础版本
'''

url = 'http://dw10.fdzcxy.edu.cn/datawarn/ReportServer?formlet=app/sjkrb.frm&op=h5&userno=这里填学号#/form'#为保护隐私我将学号删除了使用时将学号换成对应学号即可
pattern = re.compile('([a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12})')
web = Chrome()
web.get(url)




headers = {
    '__device__': 'android',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'clientType': 'mobile/h5_5.0',
    'Connection': 'keep-alive',
    'Cookie': 'JSESSIONID=CB299DDFB73B6CF66A2CC6FF2159E768',
    'deviceType': 'android',
    'Host': 'dw10.fdzcxy.edu.cn',
    'Referer': 'http://dw10.fdzcxy.edu.cn/datawarn/ReportServer?formlet=app/sjkrb.frm&op=h5&userno=212006165',
    'terminal': 'H5',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36 Edg/108.0.1462.54',
}
res = requests.get(url,headers=headers)
res.encoding = res.apparent_encoding
sessionID = re.search(pattern,res.text)[0]
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
url = 'http://dw10.fdzcxy.edu.cn/datawarn/decision/view/form?sessionID='+sessionID+'&op=fr_form&cmd=load_content&toVanCharts=true&fine_api_v_json=3&widgetVersion=1'
#sessionID每次都会变化要取寻找sessionID再请求地址






try:
    web.implicitly_wait(10)
    res = requests.get(url, headers=headers, params=params)
    source = res.json()
    name = source['items'][0]['el']['items'][2]['value']#ajax法
    '''
    利用chromdriver获取: 
    name = web.find_element(By.XPATH,'//*[@id="XM"]/div[2]/div')
    '''
    wait = WebDriverWait(web,10)
    web.find_element(By.XPATH,'//*[@id="CHECK"]/div[2]/div[2]/input').click()
    time.sleep(3)
    #不知道为什么wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="SUBMIT"]/div[2]')))没效果
    web.find_element(By.XPATH,'//*[@id="SUBMIT"]/div[2]').click()
    time = web.find_element(By.XPATH,'//*[@id="SJ"]/div[2]/div/div[1]')
    #ajax封装的时间是用时间戳表示不好获取这里改用chromedriver
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div[2]/div/div/div/div[1]/div')))
except:
    print('填报失败，请再次尝试')

with open('health.csv','a+') as f:
    writer = csv.writer(f)
    writer.writerow(['{0}你自动填报的时间是:{1}'.format(name,time.text)])


