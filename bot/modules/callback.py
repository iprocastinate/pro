from pyrogram.filters import command, private, user
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, CallbackQuery
from pyrogram.errors import FloodWait, MessageNotModified
from os import getenv
from random import choice
from pathlib import Path
from asyncio import sleep as asleep
from time import time

from bot import bot, bot_loop, Var, ani_cache, LOGS
from bot.core.database import db

async def about_cb(_, cb):
    me = await bot.get_me()
    username = me.username
    await cb.answer()
    text = f"<b><blockquote>✦ 𝗔𝗕𝗢𝗨𝗧 ✦</blockquote>\n──────────────────\n<blockquote>・ ʙᴏᴛ: <a href='https://t.me/{username}'>ᴀᴜᴛᴏ ᴘᴏʀɴ</a>\n・ ᴏᴡɴᴇʀ: <a href='https://t.me/Aporiatic'>ᴀᴘᴏʀɪᴀᴛɪᴄ</a>\n・ ᴅᴇᴠᴇʟᴏᴘᴇʀ: <a href='https://t.me/KamiKaito'>ᴋᴀᴍɪ ᴋᴀɪᴛᴏ</a>\n・ ʟᴀɴɢᴜᴀɢᴇ: <a href='https://python.org'>ᴘʏᴛʜᴏɴ</a>\n・ ᴅᴀᴛᴀʙᴀsᴇ: <a href='https://mongodb.com'>ᴍᴏɴɢᴏᴅʙ</a>\n・ ɴᴇᴛᴡᴏʀᴋ: <a href='https://t.me/Pervert_Boys'>ᴘᴇʀᴠᴇʀᴛ ʙᴏʏs</a></blockquote>\n──────────────────\n<blockquote>≡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: <a href='https://t.me/Mirage_Botz'>𝗠𝗜𝗥𝗔𝗚𝗘— 𝗕𝗢𝗧𝗭</a></blockquote></b>"
    
    btns = [
        [InlineKeyboardButton("✦ 𝗧𝗛𝗘 𝗚𝗥𝗘𝗔𝗧𝗘𝗦𝗧 ✦", url="https://telegram.me/KamiKaito")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="home_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        if Var.ABOUT_PHOTO:
            await cb.message.edit_media(
                media=InputMediaPhoto(Var.ABOUT_PHOTO, caption=text),
                reply_markup=markup
            )
        else:
            await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def help_cb(_, cb):
    await cb.answer()
    text = "<b><blockquote>✦ 𝗛𝗘𝗟𝗣 ✦</blockquote>\n──────────────────\n<blockquote>/start - sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ.\n/addtask - ᴀᴅᴅ ᴄᴜsᴛᴏᴍ ᴛᴀsᴋ.\n/pause - ᴘᴀᴜsᴇ ʀss ғᴇᴛᴄʜɪɴɢ.\n/resume - ʀᴇsᴜᴍᴇ ʀss ғᴇᴛᴄʜɪɴɢ.\n/settings - ᴏᴘᴇɴ sᴇᴛᴛɪɴɢs ᴍᴇɴᴜ.\n/restart - ʀᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ.</blockquote>\n──────────────────\n<blockquote>≡ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: <a href='https://t.me/Mirage_Botz'>𝗠𝗜𝗥𝗔𝗚𝗘— 𝗕𝗢𝗧𝗭</a></blockquote></b>"
    
    btns = [
        [InlineKeyboardButton("✦ 𝗧𝗛𝗘 𝗚𝗥𝗘𝗔𝗧𝗘𝗦𝗧 ✦", url="https://telegram.me/KamiKaito")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="home_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        if Var.HELP_PHOTO:
            await cb.message.edit_media(
                media=InputMediaPhoto(Var.HELP_PHOTO, caption=text),
                reply_markup=markup
            )
        else:
            await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def back_cb(_, cb):
    await cb.answer()
    await cb.message.delete()

async def home_cb(_, cb):
    await cb.answer()
    from_user = cb.from_user
    smsg = Var.START_MSG.format(first_name=from_user.first_name,
                                last_name=from_user.last_name,
                                mention=from_user.mention, 
                                user_id=from_user.id)
    btns = [
        [InlineKeyboardButton("✦ 𝗧𝗛𝗘 𝗚𝗥𝗘𝗔𝗧𝗘𝗦𝗧 ✦", url="https://telegram.me/KamiKaito")],
        [InlineKeyboardButton("✦ 𝗔𝗕𝗢𝗨𝗧​", callback_data="about_cb"),
         InlineKeyboardButton("𝗛𝗘𝗟𝗣 ✦", callback_data="help_cb")]
    ]
    
    try:
        if Var.START_PHOTO:
            await cb.message.edit_media(
                media=InputMediaPhoto(Var.START_PHOTO, caption=smsg),
                reply_markup=InlineKeyboardMarkup(btns)
            )
        else:
            await cb.message.edit_text(smsg, reply_markup=InlineKeyboardMarkup(btns))
    except MessageNotModified:
        pass

async def close_cb(_, cb):
    await cb.answer()
    await cb.message.delete()

async def settings_cb(_, cb):
    await cb.answer()
    text = "<b><blockquote>✦ 𝗕𝗢𝗧 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ✦</b></blockquote>"
    btns = [
        [InlineKeyboardButton("✦ 𝗕𝗢𝗧 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦", callback_data="bot_settings_cb")],
        [InlineKeyboardButton("✦ 𝗖𝗢𝗡𝗧𝗘𝗡𝗧 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦", callback_data="content_settings_cb"),
        InlineKeyboardButton("𝗨𝗦𝗘𝗥 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ✦", callback_data="user_settings_cb")],
        [InlineKeyboardButton("✦ 𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        if hasattr(Var, 'SETTINGS_PHOTO') and Var.SETTINGS_PHOTO:
            await cb.message.edit_media(
                media=InputMediaPhoto(Var.SETTINGS_PHOTO, caption=text),
                reply_markup=markup
            )
        else:
            await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def user_settings_cb(_, cb):
    await cb.answer()
    text = "<b><blockquote>✦ 𝗨𝗦𝗘𝗥 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ✦</blockquote></b>"
    btns = [
        [InlineKeyboardButton("✦ 𝗔𝗗𝗗 𝗪𝗛𝗜𝗧𝗟𝗜𝗦𝗧", callback_data="add_whitelist_cb"),
        InlineKeyboardButton("𝗥𝗘𝗠𝗢𝗩𝗘 𝗪𝗛𝗜𝗧𝗟𝗜𝗦𝗧", callback_data="remove_whitelist_cb"),
        InlineKeyboardButton("𝗟𝗜𝗦𝗧 𝗪𝗛𝗜𝗧𝗟𝗜𝗦𝗧 ✦", callback_data="list_whitelist_cb")],        
        [InlineKeyboardButton("✦ 𝗔𝗗𝗗 𝗔𝗗𝗠𝗜𝗡", callback_data="add_admin_cb"),
        InlineKeyboardButton("𝗥𝗘𝗠𝗢𝗩𝗘 𝗔𝗗𝗠𝗜𝗡", callback_data="remove_admin_cb"),
        InlineKeyboardButton("𝗟𝗜𝗦𝗧 𝗔𝗗𝗠𝗜𝗡 ✦", callback_data="list_admin_cb")],
        [InlineKeyboardButton("✦ 𝗔𝗗𝗗 𝗕𝗔𝗡", callback_data="add_ban_cb"),
        InlineKeyboardButton("𝗥𝗘𝗠𝗢𝗩𝗘 𝗕𝗔𝗡", callback_data="remove_ban_cb"),
        InlineKeyboardButton("𝗟𝗜𝗦𝗧 𝗕𝗔𝗡 ✦", callback_data="list_ban_cb")],        
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def add_whitelist_cb(_, cb):
    uid = cb.from_user.id
    
    current_time = time()
    if uid in ani_cache['whitelist_cooldown']:
        last_use = ani_cache['whitelist_cooldown'][uid]
        time_left = 60 - (current_time - last_use)
        if time_left > 0:
            return await cb.answer(f"ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ {int(time_left)} sᴇᴄᴏɴᴅs ʙᴇғᴏʀᴇ ᴜsɪɴɢ ᴡʜɪᴛᴇʟɪsᴛ ᴀɢᴀɪɴ!", show_alert=True)
    
    ani_cache['whitelist_cooldown'][uid] = current_time
    
    await cb.answer()
    text = "<b><blockquote>✦ 𝗔𝗗𝗗 𝗨𝗦𝗘𝗥 𝗧𝗢 𝗪𝗛𝗜𝗧𝗘𝗟𝗜𝗦𝗧 ✦</blockquote>\n──────────────────\n<blockquote>• ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ ᴜsᴇʀ ɪᴅ ᴛᴏ ᴀᴅᴅ ᴛʜᴇᴍ:\n• ᴇxᴀᴍᴘʟᴇ: 123456789</blockquote>\n──────────────────\n<blockquote>✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: <a href='https://t.me/Mirage_Botz'>𝗠𝗜𝗥𝗔𝗚𝗘— 𝗕𝗢𝗧𝗭</a></blockquote></b>"

    try:
        await cb.message.edit_text(text)
    except MessageNotModified:
        pass
    
    ani_cache['pending_action'] = {'action': 'add_whitelist', 'user_id': cb.from_user.id}

async def remove_whitelist_cb(_, cb):
    uid = cb.from_user.id
    
    current_time = time()
    if uid in ani_cache['whitelist_cooldown']:
        last_use = ani_cache['whitelist_cooldown'][uid]
        time_left = 60 - (current_time - last_use)
        if time_left > 0:
            return await cb.answer(f"ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ {int(time_left)} sᴇᴄᴏɴᴅs ʙᴇғᴏʀᴇ ᴜsɪɴɢ ᴡʜɪᴛᴇʟɪsᴛ ᴀɢᴀɪɴ!", show_alert=True)
    
    ani_cache['whitelist_cooldown'][uid] = current_time
    
    await cb.answer()
    text = "<b><blockquote>✦ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗨𝗦𝗘𝗥 𝗙𝗥𝗢𝗠 𝗪𝗛𝗜𝗧𝗘𝗟𝗜𝗦𝗧 ✦</blockquote>\n──────────────────\n<blockquote>• ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ ᴜsᴇʀ ɪᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴛʜᴇᴍ:\n• ᴇxᴀᴍᴘʟᴇ: 123456789</blockquote>\n──────────────────\n<blockquote>✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: <a href='https://t.me/Mirage_Botz'>𝗠𝗜𝗥𝗔𝗚𝗘— 𝗕𝗢𝗧𝗭</a></blockquote></b>"
    
    try:
        await cb.message.edit_text(text)
    except MessageNotModified:
        pass
    
    ani_cache['pending_action'] = {'action': 'remove_whitelist', 'user_id': cb.from_user.id}

async def list_whitelist_cb(_, cb):
    await cb.answer()
    from bot.core.database import db
    
    try:
        whitelisted_users = await db.get_all_whitelisted()
        
        if whitelisted_users:
            users_list = "\n".join([f"• <code>{uid}</code>" for uid in whitelisted_users])
            text = f"<b><blockquote>✦ 𝗪𝗛𝗜𝗧𝗘𝗟𝗜𝗦𝗧𝗘𝗗 𝗨𝗦𝗘𝗥𝗦 ({len(whitelisted_users)}) ✦</blockquote>\n<blockquote>{users_list}</blockquote></b>"
        else:
            text = "<b><blockquote>✦ 𝗪𝗛𝗜𝗧𝗘𝗟𝗜𝗦𝗧𝗘𝗗 𝗨𝗦𝗘𝗥𝗦 ✦</blockquote>\n\n<blockquote>• ɴᴏ ᴜsᴇʀs ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ʏᴇᴛ.</blockquote></b>"
        
        btns = [
            [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="user_settings_cb"),
             InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
        ]
        markup = InlineKeyboardMarkup(btns)
        
        try:
            await cb.message.edit_text(text, reply_markup=markup)
        except MessageNotModified:
            pass
    except Exception as e:
        LOGS.error(f"Error listing whitelist: {str(e)}")
        await cb.answer("Error fetching whitelist", show_alert=True)



async def bot_settings_cb(_, cb):
    await cb.answer()
    text = "<b><blockquote>✦ 𝗕𝗢𝗧 𝗠𝗢𝗗𝗘 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ✦</blockquote>"
    btns = [
        [InlineKeyboardButton("✦ 𝗕𝗢𝗧 𝗨𝗦𝗔𝗚𝗘 𝗠𝗢𝗗𝗘 ✦", callback_data="bot_mode_cb")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        if hasattr(Var, 'BOT_SETTINGS_PHOTO') and Var.BOT_SETTINGS_PHOTO:
            await cb.message.edit_media(
                media=InputMediaPhoto(Var.BOT_SETTINGS_PHOTO, caption=text),
                reply_markup=markup
            )
        else:
            await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def bot_mode_cb(_, cb):
    await cb.answer()
    current_mode = ani_cache.get('BOT_MODE', 'default')
    text = f"<b><blockquote>✦ 𝗕𝗢𝗧 𝗨𝗦𝗔𝗚𝗘 𝗠𝗢𝗗𝗘 ✦</blockquote>\n<blockquote>𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗠𝗢𝗗𝗘: {current_mode.upper()}</b></blockquote>"
    btns = [
        [InlineKeyboardButton("✦ 𝗪𝗛𝗜𝗧𝗘𝗟𝗜𝗦𝗧", callback_data="white_mode_set_cb"),
         InlineKeyboardButton("𝗗𝗘𝗙𝗔𝗨𝗟𝗧 ✦", callback_data="default_mode_set_cb")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="bot_settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def white_mode_set_cb(_, cb):
    await cb.answer('ᴡʜɪᴛᴇʟɪsᴛ ᴍᴏᴅᴇ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ.', show_alert=True)
    ani_cache['BOT_MODE'] = 'whitelist'
    await db.update_bot_mode('whitelist')
    text = "<b><blockquote>✦ 𝗕𝗢𝗧 𝗨𝗦𝗔𝗚𝗘 𝗠𝗢𝗗𝗘 ✦</blockquote>\n<blockquote>𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗠𝗢𝗗𝗘: 𝗪𝗛𝗜𝗧𝗘𝗟𝗜𝗦𝗧</b></blockquote>"
    btns = [
        [InlineKeyboardButton("✦ 𝗪𝗛𝗜𝗧𝗘𝗟𝗜𝗦𝗧", callback_data="white_mode_set_cb"),
         InlineKeyboardButton("𝗗𝗘𝗙𝗔𝗨𝗟𝗧 ✦", callback_data="default_mode_set_cb")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="bot_settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def default_mode_set_cb(_, cb):
    await cb.answer('ᴅᴇғᴀᴜʟᴛ ᴍᴏᴅᴇ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ.', show_alert=True)
    ani_cache['BOT_MODE'] = 'default'
    await db.update_bot_mode('default')
    text = "<b><blockquote>✦ 𝗕𝗢𝗧 𝗨𝗦𝗔𝗚𝗘 𝗠𝗢𝗗𝗘 ✦</blockquote>\n<blockquote>𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗠𝗢𝗗𝗘: 𝗗𝗘𝗙𝗔𝗨𝗟𝗧</b></blockquote>"
    btns = [
        [InlineKeyboardButton("✦ 𝗪𝗛𝗜𝗧𝗘𝗟𝗜𝗦𝗧", callback_data="white_mode_set_cb"),
         InlineKeyboardButton("𝗗𝗘𝗙𝗔𝗨𝗟𝗧 ✦", callback_data="default_mode_set_cb")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="bot_settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def content_settings_cb(_, cb):
    await cb.answer()
    text = "<b><blockquote>✦ 𝗖𝗢𝗡𝗧𝗘𝗡𝗧 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ✦</blockquote>"
    btns = [
        [InlineKeyboardButton("✦ 𝗙𝗢𝗡𝗧 𝗖𝗛𝗔𝗡𝗚𝗘𝗥", callback_data="font_changer_cb"),
        InlineKeyboardButton("𝗔𝗨𝗧𝗢 𝗨𝗣𝗟𝗢𝗔𝗗 ✦", callback_data="auto_upload_settings_cb")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def font_changer_cb(_, cb):
    await cb.answer()
    font_changer_status = ani_cache.get('FONT_CHANGER', False)
    status_text = "𝗢𝗡" if font_changer_status else "𝗢𝗙𝗙"
    text = f"<b><blockquote>✦ 𝗙𝗢𝗡𝗧 𝗖𝗛𝗔𝗡𝗚𝗘𝗥 ✦</blockquote>\n<blockquote>𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗦𝗧𝗔𝗧𝗨𝗦: {status_text}</blockquote></b>"
    
    btns = [
        [InlineKeyboardButton("✦ 𝗢𝗡", callback_data="font_changer_on_cb"),
         InlineKeyboardButton("𝗢𝗙𝗙 ✦", callback_data="font_changer_off_cb")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="content_settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def font_changer_on_cb(_, cb):
    await cb.answer('ғᴏɴᴛ ᴄʜᴀɴɢᴇʀ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ.', show_alert=True)
    ani_cache['FONT_CHANGER'] = True
    await db.update_font_changer(True)
    
    text = "<b><blockquote>✦ 𝗙𝗢𝗡𝗧 𝗖𝗛𝗔𝗡𝗚𝗘𝗥 ✦</blockquote>\n<blockquote>𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗢𝗡</blockquote></b>"
    
    btns = [
        [InlineKeyboardButton("✦ 𝗢𝗡", callback_data="font_changer_on_cb"),
         InlineKeyboardButton("𝗢𝗙𝗙 ✦", callback_data="font_changer_off_cb")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="content_settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def font_changer_off_cb(_, cb):
    await cb.answer('ғᴏɴᴛ ᴄʜᴀɴɢᴇʀ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.', show_alert=True)
    ani_cache['FONT_CHANGER'] = False
    await db.update_font_changer(False)
    
    text = "<b><blockquote>✦ 𝗙𝗢𝗡𝗧 𝗖𝗛𝗔𝗡𝗚𝗘𝗥 ✦</blockquote>\n<blockquote>𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗦𝗧𝗔𝗧𝗨𝗦: 𝗢𝗙𝗙</blockquote></b>"
    
    btns = [
        [InlineKeyboardButton("✦ 𝗢𝗡", callback_data="font_changer_on_cb"),
         InlineKeyboardButton("𝗢𝗙𝗙 ✦", callback_data="font_changer_off_cb")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="content_settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def auto_upload_settings_cb(_, cb):
    await cb.answer()
    
    enabled = ani_cache.get('AUTO_UPLOAD_ENABLED', False)
    day_limit = ani_cache.get('UPLOAD_DAY_LIMIT', 1)
    upload_time = ani_cache.get('UPLOAD_TIME', '12:00')
    uploads_today = ani_cache.get('UPLOADS_TODAY', 0)
    status = "𝗘𝗡𝗔𝗕𝗟𝗘𝗗" if enabled else "𝗗𝗜𝗦𝗔𝗕𝗟𝗘𝗗"
    
    text = f"<b><blockquote>✦ 𝗔𝗨𝗧𝗢 𝗨𝗣𝗟𝗢𝗔𝗗 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ✦</blockquote>\n──────────────────\n<blockquote>✦ 𝗦𝗧𝗔𝗧𝗨𝗦: {status}\n✦ 𝗗𝗔𝗜𝗟𝗬 𝗟𝗜𝗠𝗜𝗧: {day_limit}\n✦ 𝗨𝗣𝗟𝗢𝗔𝗗𝗘𝗗 𝗧𝗢𝗗𝗔𝗬: {uploads_today}\n✦ 𝗨𝗣𝗟𝗢𝗔𝗗 𝗧𝗜𝗠𝗘: {upload_time}</blockquote>\n──────────────────</b>"
    
    btns = [
        [InlineKeyboardButton("✦ 𝗦𝗘𝗧 𝗗𝗔𝗬 𝗟𝗜𝗠𝗜𝗧", callback_data="set_day_upload_cb"),
         InlineKeyboardButton("𝗦𝗘𝗧 𝗨𝗣𝗟𝗢𝗔𝗗 𝗧𝗜𝗠𝗘 ✦", callback_data="set_upload_time_cb")],
        [InlineKeyboardButton("✦ 𝗦𝗘𝗧 𝗔𝗨𝗧𝗢 𝗨𝗣𝗟𝗢𝗔𝗗 ✦", callback_data="set_auto_upload_cb")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="content_settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def set_day_upload_cb(_, cb):
    uid = cb.from_user.id
    
    await cb.answer()
    text = "<b><blockquote>✦ 𝗦𝗘𝗧 𝗗𝗔𝗜𝗟𝗬 𝗨𝗣𝗟𝗢𝗔𝗗 𝗟𝗜𝗠𝗜𝗧 ✦</blockquote>\n──────────────────\n<blockquote>• ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ ɴᴜᴍʙᴇʀ ᴏғ ᴜᴘʟᴏᴀᴅs ᴘᴇʀ ᴅᴀʏ:\n• ᴇxᴀᴍᴘʟᴇ: 2 ᴏʀ 3 ᴏʀ 5</blockquote>\n──────────────────\n<blockquote>✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: <a href='https://t.me/Mirage_Botz'>𝗠𝗜𝗥𝗔𝗚𝗘— 𝗕𝗢𝗧𝗭</a></blockquote></b>"

    try:
        await cb.message.edit_text(text)
    except MessageNotModified:
        pass
    
    ani_cache['pending_action'] = {'action': 'set_day_upload', 'user_id': cb.from_user.id}

async def set_upload_time_cb(_, cb):
    uid = cb.from_user.id
    
    await cb.answer()
    text = "<b><blockquote>✦ 𝗦𝗘𝗧 𝗨𝗣𝗟𝗢𝗔𝗗 𝗧𝗜𝗠𝗘 ✦</blockquote>\n──────────────────\n<blockquote>• ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛɪᴍᴇ ɪɴ:\n• 12ʜʀ ғᴏʀᴍᴀᴛ: 02:30 PM ᴏʀ 12:00 AM\n• 24ʜʀ ғᴏʀᴍᴀᴛ: 14:30 ᴏʀ 00:00</blockquote>\n──────────────────\n<blockquote>✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: <a href='https://t.me/Mirage_Botz'>𝗠𝗜𝗥𝗔𝗚𝗘— 𝗕𝗢𝗧𝗭</a></blockquote></b>"

    try:
        await cb.message.edit_text(text)
    except MessageNotModified:
        pass
    
    ani_cache['pending_action'] = {'action': 'set_upload_time', 'user_id': cb.from_user.id}

async def set_auto_upload_cb(_, cb):
    
    await cb.answer()
    
    enabled = ani_cache.get('AUTO_UPLOAD_ENABLED', False)
    status = "𝗘𝗡𝗔𝗕𝗟𝗘𝗗" if enabled else "𝗗𝗜𝗦𝗔𝗕𝗟𝗘𝗗"
    
    text = f"<b><blockquote>✦ 𝗔𝗨𝗧𝗢 𝗨𝗣𝗟𝗢𝗔𝗗 𝗦𝗧𝗔𝗧𝗨𝗦 ✦</blockquote>\n<blockquote>𝗖𝗨𝗥𝗥𝗘𝗡𝗧 𝗦𝗧𝗔𝗧𝗘: {status}</blockquote></b>"
    
    btns = [
        [InlineKeyboardButton("✦ 𝗢𝗡", callback_data="auto_upload_on_cb"),
         InlineKeyboardButton("𝗢𝗙𝗙 ✦", callback_data="auto_upload_off_cb")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="auto_upload_settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def auto_upload_on_cb(_, cb):
    uid = cb.from_user.id
    
    await cb.answer('ᴀᴜᴛᴏ ᴜᴘʟᴏᴀᴅ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ.', show_alert=True)
    ani_cache['AUTO_UPLOAD_ENABLED'] = True
    await db.set_auto_upload_enabled(True)
    
    text = "<b><blockquote>✦ 𝗔𝗨𝗧𝗢 𝗨𝗣𝗟𝗢𝗔𝗗 𝗦𝗧𝗔𝗧𝗨𝗦 ✦</blockquote>\n<blockquote>✦ 𝗦𝗧𝗔𝗧𝗘: 𝗘𝗡𝗔𝗕𝗟𝗘𝗗</blockquote></b>"
    
    btns = [
        [InlineKeyboardButton("✦ 𝗘𝗡𝗔𝗕𝗟𝗘𝗗", callback_data="auto_upload_on_cb"),
         InlineKeyboardButton("𝗗𝗜𝗦𝗔𝗕𝗟𝗘 ✦", callback_data="auto_upload_off_cb")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="auto_upload_settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def auto_upload_off_cb(_, cb):
    uid = cb.from_user.id
   
    await cb.answer('ᴀᴜᴛᴏ ᴜᴘʟᴏᴀᴅ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.', show_alert=True)
    ani_cache['AUTO_UPLOAD_ENABLED'] = False
    await db.set_auto_upload_enabled(False)
    ani_cache['UPLOADS_TODAY'] = 0
    await db.reset_daily_uploads()
    
    text = "<b><blockquote>✦ 𝗔𝗨𝗧𝗢 𝗨𝗣𝗟𝗢𝗔𝗗 𝗦𝗧𝗔𝗧𝗨𝗦 ✦</blockquote>\n<blockquote>✦ 𝗦𝗧𝗔𝗧𝗘: 𝗗𝗜𝗦𝗔𝗕𝗟𝗘𝗗</blockquote></b>"
    
    btns = [
        [InlineKeyboardButton("✦ 𝗘𝗡𝗔𝗕𝗟𝗘", callback_data="auto_upload_on_cb"),
         InlineKeyboardButton("𝗗𝗜𝗦𝗔𝗕𝗟𝗘𝗗 ✦", callback_data="auto_upload_off_cb")],
        [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="auto_upload_settings_cb"),
         InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    markup = InlineKeyboardMarkup(btns)
    
    try:
        await cb.message.edit_text(text, reply_markup=markup)
    except MessageNotModified:
        pass

async def add_admin_cb(_, cb):
    uid = cb.from_user.id
    
    if uid != Var.OWNER:
        await cb.answer("ᴏɴʟʏ ᴏᴡɴᴇʀ!", show_alert=True)
        return
    
    await cb.answer()
    text = "<b><blockquote>✦ 𝗔𝗗𝗗 𝗔𝗗𝗠𝗜𝗡 ✦</blockquote>\n──────────────────\n<blockquote>• ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ ᴜsᴇʀ ɪᴅ ᴛᴏ ᴀᴅᴅ ᴛʜᴇᴍ:\n• ᴇxᴀᴍᴘʟᴇ: 123456789</blockquote>\n──────────────────\n<blockquote>✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: <a href='https://t.me/Mirage_Botz'>𝗠𝗜𝗥𝗔𝗚𝗘— 𝗕𝗢𝗧𝗭</a></blockquote></b>"

    try:
        await cb.message.edit_text(text)
    except MessageNotModified:
        pass
    
    ani_cache['pending_action'] = {'action': 'add_admin', 'user_id': cb.from_user.id}

async def remove_admin_cb(_, cb):
    uid = cb.from_user.id
    
    if uid != Var.OWNER:
        await cb.answer("ᴏɴʟʏ ᴏᴡɴᴇʀ!", show_alert=True)
        return
    
    await cb.answer()
    text = "<b><blockquote>✦ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗔𝗗𝗠𝗜𝗡 ✦</blockquote>\n──────────────────\n<blockquote>• ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ ᴜsᴇʀ ɪᴅ ᴛᴏ ʀᴇᴍᴏᴠᴇ ᴛʜᴇᴍ:\n• ᴇxᴀᴍᴘʟᴇ: 123456789</blockquote>\n──────────────────\n<blockquote>✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: <a href='https://t.me/Mirage_Botz'>𝗠𝗜𝗥𝗔𝗚𝗘— 𝗕𝗢𝗧𝗭</a></blockquote></b>"
    
    try:
        await cb.message.edit_text(text)
    except MessageNotModified:
        pass
    
    ani_cache['pending_action'] = {'action': 'remove_admin', 'user_id': cb.from_user.id}

async def list_admin_cb(_, cb):
    uid = cb.from_user.id
    
    await cb.answer()
    try:
        admin_list = await db.get_all_admins()
        
        if admin_list:
            admins_text = "\n".join([f"• <code>{aid}</code>" for aid in admin_list])
            text = f"<b><blockquote>✦ 𝗔𝗗𝗠𝗜𝗡 𝗟𝗜𝗦𝗧 ({len(admin_list)}) ✦</blockquote>\n<blockquote>{admins_text}</blockquote></b>"
        else:
            text = "<b><blockquote>✦ 𝗔𝗗𝗠𝗜𝗡 𝗟𝗜𝗦𝗧 ✦</blockquote>\n\n<blockquote>• ɴᴏ ᴀᴅᴍɪɴs ᴀʏᴇᴛ.</blockquote></b>"
        
        btns = [
            [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="user_settings_cb"),
             InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
        ]
        markup = InlineKeyboardMarkup(btns)
        
        try:
            await cb.message.edit_text(text, reply_markup=markup)
        except MessageNotModified:
            pass
    except Exception as e:
        LOGS.error(f"Error listing admins: {str(e)}")
        await cb.answer("Error fetching admin list", show_alert=True)

async def add_ban_cb(_, cb):
    uid = cb.from_user.id
    
    await cb.answer()
    text = "<b><blockquote>✦ 𝗔𝗗𝗗 𝗕𝗔𝗡 ✦</blockquote>\n──────────────────\n<blockquote>• ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ ᴜsᴇʀ ɪᴅ ᴛᴏ ʙᴀɴ ᴛʜᴇᴍ:\n• ᴇxᴀᴍᴘʟᴇ: 123456789</blockquote>\n──────────────────\n<blockquote>✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: <a href='https://t.me/Mirage_Botz'>𝗠𝗜𝗥𝗔𝗚𝗘— 𝗕𝗢𝗧𝗭</a></blockquote></b>"

    try:
        await cb.message.edit_text(text)
    except MessageNotModified:
        pass
    
    ani_cache['pending_action'] = {'action': 'add_ban', 'user_id': cb.from_user.id}

async def remove_ban_cb(_, cb):
    uid = cb.from_user.id
    
    await cb.answer()
    text = "<b><blockquote>✦ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗕𝗔𝗡 ✦</blockquote>\n──────────────────\n<blockquote>• ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ ᴜsᴇʀ ɪᴅ ᴛᴏ ᴜɴʙᴀɴ ᴛʜᴇᴍ:\n• ᴇxᴀᴍᴘʟᴇ: 123456789</blockquote>\n──────────────────\n<blockquote>✦ ᴘᴏᴡᴇʀᴇᴅ ʙʏ: <a href='https://t.me/Mirage_Botz'>𝗠𝗜𝗥𝗔𝗚𝗘— 𝗕𝗢𝗧𝗭</a></blockquote></b>"
    
    try:
        await cb.message.edit_text(text)
    except MessageNotModified:
        pass
    
    ani_cache['pending_action'] = {'action': 'remove_ban', 'user_id': cb.from_user.id}

async def list_ban_cb(_, cb):
    uid = cb.from_user.id
    
    await cb.answer()
    try:
        ban_list = await db.get_all_bans()
        
        if ban_list:
            bans_text = "\n".join([f"• <code>{bid}</code>" for bid in ban_list])
            text = f"<b><blockquote>✦ 𝗕𝗔𝗡 𝗟𝗜𝗦𝗧 ({len(ban_list)}) ✦</blockquote>\n<blockquote>{bans_text}</blockquote></b>"
        else:
            text = "<b><blockquote>✦ 𝗕𝗔𝗡 𝗟𝗜𝗦𝗧 ✦</blockquote>\n\n<blockquote>• ɴᴏ ʙᴀɴɴᴇᴅ ᴜsᴇʀs ʏᴇᴛ.</blockquote></b>"
        
        btns = [
            [InlineKeyboardButton("✦ 𝗕𝗔𝗖𝗞", callback_data="user_settings_cb"),
             InlineKeyboardButton("𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
        ]
        markup = InlineKeyboardMarkup(btns)
        
        try:
            await cb.message.edit_text(text, reply_markup=markup)
        except MessageNotModified:
            pass
    except Exception as e:
        LOGS.error(f"Error listing bans: {str(e)}")
        await cb.answer("Error fetching ban list", show_alert=True)

def load_insults():
    try:
        insult_file = Path(__file__).parent.parent / "INSULT_LANG.txt"
        if not insult_file.exists():
            return {'english': [], 'hindi': [], 'spam': []}
        
        insults = {'english': [], 'hindi': [], 'spam': []}
        current_lang = None
        
        with open(insult_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line == "English:":
                    current_lang = 'english'
                elif line == "Hindi:":
                    current_lang = 'hindi'
                elif line == "Spam:":
                    current_lang = 'spam'
                elif line and current_lang:
                    insults[current_lang].append(line)
        
        return insults
    except Exception as e:
        LOGS.error(f"Error loading insults: {str(e)}")
        return {'english': [], 'hindi': [], 'spam': []}

INSULTS = load_insults()

@bot.on_callback_query()
async def handle_callbacks(client, cb):
    data = cb.data
    uid = cb.from_user.id
    
    # Check if user is admin/owner for sensitive operations
    sensitive_operations = [
        "bot_settings_cb", "bot_mode_cb", "white_mode_set_cb", "default_mode_set_cb",
        "auto_upload_settings_cb", "set_day_upload_cb", "set_upload_time_cb", "set_auto_upload_cb",
        "auto_upload_on_cb", "auto_upload_off_cb", "user_settings_cb",
        "add_whitelist_cb", "remove_whitelist_cb", "list_whitelist_cb",
        "add_admin_cb", "remove_admin_cb", "list_admin_cb",
        "add_ban_cb", "remove_ban_cb", "list_ban_cb"
    ]
    
    if data in sensitive_operations:
        if uid != Var.OWNER and uid not in Var.ADMINS:
            await cb.answer('✦ ᴏɴʟʏ ᴀᴅᴍɪɴs/ᴏᴡɴᴇʀ ᴄᴀɴ ᴀᴄᴄᴇss ᴛʜɪs ✦', show_alert=True)
            return
    
    if data == "about_cb":
        await about_cb(client, cb)
    elif data == "help_cb":
        await help_cb(client, cb)
    elif data == "home_cb":
        await home_cb(client, cb)
    elif data == "close_cb":
        await close_cb(client, cb)
    elif data == "settings_cb":
        await settings_cb(client, cb)
    elif data == "bot_settings_cb":
        await bot_settings_cb(client, cb)
    elif data == "bot_mode_cb":
        await bot_mode_cb(client, cb)
    elif data == "white_mode_set_cb":
        await white_mode_set_cb(client, cb)
    elif data == "default_mode_set_cb":
        await default_mode_set_cb(client, cb)
    elif data == "content_settings_cb":
        await content_settings_cb(client, cb)
    elif data == "font_changer_cb":
        await font_changer_cb(client, cb)
    elif data == "font_changer_on_cb":
        await font_changer_on_cb(client, cb)
    elif data == "font_changer_off_cb":
        await font_changer_off_cb(client, cb)
    elif data == "auto_upload_settings_cb":
        await auto_upload_settings_cb(client, cb)
    elif data == "set_day_upload_cb":
        await set_day_upload_cb(client, cb)
    elif data == "set_upload_time_cb":
        await set_upload_time_cb(client, cb)
    elif data == "set_auto_upload_cb":
        await set_auto_upload_cb(client, cb)
    elif data == "auto_upload_on_cb":
        await auto_upload_on_cb(client, cb)
    elif data == "auto_upload_off_cb":
        await auto_upload_off_cb(client, cb)
    elif data == "user_settings_cb":
        await user_settings_cb(client, cb)
    elif data == "add_whitelist_cb":
        await add_whitelist_cb(client, cb)
    elif data == "remove_whitelist_cb":
        await remove_whitelist_cb(client, cb)
    elif data == "list_whitelist_cb":
        await list_whitelist_cb(client, cb)
    elif data == "add_admin_cb":
        await add_admin_cb(client, cb)
    elif data == "remove_admin_cb":
        await remove_admin_cb(client, cb)
    elif data == "list_admin_cb":
        await list_admin_cb(client, cb)
    elif data == "add_ban_cb":
        await add_ban_cb(client, cb)
    elif data == "remove_ban_cb":
        await remove_ban_cb(client, cb)
    elif data == "list_ban_cb":
        await list_ban_cb(client, cb)
    elif data.startswith("insult_lang_"):
        try:
            parts = data.split('_')
            language = parts[2]
            user_id = int(parts[3])
            
            insults = load_insults()
            
            if language not in insults or not insults[language]:
                await cb.answer("No insults available for this language", show_alert=True)
                return
            
            await cb.answer()
            await cb.message.delete()
            
            language_insults = insults[language]
            LOGS.info(f"Sending 50 insults to non-whitelisted user {user_id} in {language}")
            
            for i in range(50):
                if language_insults:
                    insult = choice(language_insults)
                    try:
                        await client.send_message(user_id, f"<b>{insult}</b>")
                        await asleep(0.5)
                    except FloodWait as e:
                        LOGS.warning(f"FloodWait for user {user_id}, waiting {e.value} seconds")
                        await asleep(e.value)
                        await client.send_message(user_id, f"<b>{insult}</b>")
                    except Exception as e:
                        LOGS.error(f"Error sending insult {i+1}/50: {str(e)}")
            
            LOGS.info(f"Successfully sent 50 insults to non-whitelisted user {user_id}: {language}")
            username = (await client.get_users(user_id)).username
            LOGS.info(f"User details - ID: {user_id}, Username: @{username if username else 'N/A'}")
            await rep.report(f"Non-whitelisted user {user_id} ({username if username else 'N/A'}) received 50 insults in language {language}", "critical")

            
        except Exception as e:
            LOGS.error(f"Error handling insult callback: {str(e)}")
            await cb.answer("Error processing request", show_alert=True)

