#coding=utf8
import sys
import requests, json
import logging

class TuLing(object):
    def __init__(self):
        self.key = '2783ae1ae8694822b4b7d19baeda93ae'
        self.url = 'http://www.tuling123.com/openapi/api'
        self.tl_open = True
        self.init_log()

    def init_log(self):
        infoHandler = logging.FileHandler('./logs/tuling.log', 'a')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
        infoHandler.setFormatter(formatter)

        self.infoLogger = logging.getLogger("infoLog")
        self.infoLogger.setLevel(logging.INFO)
        self.infoLogger.addHandler(infoHandler)

    def get_msg(self, msg, user_id=123):
        if self.tl_open is False:
            return u'聊天程序已关闭'

        #user_id = user.replace('@', '')[:30]
        body = {'key': self.key, 'info': msg.encode('utf8'), 'userid': user_id}
        r = requests.post(self.url, data=body)
        respond = json.loads(r.text)
        result = ''
        if respond['code'] == 100000:
            result = respond['text'].replace('<br>', '  ')
            result = result.replace(u'\xa0', u' ')
        elif respond['code'] == 200000:
            result = respond['url']
        elif respond['code'] == 302000:
            for k in respond['list']:
                result = result + u"【" + k['source'] + u"】 " +\
                    k['article'] + "\t" + k['detailurl'] + "\n"
        elif respond['code'] == 40001:
            self.infoLogger.warning(respond['text'])
            result = u'参数错误'
        elif respond['code'] == 40002:
            self.infoLogger.warning(respond['text'])
            result = u'请求内容info为空'
        elif respond['code'] == 40004:
            self.infoLogger.warning(respond['text'])
            result = u'当天请求次数已使用完'
        elif respond['code'] == 40007:
            self.infoLogger.warning(respond['text'])
            result = u'数据格式异常'
        else:
            self.infoLogger.warning('tuling msg no match')
            result = respond['text'].replace('<br>', '  ')
            result = result.replace(u'\xa0', u' ')

        return result

    def set_switch(self, status):
        if status is True:
            self.tl_open = True
            return u'启动聊天程序'

        if status is False:
            self.tl_open = False
            return u'关闭聊天程序'

    def get_switch(self):
        return self.tl_open


if __name__ == '__main__':
    a = TuLing()
    print (a.get_msg('test'))