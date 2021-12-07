import os
from pyrogram import Client, filters
from pyrogram.types import *

from VEXERA.conf import get_str_key
from VEXERA import pbot

REPO_TEXT = "**A POWERFUL BOT to Make Your Groups Secured and Organized ! \n\n↼ Øwñêr ⇀ : 『 [ABHI](t.me/KAMINAxd) 』\n╭──────────────\n┣─ » Python ~ 3.10.0\n┣─ » Update ~ Recently\n╰──────────────\n\n»»» @SNEHABHI_SERVER «««"
  
BUTTONS = InlineKeyboardMarkup(
      [[
        InlineKeyboardButton("⚡ ʀᴇᴘᴏꜱɪᴛᴏʀʏ🔥", url=f"https://T.ME/LIVE_LIFE_LIKE"),
        InlineKeyboardButton(" ᴊᴏɪɴ 💫", url=f"https://t.me/SUKOON_MATLAB_TUM"),
      ],[
        InlineKeyboardButton("ᴏᴡɴᴇʀ ❣️", url="https://t.me/KAMINAXD"),
        InlineKeyboardButton("ꜱᴜᴘᴘᴏʀᴛ ⚡", url="https://t.me/SNEHABHI_SERVER"),
      ],[
        InlineKeyboardButton("⚡ ᴜᴘᴅᴀᴛᴇꜱ ☑️", url="https://t.me/SNEHABHI_UPDATES"),
        InlineKeyboardButton("ᴅᴇᴠᴇʟᴏᴘᴇʀ ➡️", url="https://t.me/KAMINAxd"),
      ]]
    )
  
  
@pbot.on_message(filters.command(["repo"]))
async def repo(pbot, update):
    await update.reply_text(
        text=REPO_TEXT,
        reply_markup=BUTTONS,
        disable_web_page_preview=True,
        quote=True
    )
