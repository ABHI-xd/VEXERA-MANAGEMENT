import importlib
import random
import time
import re

from sys import argv
from typing import Optional

from  import (
    ALLOW_EXCL,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    TOKEN,
    URL,
    WEBHOOK,
    SUPPORT_CHAT,UPDATES_CHANNEL,
    dispatcher,
    StartTime,
    telethn,
    updater)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from VEXERA.modules import ALL_MODULES
from VEXERA.modules.helper_funcs.chat_status import is_user_admin
from VEXERA.modules.helper_funcs.misc import paginate_modules
from VEXERA.modules.disable import DisableAbleCommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown



def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """
𝑯𝒆𝒍𝒍𝒐 𝒔𝒊𝒓/𝒎𝒂'𝒂𝒎 , 𝑰'𝒎 𝑽𝑬𝑿𝑬𝑹𝑨....
`𝙸 𝙰𝙼 𝙰 𝙽𝙴𝚇𝚃 𝙶𝙴𝙽𝙴𝚁𝙰𝚃𝙸𝙾𝙽 𝙿𝙾𝚆𝙴𝚁𝙵𝚄𝙻 𝙼𝙰𝙽𝙰𝙶𝙴𝙼𝙴𝙽𝚃 𝙱𝙾𝚃!`\n\n𝙷𝙸𝚃 /vexera 𝚃𝙾 𝙼𝚈 𝙵𝙸𝙽𝙳 𝙰𝙻𝙻 𝙰𝚅𝙰𝙸𝙻𝙰𝙱𝙻𝙴 𝙲𝙾𝙼𝙼𝙰𝙽𝙳𝚂
 𝙰 𝚂𝙸𝙼𝙿𝙻𝙴 𝙼𝙰𝙽𝙰𝙶𝙴𝙼𝙴𝙽𝚃 𝙱𝙾𝚃 𝙱𝚈 @KAMINAxd
"""

buttons = [
    [
        InlineKeyboardButton(
            text="★𝙶𝚁𝙾𝚄𝙿 𝙼𝙴 𝙳𝙰𝙻𝙳𝙾★", url="t.me/VEXERA_ROBOT?startgroup=true"),
    ],
    [
        InlineKeyboardButton(text="★ʀᴇᴘᴏꜱɪᴛᴏʀʏ★", url=f"https://t.me/SNEHABHI_UPDATES"),
        InlineKeyboardButton(
            text="★𝚅𝙴𝚇𝙴𝚁𝙰 𝚂𝚄𝙿𝙿𝙾𝚁𝚃★", url=f"https://t.me/SNEHABHI_SERVER"
        ),
    ],
    [
        InlineKeyboardButton(text="★ᴄʜᴀɴɴᴇʟ★", url=f"https://t.me/SUKOON_MATLAB_TUM"),
        InlineKeyboardButton(
            text="★ᴍᴀꜱᴛɪ ɢʀᴏᴜᴘ★", url=f"https://t.me/LIVE_LIFE_LIKE"
        ),
    ],
    [
        InlineKeyboardButton(text="★ɪɴɴᴏᴄᴇɴᴛ ᴏᴡɴᴇʀ★", url=f"https://t.me/KAMINAxd")],
    [
        InlineKeyboardButton(text="★𝙑𝙀𝙓𝙀𝙍𝘼 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎★", callback_data="help_back"),
    ],
]


HELP_STRINGS = """
`ʏᴏᴜ ᴄᴀɴ ᴄʜᴏᴏꜱᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ, ʙʏ ᴄʟɪᴄᴋɪɴɢ ᴀ ʙᴜᴛᴛᴏɴ..`
ᴀʟꜱᴏ ʏᴏᴜ ᴄᴀɴ ᴀꜱᴋ ᴀɴʏᴛʜɪɴɢ ɪɴ ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ [❤️](https://telegra.ph/file/cab6825dea9263d347831.jpg)"""



DONATE_STRING = "𝙽𝙾 𝙽𝙴𝙴𝙳 , 𝙸'𝙼 𝚁𝙸𝙲𝙷 😏😏😂"

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("TGNRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

