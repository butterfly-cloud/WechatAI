#coding=utf8
from wxpy import *
#sys.path.append("/Users/yixin/sunhao25/")
from zodic import Zodic
from random import choice
import random
import linecache
import subprocess
import threading
import time

class Robot(Bot):

    def __init__(self):
        Bot.__init__(self, True)
        self.enable_puid('./cache/admin_puid.pkl')
        self.admin = self.get_admin()
        self.zodic = Zodic()
        self.user_code = ['所有指令:','joke', 'python: wiki 主页','music', 'wru', '星座：查看运势，例：摩羯', 'lunch', 'll: lunch list']
        self.admin_code = ['管理员指令:', 'st: status','勿扰: wrk 开 | wrg 关', 'lunch = [xx,xx]', 'lunch + xx', 'lunch - xx','logout','limit plat id']
        self.wr = False

        self.lunch = ['迦南', '7楼', '金地', '711']

        #open laugh file
        self.file_count = len(open('./files/laugh.txt','rU').readlines())

        self.wr_msg = '我现在正忙，看到消息会第一时间回复'

        group_receiver = ensure_one(self.groups().search('冰岛'))
        self.logger = get_wechat_logger(group_receiver)

        #动态的数据不能再这里制定，不然值不会变，如random函数
        #好友指令
        #函数要分有参数和没参数的区别，不然无法调用传参

        #纯文本信息
        self.FRIEND_TEXT = {
                        'code':  "\n".join(self.user_code),
                        'wru': '我是一个AI，我的父亲是克劳德，我刚刚被开发出来，功能还不完善',
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
                        'logout': self.logout,
                        'll': self.all_lunch,
                        'st': self.get_status,
        }

        self.FUNC_CODE_PARAM = {
                        #msg
                        'logout': self.logout,
        }

        
        self.FUNC_CODE_like = {
                            'lunch ': self.set_lunch,
        }

        self.GROUP_CODE_USER = {


        }

        #指令分为有参数，无参数，有参数like，无参数like
        self.friend_no_param = set(['lunch','joke', 'll'])
        self.friend_param = set([])

        self.admin_no_param = self.friend_no_param | set(['wrk','wrg','status'])
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
        ans = '勿扰模式: ' + '开' if self.wr else '关'

    

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
        return self.zodic.get_joke()

    def set_wrk(self):
        self.wr = True
        return '开启勿扰模式'

    def set_wrg(self):
        self.wr = False
        return '关闭勿扰模式'

    def logout(self, msg):
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
    def friend_text_process(self, msg):

        msg_rec = msg.text

        """
        if msg.text.lower() == 'code':
            return "\n".join(self.user_code)

        if msg.text.lower() == 'wru':
            return '我是一个AI，我的父亲是克劳德，我刚刚被开发出来，功能还不完善'

        if msg.text.lower() == 'lunch':
            return choice(self.lunch)

        if msg.text.lower() == 'll':
            return ", ".join(self.lunch)


        if msg.text in self.zodic.stars.keys():
            return self.zodic.get_data(msg.text)

        if msg_rec.startswith('lunch = ') and isinstance(msg_rec[10:], list) and list(msg_rec[10:]) < 20:
            self.lunch = list(msg_rec[10:])
            return '设置完成'

        if msg_rec.startswith('lunch + ') and len(msg_rec) < 20:
            self.lunch.append(msg_rec[10:])
            return '设置完成'

        if msg_rec.startswith('lunct - ') and len(msg_rec) < 20:
            self.lunch.remove(msg_rec[10:])
            return '设置完成'

        if msg.text.lower() == 'joke':
            return self.zodic.get_joke()
        """

        #判断文本信息指令
        if self.FRIEND_TEXT.get(msg_rec) is not None:
            return self.FRIEND_TEXT.get(msg_rec)

        #星座信息
        if msg.text in self.zodic.stars.keys():
            return self.zodic.get_data(msg.text)


        if msg_rec in self.friend_no_param:
            return self.FUNC_CODE_NO_PARAM.get(msg_rec)()


        #默认调用图灵
        return self.zodic.get_tuling(msg.text, 'test')

        
    def admin_text_process(self, msg):
        msg_rec = msg.text

        """
        if msg.text.lower() == 'admin':
            return "\n".join(self.admin_code)

        #开启勿扰模式
        if msg.text.lower() == 'wrk':
            self.wr = True
            return '开启勿扰模式'

        #关闭勿扰模式
        if msg.text.lower() == 'wrg':
            self.wr = False
            return '关闭勿扰模式'

        if msg.text == 'logout':
            msg.reply_msg('AI logout')
            self.logout() 

        


        return self.code_to_info_user(msg)
        """

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

        #默认调用图灵
        return self.zodic.get_tuling(msg.text, 'test')

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
                new_friend = bot.accept_friend(msg.card)
                # 或 new_friend = msg.card.accept()
                # 向新的好友发送消息
                new_friend.send('你好，我们现在可以愉快地聊天啦')


    def group_is_at(self, msg):
        #勿扰
        if self.wr:
            return self.wr_msg

        at_msg = random.randrange(1,self.file_count, 1)
        msg = linecache.getline('./files/laugh.txt', at_msg).strip()
        return msg

    """
    def group_msg(self, msg):
        return self.code_to_info_user(msg)
    """

    def group_func(self):
        test_group = ensure_one(self.groups().search('冰岛'))

        @self.register(test_group)
        def test_group_at(msg):
            if msg.is_at:
                return self.group_is_at(msg)

            if msg.member == self.admin:
                ans = self.admin_text_process(msg)
                if ans is not None:
                    return ans

            if self.wr:
                pass
            else:
                return self.friend_text_process(msg)

          
    #定时吃饭
    def cron_lunch(self):
        while True:
            self.logger.warning('该吃饭了!!!')
            time.sleep(10)


    def threads(self):
        t_lunch = threading.Thread(target=self.cron_lunch)
        t_lunch.setDaemon(True)
        t_lunch.start()




                           


            






