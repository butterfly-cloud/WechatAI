#coding=utf8
from wxpy import *

class Robot(object):
    def __init__(self):
        self.bot = Bot()

        @bot.register(Friend, TEXT)
        def wr_msg(msg):
            return '我现在正忙，看到消息会第一时间回复'