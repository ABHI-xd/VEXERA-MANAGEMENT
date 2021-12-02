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
ʜᴏɪ, ɪ ᴍ ᴛɢɴ ʀᴏʙᴏᴛ
`ɪ'ᴍ ʜᴇʀᴇ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘꜱ ᴀɴᴅ ɪ ᴍ ᴠᴇʀʏ ᴘᴏᴡᴇʀꜰᴜʟʟ ʙᴏᴛ! ʜɪᴛ` /help
 [❤](https://telegra.ph/file/cab6825dea9263d347831.jpg)
"""

buttons = [
    [
        InlineKeyboardButton(
            text="ᴀᴅᴅ ᴛɢɴ ʀᴏʙᴏᴛ ᴛᴏ ᴜʀ ᴄʜᴀᴛ", url="t.me/TGN_Ro_bot?startgroup=true"),
    ],
    [
        InlineKeyboardButton(text="ꜱᴏᴜʀᴄᴇ 💫", url=f"https://github.com/Itsunknown-12/TGN-Robot"),
        InlineKeyboardButton(
            text="ꜱᴜᴘᴘᴏʀᴛ ⚡", url=f"https://t.me/{SUPPORT_CHAT}"
        ),
    ],
    [
        InlineKeyboardButton(text="ᴜᴘᴅᴀᴛᴇꜱ ☑️", url=f"https://t.me/The_Godfather_Network"),
        InlineKeyboardButton(
            text="ᴛɢɴ ᴄʜᴀᴛ", url=f"https://t.me/greatpersonxd"
        ),
    ],
    [
        InlineKeyboardButton(text="ʜᴇʟᴘ ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅꜱ", callback_data="help_back"),
    ],
]


HELP_STRINGS = """
`ʏᴏᴜ ᴄᴀɴ ᴄʜᴏᴏꜱᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ, ʙʏ ᴄʟɪᴄᴋɪɴɢ ᴀ ʙᴜᴛᴛᴏɴ..`
ᴀʟꜱᴏ ʏᴏᴜ ᴄᴀɴ ᴀꜱᴋ ᴀɴʏᴛʜɪɴɢ ɪɴ ꜱᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ [❤️](https://telegra.ph/file/cab6825dea9263d347831.jpg)"""

START_IMG = "https://telegra.ph/file/63d1ee18f81c92d11210e.mp4"

DONATE_STRING = """Heya, glad to hear you want to donate!
 You can support the project [Lucifer](t.me/detctective_de) \
 Supporting isnt always financial! [ ɴᴇᴛᴡᴏʀᴋ](https://t.me/Zaid_updates) \
 Those who cannot provide monetary support are welcome to help us develop the bot at ."""

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

