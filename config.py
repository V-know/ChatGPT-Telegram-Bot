from telegram import ReplyKeyboardMarkup
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

fh = logging.FileHandler('main.log')

formatter = logging.Formatter('%(message)s')
fh.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(fh)

token = {0: 256, 1: 1024, 2: 1024}
context_count = {0: 3, 1: 5, 2: 10}
rate_limit = {0: 5, 1: 15, 2: 300}

CHOOSING, TYPING_REPLY, TYPING_SYS_CONTENT = range(3)
contact_admin = "🆘求助"
start_button = "🚀Start"
set_sys_content_button = "🆔自定义角色"
reset_context_button = "🔃重开会话"
statistics_button = "📈用量查询"
switch_role_button = "🙋多角色切换"
reply_keyboard = [
    [contact_admin, start_button],
    [set_sys_content_button, switch_role_button],
    [reset_context_button, statistics_button],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

