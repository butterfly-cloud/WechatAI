#phthon3.5
#coding=utf8
#星座运势

from urllib import request, parse
import json
import random
 
class Zodic(object):
    def __init__(self):
        self.showapi_appid="36950"  #替换此值
        self.showapi_sign="43d37c53fb114121adaf6b94977db181"   #替换此值
        self.url="http://route.showapi.com/872-1"
        self.stars = {'白羊':'baiyang','金牛':'jinniu', '双子':'shuangzi','巨蟹':'juxie', \
                        '狮子':'shizi', '处女':'chunv', '天秤':'tiancheng', '天蝎':'tianxie',\
                        '射手':'sheshou','摩羯':'mojie','水瓶':'shuiping', '双鱼':'shuangyu', \
                        '白羊座':'baiyang','金牛座':'jinniu', '双子座':'shuangzi','巨蟹座':'juxie', \
                        '狮子座':'shizi', '处女座':'chunv', '天秤座':'tiancheng', '天蝎座':'tianxie',\
                        '射手座':'sheshou','摩羯座':'mojie','水瓶座':'shuiping', '双鱼座':'shuangyu'}
        
    def replace_html(self, msg):
        if msg is not None:
            msg = msg.replace("\\n","").replace('\\r','')
            msg = msg.replace("<br />","")
        return msg
 
    def get_data(self, star='摩羯'):
        send_data = parse.urlencode([
            ('showapi_appid', self.showapi_appid)
            ,('showapi_sign', self.showapi_sign)
                            ,('star', self.stars.get(star))
                            ,('needTomorrow', "0")
                            ,('needWeek', "0")
                            ,('needMonth', "0")
                            ,('needYear', "0")
             
          ])
        req = request.Request(self.url)
        with request.urlopen(req, data=send_data.encode('utf-8')) as f:
            #print('Status:', f.status, f.reason)
            if int(f.status) != 200:
                return f.reason
            str_res= f.read().decode('utf-8')
            str_res = self.replace_html(str_res)
            str_res = json.loads(str_res)
            
            if int(str_res['showapi_res_code']) != 0:
                return str_res['showapi_res_error']


            today = str_res.get('showapi_res_body',{}).get('day')
            ans = '今日运势：' + today['time']
            ans += '\n爱情运势：' + today['love_txt']
            ans += '\n工作运势：' + today['work_txt']
            ans += '\n财富运势：' + today['money_txt']
            #ans += '\n运势简评：' + today['general_txt']
            ans += '\n幸运数字：' + today['lucky_num']
            ans += '\n今日提醒：' + today['day_notice']
            return ans

    #joke 获取
    def get_joke(self):

        #随机一个joke
        rand_page = random.randint(1,100)

        url="http://route.showapi.com/341-1"
        send_data = parse.urlencode([
            ('showapi_appid', self.showapi_appid)
            ,('showapi_sign', self.showapi_sign)
                            ,('time', "")
                            ,('page', str(rand_page))
                            ,('maxResult', "1")
             
          ])


        req = request.Request(url)
        with request.urlopen(req, data=send_data.encode('utf-8')) as f:
            str_res= f.read().decode('utf-8')
            #str_res = self.replace_html(str_res)
            str_res = json.loads(str_res)

            if int(str_res['showapi_res_code']) != 0:
                return str_res['showapi_res_error']

            return self.replace_html(str_res['showapi_res_body']['contentlist'][0]['text'])


    #图灵
    def get_tuling(self, msg, userid):
        url="http://route.showapi.com/60-27"
        send_data = parse.urlencode([
            ('showapi_appid', self.showapi_appid)
            ,('showapi_sign', self.showapi_sign)
                            ,('info', msg)
                            ,('userid', 'myself')
             
          ])
         
        req = request.Request(url)
        with request.urlopen(req, data=send_data.encode('utf-8')) as f:
            str_res= f.read().decode('utf-8')
            str_res = json.loads(str_res)
            if int(str_res['showapi_res_code']) != 0:
                return str_res['showapi_res_error']

            return str_res['showapi_res_body']['text']

if __name__ == '__main__':
    zodic = Zodic()
    print (zodic.get_joke())


















