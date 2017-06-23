#coding=utf8
from wxpy import *
from processor.zodic import Zodic
from processor.tuling import TuLing
from random import choice
import random
import linecache
import subprocess
import threading
import time, datetime
import config


class Robot(Bot):

    def __init__(self):
        Bot.__init__(self, True)
        self.enable_puid('./cache/admin_puid.pkl')
        self.admin = self.get_admin()
        self.zodic = Zodic()
        self.tuling = TuLing()

        #disturb state
        self.wr = False

        self.lunch = ['迦南', '7楼', '金地', '驴肉火烧']

        #open laugh file
        self.file_count = len(open('./files/laugh.txt','rU').readlines())

        #change to your group
        group_receiver = ensure_one(self.groups().search('满天星也是research'))
        self.logger = get_wechat_logger(group_receiver)

        #动态的数据不能再这里制定，不然值不会变，如random函数
        #好友指令
        #函数要分有参数和没参数的区别，不然无法调用传参

        #纯文本信息
        self.FRIEND_TEXT = {
                        'code':  "\n".join(config.USER_CODE),
                        'python': 'http://wiki.bdp.cc/pages/viewpage.action?pageId=22577867',
        }

        self.ADMIN_TEXT = {
                        'admin':  "\n".join(config.ADMIN_CODE),
        }


        #函数信息
        self.FUNC_CODE_NO_PARAM = {
                        'lunch': self.get_lunch,
                        'joke': self.get_joke,
                        #以下是admin指令
                        'wrk': self.set_wrk,
                        'wrg': self.set_wrg,
                        'll': self.all_lunch,
                        'st': self.get_status,
        }

        self.FUNC_CODE_PARAM = {
                        #msg
                        'logout': self.ai_logout,
        }

        
        self.FUNC_CODE_like = {
                            'lunch ': self.set_lunch,
        }

        self.GROUP_CODE_USER = {


        }

        #指令分为有参数，无参数，有参数like，无参数like
        self.friend_no_param = set(['lunch','joke', 'll'])
        self.friend_param = set([])

        self.admin_no_param = self.friend_no_param | set(['wrk','wrg','st'])
        self.admin_param = self.friend_param | set(['logout'])

        #需要正则判断的无参数的指令
        self.friend_no_param_like = set([])
        self.admin_no_param_like = self.friend_no_param_like | set(['lunch '])



    def get_admin(self):
        users = self.search(config.ADMIN_NAME)
        admin = None
        for v in users:
            if v.puid == config.ADMIN_PUID:
                admin = v
        return admin

    #将文字信息函数分离出来，这样可以通过指令集合来区分不同的人，避免拟合

    def get_status(self):
        ans = u'勿扰模式: ' + (u'开' if self.wr else u'关')
        ans += u'\n聊天程序: ' + (u'开' if self.tuling.get_switch() else u'关')
        return ans

    

    def all_lunch(self):
        return ", ".join(self.lunch)

    #设置lunch
    def get_lunch(self):
        return choice(self.lunch)


    def set_lunch(self, msg_rec):
        pre = 8
        if msg_rec.startswith('lunch = ') and isinstance(msg_rec[pre:], list) and list(msg_rec[pre:]) < 20:
            self.lunch = list(msg_rec[pre:])
            return '设置完成'

        if msg_rec.startswith('lunch + ') and len(msg_rec) < 20:
            self.lunch.append(msg_rec[pre:])
            return '添加成功'

        if msg_rec.startswith('lunct - ') and len(msg_rec) < 20:
            self.lunch.remove(msg_rec[pre:])
            return '删除成功'

    def get_joke(self):
        #勿扰
        if self.wr:
            return config.WR_MSG

        at_msg = random.randrange(1,self.file_count, 1)
        msg = linecache.getline('./files/laugh.txt', at_msg).strip()
        return msg

    def set_wrk(self):
        self.wr = True
        return '开启勿扰模式'

    def set_wrg(self):
        self.wr = False
        return '关闭勿扰模式'

    def ai_logout(self, msg):
        msg.reply_msg('AI logout')
        self.logout()

    def is_number(self, x):
        try:
            int(x)
            return True
        except:
            return False

    #文本信息，处理函数
    def friend_text_process(self, msg, tuling=True):

        msg_rec = msg.text

        #判断文本信息指令
        if self.FRIEND_TEXT.get(msg_rec) is not None:
            return self.FRIEND_TEXT.get(msg_rec)

        #星座信息
        if msg.text in self.zodic.stars.keys():
            return self.zodic.get_data(msg.text)


        if msg_rec in self.friend_no_param:
            return self.FUNC_CODE_NO_PARAM.get(msg_rec)()

        if tuling:
            #默认调用图灵AI
            return self.tuling.get_msg(msg.text, msg.sender.puid)

        
    def admin_text_process(self, msg, tuling=True):
        msg_rec = msg.text

        #判断文本信息指令
        if self.FRIEND_TEXT.get(msg_rec) is not None:
            return self.FRIEND_TEXT.get(msg_rec)

        if self.ADMIN_TEXT.get(msg_rec) is not None:
            return self.ADMIN_TEXT.get(msg_rec)

        #星座信息
        if msg.text in self.zodic.stars.keys():
            return self.zodic.get_data(msg.text)


        #判断是否是无参数指令
        if msg_rec in self.admin_no_param:
            return self.FUNC_CODE_NO_PARAM.get(msg_rec)()

        #判断是否是有参数指令
        if msg_rec in self.admin_param:
            return self.FUNC_CODE_PARAM.get(msg_rec)(msg)


        #判断是否是startwith指令
        ans = None
        for code in self.admin_no_param_like:
            if msg_rec.startswith(code):
                ans = self.FUNC_CODE_like[code](msg_rec)
                break

        if ans is not None:
            return ans

        #开关聊天程序
        if msg_rec in ['tlk','tlg']:
            return self.tuling.set_switch(True if msg_rec == 'tlk' else False)

        if tuling :
            #默认调用图灵
            return self.tuling.get_msg(msg.text, msg.sender.puid)

    #后注册的配置具有更高的优先级
    def memmber_func(self):

        @self.register(Friend, TEXT)
        def text_processor(msg):
            if msg.sender == self.admin:
                ans = self.admin_text_process(msg)
                if ans is not None:
                    return ans

            if self.wr:
                return config.WR_MSG
            else:
                return self.friend_text_process(msg)

    #基础功能
    def general_func(self):
        #自动通过好友认证
        @self.register(msg_types=FRIENDS)
        def auto_accept_friends(msg):
            # 判断好友请求中的验证文本
            if 'cloud' in msg.text.lower():
                # 接受好友 (msg.card 为该请求的用户对象)
                new_friend = self.accept_friend(msg.card)
                # 或 new_friend = msg.card.accept()
                # 向新的好友发送消息
                new_friend.send('我是@孙小号，输入code查看指令')


    def group_is_at(self, msg):
        #勿扰
        if self.wr:
            return config.WR_MSG

        return self.tuling.get_msg(msg.text[5:], msg.sender.puid)
        

    def group_func(self):
        
        mantianxing_group = ensure_one(self.groups().search('满天星也是research'))
        @self.register(mantianxing_group, TEXT)
        def test_group_at(msg):
            if msg.is_at:
                return self.group_is_at(msg)

            if self.wr:
                pass
            else:
                return self.friend_text_process(msg, False)
          
    #lunch warning
    def cron_lunch(self):
        while True:
            SECONDS_PER_DAY = 24 * 60 * 60
            curTime = datetime.datetime.now()
            desTime = curTime.replace(hour=12, minute=5, second=1, microsecond=0)
            delta = (desTime - curTime).total_seconds()
            skipSeconds = (SECONDS_PER_DAY + delta ) if delta < 0 else delta
            time.sleep(skipSeconds)
            self.logger.warning(choice(config.LUNCH_WARN))
         

    def threads(self):
        t_lunch = threading.Thread(target=self.cron_lunch)
        t_lunch.setDaemon(True)
        t_lunch.start()




                           


            






