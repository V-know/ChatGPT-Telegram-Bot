from telegram import ReplyKeyboardMarkup
import logging
import yaml

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

# Load data from config.yaml file
with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
time_span = config["TIME_SPAN"]
token = config["MAX_TOKEN"]
context_count = config["CONTEXT_COUNT"]
rate_limit = config["RATE_LIMIT"]
notification_channel = config.get("NOTIFICATION_CHANNEL")

CHOOSING, TYPING_REPLY, TYPING_SYS_CONTENT = range(3)
contact_admin = "🆘Help"
start_button = "🚀Start"
set_sys_content_button = "🆔Customize Role"
reset_context_button = "🔃Restart Session"
statistics_button = "📈Statistics"
switch_role_button = "🙋Switch Roles"
language_button = "🔤Language"
reply_keyboard = [
    [language_button, contact_admin, start_button],
    [set_sys_content_button, switch_role_button],
    [reset_context_button, statistics_button],
]
reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

cancel_button = "🚫Cancel"
cancel_keyboard = [[cancel_button]]
cancel_markup = ReplyKeyboardMarkup(cancel_keyboard, one_time_keyboard=True)
