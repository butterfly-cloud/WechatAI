#coding=utf8
from wxpy import *
#sys.path.append("/Users/yixin/sunhao25/")
from zodic import Zodic
from processor.tuling import TuLing
from random import choice
import random
import linecache
import subprocess
import threading
import time, datetime


class Robot(Bot):

    def __init__(self):
        Bot.__init__(self, True)
        self.enable_puid('./cache/admin_puid.pkl')
        self.admin = self.get_admin()
        self.zodic = Zodic()
        self.tuling = TuLing()

        self.user_code = ['所有指令:','joke', 'python: wiki 主页','music', '星座：查看运势，例：摩羯', 'lunch', 'll: lunch list']
        self.admin_code = ['管理员指令:', 'st: status','勿扰: wrk 开 | wrg 关', 'lunch = [xx,xx]', 'lunch + xx', 'lunch - xx',\
                            'logout','limit plat id','tlk | tkg : 开启/关闭聊天程序']
        #勿扰状态
        self.wr = False

        self.lunch = ['迦南', '7楼', '金地', '驴肉火烧']

        #open laugh file
        self.file_count = len(open('./files/laugh.txt','rU').readlines())

        self.wr_msg = '我现在正忙，看到消息会第一时间回复'

        group_receiver = ensure_one(self.groups().search('满天星也是research'))
        #group_receiver = ensure_one(self.groups().search('冰岛'))
        self.logger = get_wechat_logger(group_receiver)

        #动态的数据不能再这里制定，不然值不会变，如random函数
        #好友指令
        #函数要分有参数和没参数的区别，不然无法调用传参

        #纯文本信息
        self.FRIEND_TEXT = {
                        'code':  "\n".join(self.user_code),
                        'python': 'http://wiki.bdp.cc/pages/viewpage.action?pageId=22577867',
        }

        self.ADMIN_TEXT = {
                        'admin':  "\n".join(self.admin_code),
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
        users = self.search('克劳德')
        admin = None
        for v in users:
            if v.puid == '6af65e45':
                admin = v
        return admin

    #将文字信息函数分离出来，这样可以通过指令集合来区分不同的人，避免拟合
    #def general_code(self):
    #    return "\n".join(self.user_code)

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
            return self.wr_msg

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


    #检查是否是额度测试代码
    def check_limit_code(self, msg):
        arr = msg.text.split(' ')
        plats = set(['amazon','ebay','wish','lazada'])
        if len(arr) != 3 or arr[0] != 'limit' or arr[1] not in plats or self.is_number(arr[2]) == False:
            return None
        else:
            msg.reply_msg('running...')
            code,ans = subprocess.getstatusoutput('/usr/bin/python /Users/yixin/sunhao25/std_miner/testwm.py '+arr[1]+' '+str(arr[2]))
            return ans

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
            #默认调用图灵
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

        #是否是测试额度代码
        ans = self.check_limit_code(msg)
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
                return self.wr_msg
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
                new_friend.send('我是孙小号，输入code查看指令')


    def group_is_at(self, msg):
        #勿扰
        if self.wr:
            return self.wr_msg

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
        
        test_group = ensure_one(self.groups().search('冰岛'))
        @self.register(test_group, TEXT)
        def test_group_at(msg):
            if msg.is_at:
                return self.group_is_at(msg)

            if msg.member == self.admin:
                ans = self.admin_text_process(msg, False)
                if ans is not None:
                    return ans

            if self.wr:
                pass
            elif '孙小号' in msg.text :
                joke_replay = [
                    '祥参又要下班了',
                    '🐻才今天带午饭了么',
                    '泰青，房价又涨了！',
                    '兰总：一毛一样',
                    'amazon 预估又有问题了',
                ]
                return choice(joke_replay) if random.randint(1,10) == 1 else None
            else:
                return self.friend_text_process(msg, False)
        
          
    #定时吃饭
    def cron_lunch(self):
        while True:
            SECONDS_PER_DAY = 24 * 60 * 60
            curTime = datetime.datetime.now()
            desTime = curTime.replace(hour=12, minute=0, second=0, microsecond=0)
            delta = (desTime - curTime).total_seconds()
            skipSeconds = (SECONDS_PER_DAY + delta ) if delta < 0 else delta
            time.sleep(skipSeconds)
            self.logger.warning(choice(['民以食为天，你还不吃饭','到点啦，该吃午饭啦', '🍚🍚🍚']))
         

    def threads(self):
        t_lunch = threading.Thread(target=self.cron_lunch)
        t_lunch.setDaemon(True)
        t_lunch.start()




                           


            






