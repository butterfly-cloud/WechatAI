#coding=utf8
from wxpy import *
sys.path.append("/Users/yixin/sunhao25/")
from zodic import Zodic
from processor.robot import Robot
import time

zodic = Zodic()

bot = Robot()
bot.memmber_func()
bot.general_func()
bot.group_func()
bot.threads()

#bot.test()
#bot = Bot()
#bot.enable_puid('./cache/admin_puid.pkl')

#admin = bot.get_admin()




#code_info = ['所有指令:','joke', 'music', 'wru', '星座：查看运势，例：摩羯']



embed()
