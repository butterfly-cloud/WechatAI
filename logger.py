import logging
from wxpy import WeChatLoggingHandler, Bot
import time

bot = Bot()

# 这是你现有的 Logger
logger = logging.getLogger(__name__)

# 初始化一个微信 Handler
wechat_handler = WeChatLoggingHandler(bot.self)
# 加到入现有的 Logger
logger.addHandler(wechat_handler)

#while 1:
logger.warning('new test')
    