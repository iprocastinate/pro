from asyncio import sleep as asleep, gather
from time import time
from pyrogram.filters import command, private, user
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, MessageNotModified
from urllib.parse import parse_qs, urlparse
from random import randint
from re import findall, sub

from bot import bot, bot_loop, Var, ani_cache, LOGS
from bot.core.database import db
from bot.core.func_utils import decode, is_fsubbed, get_fsubs, editMessage, sendMessage, new_task, convertTime, getfeed
from bot.core.rss_fetcher import get_rss
from bot.core.reporter import rep



@bot.on_message(command('start') & private)
@new_task
async def start_msg(client, message):
    uid = message.from_user.id
    from_user = message.from_user
    txtargs = message.text.split()
    
    if 'BOT_MODE' not in ani_cache:
        ani_cache['BOT_MODE'] = 'default'
    if 'INSULT_WARNINGS' not in ani_cache:
        ani_cache['INSULT_WARNINGS'] = {}
    
    if ani_cache['BOT_MODE'] == 'whitelist' and uid not in Var.ADMINS and uid not in Var.OWNER:
        is_whitelisted = await db.is_whitelisted(uid)
        if not is_whitelisted:
            if uid not in ani_cache['INSULT_WARNINGS']:
                ani_cache['INSULT_WARNINGS'][uid] = True
                return await sendMessage(message, f"<b><blockquote>You dare touch me without my master's permission? Know your place you little piece of shit!</blockquote></b>")
            else:
                btns = [
                    [InlineKeyboardButton("𝗘𝗡𝗚𝗟𝗜𝗦𝗛", callback_data=f"insult_lang_english_{uid}"),
                     InlineKeyboardButton("𝗛𝗜𝗡𝗗𝗜", callback_data=f"insult_lang_hindi_{uid}")]
                ]
                return await sendMessage(message, "<b><blockquote>sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴘʀᴇғᴇʀᴀʙʟᴇ ʟᴀɴɢᴜᴀɢᴇ:</blockquote></b>", InlineKeyboardMarkup(btns))
    
    temp = await sendMessage(message, "<b><blockquote>ᴘʀᴏᴄᴇssɪɴɢ ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ...<blockquote></b>")
    if not await is_fsubbed(uid):
        txt, btns = await get_fsubs(uid, txtargs)
        return await editMessage(temp, txt, InlineKeyboardMarkup(btns))
    if len(txtargs) <= 1:
        await temp.delete()
        btns = [
            [InlineKeyboardButton("✦ 𝗔𝗕𝗢𝗨𝗧​", callback_data="about_cb"),
             InlineKeyboardButton("𝗛𝗘𝗟𝗣 ✦", callback_data="help_cb")],
            [InlineKeyboardButton("✦ 𝗧𝗛𝗘 𝗚𝗥𝗘𝗔𝗧𝗘𝗦𝗧 ✦", url="https://telegram.me/KamiKaito")]
        ]
        smsg = Var.START_MSG.format(first_name=from_user.first_name,
                                    last_name=from_user.first_name,
                                    mention=from_user.mention, 
                                    user_id=from_user.id)
        if Var.START_PHOTO:
            await message.reply_photo(
                photo=Var.START_PHOTO, 
                caption=smsg,
                reply_markup=InlineKeyboardMarkup(btns) if len(btns) != 0 else None
            )
        else:
            await sendMessage(message, smsg, InlineKeyboardMarkup(btns) if len(btns) != 0 else None)
        return
    try:
        arg = (await decode(txtargs[1])).split('-')
    except Exception as e:
        await rep.report(f"User : {uid} | Error : {str(e)}", "error")
        await editMessage(temp, "<b>Input Link Code Decode Failed !</b>")
        return
    
    if arg[0] != 'get':
        await editMessage(temp, "<b>Input Link is Invalid for Usage !</b>")
        return
    
    if len(arg) == 3:
        try:
            first_fid = int(int(arg[1]) / abs(int(Var.FILE_STORE)))
            last_fid = int(int(arg[2]) / abs(int(Var.FILE_STORE)))
        except Exception as e:
            await rep.report(f"User : {uid} | Batch Decode Error : {str(e)}", "error")
            await editMessage(temp, "<b>Input Link Code Decode Failed !</b>")
            return
        
        try:
            await temp.delete()
            sent_count = 0
            msg_ids = list(range(first_fid, last_fid + 1))
            
            for msg_id in msg_ids:
                try:
                    msg = await client.get_messages(Var.FILE_STORE, message_ids=msg_id)
                    if msg and not msg.empty:
                        nmsg = await msg.copy(message.chat.id, reply_markup=None)
                        sent_count += 1
                        await asleep(0.5)
                except Exception as e:
                    LOGS.debug(f"Failed to get message {msg_id}: {str(e)}")
                    continue
            
            if sent_count > 0:
                LOGS.debug(message, f'Downloaded {sent_count} files')
                if Var.AUTO_DEL:
                    async def auto_del_batch(msgs_to_del):
                        await asleep(Var.DEL_TIMER)
                        try:
                            await client.delete_messages(message.chat.id, message_ids=msgs_to_del)
                        except:
                            pass
                    await sendMessage(message, f'<i>Files will be Auto Deleted in {convertTime(Var.DEL_TIMER)}, Forward to Saved Messages Now..</i>')
            else:
                await editMessage(temp, "<b>No Files Found in Range !</b>")
        except Exception as e:
            await rep.report(f"User : {uid} | Batch Error : {str(e)}", "error")
            await editMessage(temp, "<b>Error Downloading Batch Files !</b>")
    
    elif len(arg) == 2:
        try:
            fid = int(int(arg[1]) / abs(int(Var.FILE_STORE)))
        except Exception as e:
            await rep.report(f"User : {uid} | Error : {str(e)}", "error")
            await editMessage(temp, "<b>Input Link Code is Invalid !</b>")
            return
        try:
            msg = await client.get_messages(Var.FILE_STORE, message_ids=fid)
            if msg.empty:
                return await editMessage(temp, "<b>File Not Found !</b>")
            nmsg = await msg.copy(message.chat.id, reply_markup=None)
            await temp.delete()
            if Var.AUTO_DEL:
                async def auto_del(msg, timer):
                    await asleep(timer)
                    await msg.delete()
                await sendMessage(message, f'<i>File will be Auto Deleted in {convertTime(Var.DEL_TIMER)}, Forward to Saved Messages Now..</i>')
                bot_loop.create_task(auto_del(nmsg, Var.DEL_TIMER))
        except Exception as e:
            await rep.report(f"User : {uid} | Error : {str(e)}", "error")
            await editMessage(temp, "<b>File Not Found !</b>")
    else:
        await editMessage(temp, "<b>Input Link is Invalid for Usage !</b>")
    
@bot.on_message(command('pause') & private & user([Var.OWNER] + Var.ADMINS))
async def pause_fetch(client, message):
    ani_cache['fetch_rss'] = False
    await sendMessage(message, "<b><blockquote>ʀss ғᴇᴛᴄʜɪɴɢ ʜᴀs ʙᴇᴇɴ sᴛᴏᴘᴘᴇᴅ.</blockquote></b>")

@bot.on_message(command('resume') & private & user([Var.OWNER] + Var.ADMINS))
async def resume_fetch(client, message):
    ani_cache['fetch_rss'] = True
    await sendMessage(message, "<b><blockquote>ʀss ғᴇᴛᴄʜɪɴɢ ʜᴀs ʙᴇᴇɴ sᴛᴀʀᴛᴇᴅ.</blockquote></b>")

@bot.on_message(command('settings') & private & user([Var.OWNER] + Var.ADMINS))
@new_task
async def settings_cmd(client, message):
    text = "<b><blockquote>✦ 𝗕𝗢𝗧 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ✦</b></blockquote>"
    btns = [
        [InlineKeyboardButton("✦ 𝗕𝗢𝗧 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦", callback_data="bot_settings_cb")],
        [InlineKeyboardButton("✦ 𝗖𝗢𝗡𝗧𝗘𝗡𝗧 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦", callback_data="content_settings_cb"),
        InlineKeyboardButton("𝗨𝗦𝗘𝗥 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ✦", callback_data="user_settings_cb")],
        [InlineKeyboardButton("✦ 𝗖𝗟𝗢𝗦𝗘 ✦", callback_data="close_cb")]
    ]
    await sendMessage(message, text, InlineKeyboardMarkup(btns))

@bot.on_message(private & user([Var.OWNER] + Var.ADMINS) & ~command(['start', 'pause', 'resume', 'settings', 'addtask', 'restart']))
async def handle_whitelist_input(client, message):
    try:
        if message.text and message.text.startswith('/'):
            return
        
        pending = ani_cache.get('pending_action')
        if not pending or pending.get('user_id') != message.from_user.id:
            return
        
        action = pending.get('action')
        
        if action == 'set_window_start_time':
            try:
                time_input = message.text.strip()
                time_parts = time_input.split(':')
                if len(time_parts) != 2:
                    raise ValueError("Invalid time format")
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    raise ValueError("Invalid hour or minute")
                formatted_time = f"{hour:02d}:{minute:02d}"
                
                ani_cache['UPLOAD_START_TIME'] = formatted_time
                await db.set_upload_time_window(
                    ani_cache.get('UPLOAD_TIME_WINDOW_ENABLED', False),
                    formatted_time,
                    ani_cache.get('UPLOAD_STOP_TIME', '23:59')
                )
                await sendMessage(message, f"<b><blockquote>ᴜʟᴏᴀᴅ ᴡɪɴᴅᴏᴡ sᴛᴀʀᴛ ᴛɪᴍᴇ sᴇᴛ ᴛᴏ {formatted_time}!</blockquote></b>")
                LOGS.info(f"Upload window start time set to {formatted_time} by {message.from_user.id}")
            except ValueError as ve:
                await sendMessage(message, f"<b><blockquote>ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ғᴏʀᴍᴀᴛ: {str(ve)}\nᴜsᴇ 24ʜʀ ғᴏʀᴍᴀᴛ (ᴇ.ɢ., 08:00)</blockquote></b>")
            except Exception as e:
                LOGS.error(f"Error setting window start time: {str(e)}")
                await sendMessage(message, f"<b><blockquote>ᴇʀʀᴏʀ: {str(e)}</blockquote></b>")
            ani_cache['pending_action'] = None
            return
        
        if action == 'set_window_stop_time':
            try:
                time_input = message.text.strip()
                time_parts = time_input.split(':')
                if len(time_parts) != 2:
                    raise ValueError("Invalid time format")
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                    raise ValueError("Invalid hour or minute")
                formatted_time = f"{hour:02d}:{minute:02d}"
                
                ani_cache['UPLOAD_STOP_TIME'] = formatted_time
                await db.set_upload_time_window(
                    ani_cache.get('UPLOAD_TIME_WINDOW_ENABLED', False),
                    ani_cache.get('UPLOAD_START_TIME', '00:00'),
                    formatted_time
                )
                await sendMessage(message, f"<b><blockquote>ᴜʟᴏᴀᴅ ᴡɪɴᴅᴏᴡ sᴛᴏᴘ ᴛɪᴍᴇ sᴇᴛ ᴛᴏ {formatted_time}!</blockquote></b>")
                LOGS.info(f"Upload window stop time set to {formatted_time} by {message.from_user.id}")
            except ValueError as ve:
                await sendMessage(message, f"<b><blockquote>ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ғᴏʀᴍᴀᴛ: {str(ve)}\nᴜsᴇ 24ʜʀ ғᴏʀᴍᴀᴛ (ᴇ.ɢ., 23:59)</blockquote></b>")
            except Exception as e:
                LOGS.error(f"Error setting window stop time: {str(e)}")
                await sendMessage(message, f"<b><blockquote>ᴇʀʀᴏʀ: {str(e)}</blockquote></b>")
            ani_cache['pending_action'] = None
            return
        
        if action == 'set_upload_time':
            try:
                time_input = message.text.strip().upper()
                
                if 'AM' in time_input or 'PM' in time_input:
                    time_str = time_input.replace('AM', '').replace('PM', '').strip()
                    is_pm = 'PM' in time_input
                    time_parts = time_str.split(':')
                    if len(time_parts) != 2:
                        raise ValueError("Invalid time format")
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    if hour < 1 or hour > 12 or minute < 0 or minute > 59:
                        raise ValueError("Invalid hour or minute")
                    if is_pm and hour != 12:
                        hour += 12
                    elif not is_pm and hour == 12:
                        hour = 0
                    formatted_time = f"{hour:02d}:{minute:02d}"
                else:
                    time_parts = time_input.split(':')
                    if len(time_parts) != 2:
                        raise ValueError("Invalid time format")
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                        raise ValueError("Invalid hour or minute")
                    formatted_time = f"{hour:02d}:{minute:02d}"
                
                ani_cache['UPLOAD_TIME'] = formatted_time
                await db.set_upload_time(formatted_time)
                ani_cache['UPLOADS_TODAY'] = 0
                await db.reset_daily_uploads()
                await sendMessage(message, f"<b><blockquote>ᴜᴘʟᴏᴀᴅ ᴛɪᴍᴇ sᴇᴛ ᴛᴏ {formatted_time}!</blockquote></b>")
                LOGS.info(f"Upload time set to {formatted_time} by {message.from_user.id}")
            except ValueError as ve:
                await sendMessage(message, f"<b><blockquote>ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ғᴏʀᴍᴀᴛ: {str(ve)}</blockquote></b>")
            except Exception as e:
                LOGS.error(f"Error setting upload time: {str(e)}")
                await sendMessage(message, f"<b><blockquote>ᴇʀʀᴏʀ:</blockquote></b> {str(e)}")
            ani_cache['pending_action'] = None
            return
        
        try:
            user_id = int(message.text.strip())
        except ValueError:
            return await sendMessage(message, "<b><blockquote>ɪɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ. ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!</blockquote></b>")
        
        if action == 'add_whitelist':
            try:
                success = await db.add_to_whitelist(user_id)
                if success:
                    await sendMessage(message, f"<b><blockquote>ᴜsᴇʀ {user_id} ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ᴡʜɪᴛᴇʟɪsᴛ!</blockquote></b>")
                    LOGS.info(f"User {user_id} added to whitelist by {message.from_user.id}")
                else:
                    await sendMessage(message, f"<b><blockquote>ᴜsᴇʀ {user_id} ᴀʟʀᴇᴀᴅʏ ɪɴ ᴡʜɪᴛᴇʟɪsᴛ.</blockquote></b>")
            except Exception as e:
                LOGS.error(f"Error adding to whitelist: {str(e)}")
                await sendMessage(message, f"<b><blockquote>ᴇʀʀᴏʀ:</blockquote></b> {str(e)}")
        
        elif action == 'remove_whitelist':
            try:
                success = await db.remove_from_whitelist(user_id)
                if success:
                    await sendMessage(message, f"<b><blockquote>ᴜsᴇʀ {user_id} ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴡʜɪᴛᴇʟɪsᴛ!</blockquote></b>")
                    LOGS.info(f"User {user_id} removed from whitelist by {message.from_user.id}")
                else:
                    await sendMessage(message, f"<b><blockquote>ᴜsᴇʀ {user_id} ɪs ɴᴏᴛ ɪɴ ᴡʜɪᴛᴇʟɪsᴛ.</blockquote></b>")
            except Exception as e:
                LOGS.error(f"Error removing from whitelist: {str(e)}")
                await sendMessage(message, f"<b><blockquote>ᴇʀʀᴏʀ:</blockquote></b> {str(e)}")
        
        elif action == 'add_admin':
            try:
                success = await db.add_admin(user_id)
                if success:
                    await sendMessage(message, f"<b><blockquote>ᴜsᴇʀ {user_id} ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴀs ᴀᴅᴍɪɴ!</blockquote></b>")
                    LOGS.info(f"User {user_id} added as admin by {message.from_user.id}")
                else:
                    await sendMessage(message, f"<b><blockquote>ᴜsᴇʀ {user_id} ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ.</blockquote></b>")
            except Exception as e:
                LOGS.error(f"Error adding admin: {str(e)}")
                await sendMessage(message, f"<b><blockquote>ᴇʀʀᴏʀ:</blockquote></b> {str(e)}")
        
        elif action == 'remove_admin':
            try:
                success = await db.remove_admin(user_id)
                if success:
                    await sendMessage(message, f"<b><blockquote>ᴜsᴇʀ {user_id} ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴀᴅᴍɪɴs!</blockquote></b>")
                    LOGS.info(f"User {user_id} removed from admins by {message.from_user.id}")
                else:
                    await sendMessage(message, f"<b><blockquote>ᴜsᴇʀ {user_id} ɪs ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ.</blockquote></b>")
            except Exception as e:
                LOGS.error(f"Error removing admin: {str(e)}")
                await sendMessage(message, f"<b><blockquote>ᴇʀʀᴏʀ:</blockquote></b> {str(e)}")
        
        elif action == 'add_ban':
            try:
                success = await db.add_ban(user_id)
                if success:
                    await sendMessage(message, f"<b><blockquote>ᴜsᴇʀ {user_id} ʜᴀs ʙᴇᴇɴ ʙᴀɴɴᴇᴅ!</blockquote></b>")
                    LOGS.info(f"User {user_id} banned by {message.from_user.id}")
                else:
                    await sendMessage(message, f"<b><blockquote>ᴜsᴇʀ {user_id} ᴀʟʀᴇᴀᴅʏ ʙᴀɴɴᴇᴅ.</blockquote></b>")
            except Exception as e:
                LOGS.error(f"Error adding ban: {str(e)}")
                await sendMessage(message, f"<b><blockquote>ᴇʀʀᴏʀ:</blockquote></b> {str(e)}")
        
        elif action == 'remove_ban':
            try:
                success = await db.remove_ban(user_id)
                if success:
                    await sendMessage(message, f"<b><blockquote>ᴜsᴇʀ {user_id} ʜᴀs ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ!</blockquote></b>")
                    LOGS.info(f"User {user_id} unbanned by {message.from_user.id}")
                else:
                    await sendMessage(message, f"<b><blockquote>ᴜsᴇʀ {user_id} ɪs ɴᴏᴛ ʙᴀɴɴᴇᴅ.</blockquote></b>")
            except Exception as e:
                LOGS.error(f"Error removing ban: {str(e)}")
                await sendMessage(message, f"<b><blockquote>ᴇʀʀᴏʀ:</blockquote></b> {str(e)}")
        
        elif action == 'set_day_upload':
            try:
                day_limit = int(message.text.strip())
                if day_limit < 1:
                    await sendMessage(message, "<b><blockquote>ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ɴᴜᴍʙᴇʀ ɢʀᴇᴀᴛᴇʀ ᴛʜᴀɴ 0!</blockquote></b>")
                    ani_cache['pending_action'] = None
                    return
                
                ani_cache['UPLOAD_DAY_LIMIT'] = day_limit
                await db.set_upload_day_limit(day_limit)
                ani_cache['UPLOADS_TODAY'] = 0
                await db.reset_daily_uploads()
                await sendMessage(message, f"<b><blockquote>ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ ʟɪᴍɪᴛ sᴇᴛ ᴛᴏ {day_limit}!</blockquote></b>")
                LOGS.info(f"Daily upload limit set to {day_limit} by {message.from_user.id}")
            except ValueError:
                await sendMessage(message, "<b><blockquote>ɪɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ. ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ɴᴜᴍʙᴇʀ!</blockquote></b>")
            except Exception as e:
                LOGS.error(f"Error setting day upload: {str(e)}")
                await sendMessage(message, f"<b><blockquote>ᴇʀʀᴏʀ:</blockquote></b> {str(e)}")
        
        ani_cache['pending_action'] = None
        
    except Exception as e:
        LOGS.error(f"Error in handle_whitelist_input: {str(e)}")

def parse_magnet_link(magnet_url: str) -> dict:
    try:
        if not magnet_url.startswith("magnet"):
            return None
        
        magnet_url = magnet_url.replace("magnet:?", "")
        params = parse_qs(magnet_url)
        
        magnet_data = {
            'title': None,
            'info_hash': None,
            'size': 'Unknown',
            'category': 'Real Life',
            'seeders': 0,
            'leechers': 0
        }
        
        if 'dn' in params:
            magnet_data['title'] = params['dn'][0]
        
        if 'xt' in params:
            xt_list = params['xt'] if isinstance(params['xt'], list) else [params['xt']]
            for xt_value in xt_list:
                if 'btih:' in xt_value:
                    hash_part = xt_value.split('btih:')[1]
                    magnet_data['info_hash'] = hash_part
                    break
        
        return magnet_data if magnet_data['title'] else None
    except Exception as e:
        LOGS.error(f"Error parsing magnet link: {str(e)}")
        return None

async def get_random_telegram_file():
    try:
        if not Var.DATABASE_CHANNEL or Var.DATABASE_CHANNEL == 0:
            return None
        
        try:
            latest_msgs = []
            async for msg in bot.search_messages(Var.DATABASE_CHANNEL, limit=1):
                latest_msgs.append(msg)
            
            if latest_msgs:
                max_msg_id = latest_msgs[0].id
            else:
                max_msg_id = 10000
            LOGS.debug(f"Max message ID in DATABASE_CHANNEL: {max_msg_id}")
        except Exception as e:
            LOGS.debug(f"Error getting latest message: {str(e)}, using fallback")
            max_msg_id = 10000
        
        max_attempts = 15
        for attempt in range(max_attempts):
            try:
                random_msg_id = randint(1, max(max_msg_id, 5000))
                msg = await bot.get_messages(Var.DATABASE_CHANNEL, message_ids=random_msg_id)
                
                if msg and msg.document:
                    file_name = msg.document.file_name or f"Document_{msg.id}"
                    file_size = msg.document.file_size
                    file_id = msg.document.file_id
                    LOGS.info(f"✓ Found random file: {file_name[:50]}")
                    return {
                        'file_id': file_id,
                        'file_name': file_name,
                        'file_size': file_size,
                        'message_id': msg.id
                    }
                elif msg and msg.video:
                    file_name = msg.video.file_name or f"Video_{msg.id}.mp4"
                    file_size = msg.video.file_size
                    file_id = msg.video.file_id
                    LOGS.info(f"✓ Found random video: {file_name[:50]}")
                    return {
                        'file_id': file_id,
                        'file_name': file_name,
                        'file_size': file_size,
                        'message_id': msg.id
                    }
                elif msg and msg.audio:
                    file_name = msg.audio.file_name or f"{msg.id}.mp3"
                    file_size = msg.audio.file_size
                    file_id = msg.audio.file_id
                    return {
                        'file_id': file_id,
                        'file_name': file_name,
                        'file_size': file_size,
                        'message_id': msg.id
                    }
                elif msg and msg.text:
                    pass
            except Exception as e:
                LOGS.debug(f"Attempt {attempt + 1}/{max_attempts} failed (ID: {random_msg_id}): {str(e)}")
                await asleep(0.3)
        
        LOGS.warning(f"Could not find file after {max_attempts} attempts in DATABASE_CHANNEL")
        return None
    except Exception as e:
        LOGS.error(f"Error getting random telegram file: {str(e)}")
        return None

@bot.on_message(command('addtask') & private & user([Var.OWNER] + Var.ADMINS))
@new_task
async def add_task(client, message):
    try:
        if len(args := message.text.split()) <= 1:
            return await sendMessage(message, "<b>No Task Found to Add</b>")
        
        input_link = args[1]
        
        # support /addtask telegram -> random file
        if input_link.lower() == "telegram":
            if not Var.DATABASE_CHANNEL or Var.DATABASE_CHANNEL == 0:
                return await sendMessage(message, "<b>DATABASE_CHANNEL not configured!</b>")
            
            tg_file = await get_random_telegram_file()
            if not tg_file:
                return await sendMessage(message, "<b>No files found in DATABASE_CHANNEL!</b>")
            
            title = tg_file['file_name']
            file_id = tg_file['file_id']
            file_size = tg_file['file_size']
            
            size_gb = file_size / (1024**3)
            if size_gb >= 1:
                size_str = f"{size_gb:.2f} GB"
            else:
                size_mb = file_size / (1024**2)
                size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{file_size / 1024:.2f} KB"
            
            await sendMessage(message, f"<i><b>Telegram File Task Added!</b></i>\n\n    • <b>File Name :</b> {title}\n    • <b>Size :</b> {size_str}")
            
            ani_cache['torrent_queue'].insert(0, {
                'title': title,
                'file_id': file_id,
                'file_size': file_size,
                'is_telegram': True,
                'size': size_str,
                'category': None,
                'seeders': 0,
                'leechers': 0,
                'info_hash': None,
                'torrent_url': None,
                'publish_date': None,
                'force': True
            })
            LOGS.info(f"Telegram file queued: {title[:50]}. Queue size: {len(ani_cache['torrent_queue'])}")
            return
        
        # support /addtask db<msgid> to queue specific database file
        if input_link.lower().startswith("db") and len(input_link) > 2 and input_link[2:].isdigit():
            if not Var.DATABASE_CHANNEL or Var.DATABASE_CHANNEL == 0:
                return await sendMessage(message, "<b>DATABASE_CHANNEL not configured!</b>")
            
            try:
                msg_id = int(input_link[2:])
            except ValueError:
                return await sendMessage(message, "<b>Invalid database message ID!</b>")
            
            # fetch specified message from database channel
            try:
                db_msg = await bot.get_messages(Var.DATABASE_CHANNEL, message_ids=msg_id)
            except Exception as e:
                LOGS.error(f"Error fetching message {msg_id} from DATABASE_CHANNEL: {e}")
                return await sendMessage(message, "<b>Error accessing DATABASE_CHANNEL</b>")
            
            if not db_msg or db_msg.empty:
                return await sendMessage(message, "<b>No message found with that ID in DATABASE_CHANNEL!</b>")
            
            # determine file type
            if db_msg.video:
                title = db_msg.video.file_name or f"Video_{msg_id}"
                file_id = db_msg.video.file_id
                file_size = db_msg.video.file_size
            elif db_msg.document:
                title = db_msg.document.file_name or f"Doc_{msg_id}"
                file_id = db_msg.document.file_id
                file_size = db_msg.document.file_size
            else:
                return await sendMessage(message, "<b>Specified message does not contain a video/document</b>")
            
            size_gb = file_size / (1024**3)
            if size_gb >= 1:
                size_str = f"{size_gb:.2f} GB"
            else:
                size_mb = file_size / (1024**2)
                size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{file_size / 1024:.2f} KB"
            
            await sendMessage(message, f"<i><b>Database File Task Added!</b></i>\n\n    • <b>File Name :</b> {title}\n    • <b>Size :</b> {size_str}\n    • <b>Source ID :</b> {msg_id}")
            
            ani_cache['torrent_queue'].insert(0, {
                'title': title,
                'file_id': file_id,
                'file_size': file_size,
                'is_telegram': True,
                'size': size_str,
                'category': None,
                'seeders': 0,
                'leechers': 0,
                'info_hash': None,
                'torrent_url': None,
                'publish_date': None,
                'force': True
            })
            LOGS.info(f"Database file queued: {title[:50]} (msg {msg_id}). Queue size: {len(ani_cache['torrent_queue'])}")
            return
        
        if input_link.startswith("magnet"):
            LOGS.info("Detected magnet link, parsing...")
            magnet_data = parse_magnet_link(input_link)
            
            if not magnet_data:
                return await sendMessage(message, "<b>Invalid Magnet Link! Could not extract title or hash.</b>")
            
            title = magnet_data['title']
            link = input_link
            size = magnet_data['size']
            category = magnet_data['category']
            seeders = magnet_data['seeders']
            leechers = magnet_data['leechers']
            info_hash = magnet_data['info_hash']
            published = None
            
            await sendMessage(message, f"<i><b>Magnet Task Added!</b></i>\n\n    • <b>Task Name :</b> {title}\n    • <b>Hash :</b> <code>{info_hash}</code>")
        else:
            index = int(args[2]) - 1 if len(args) > 2 and args[2].isdigit() else 0
            taskInfo = await getfeed(input_link, index)
            
            if not taskInfo:
                return await sendMessage(message, "<b>No Task Found to Add for the Provided Link</b>")
            
            title = (taskInfo.get('title') or getattr(taskInfo, 'title', None) or f"Torrent {int(time())}").strip()
            if not title or title.lower() == 'unknown':
                title = f"Task-{int(time())}"
            
            link = (taskInfo.get('link') or getattr(taskInfo, 'link', input_link) or input_link).strip()
            size = taskInfo.get('size') or getattr(taskInfo, 'size', 'Unknown')
            category = taskInfo.get('category') or getattr(taskInfo, 'category', 'Unknown')
            seeders = int(taskInfo.get('seeders') or getattr(taskInfo, 'seeders', 0) or 0)
            leechers = int(taskInfo.get('leechers') or getattr(taskInfo, 'leechers', 0) or 0)
            info_hash = taskInfo.get('info_hash') or getattr(taskInfo, 'info_hash', None)
            published = taskInfo.get('published') or getattr(taskInfo, 'published', None)
            
            await sendMessage(message, f"<i><b>Task Added Successfully!</b></i>\n\n    • <b>Task Name :</b> {title}\n    • <b>Task Link :</b> {link}")
        
        ani_cache['torrent_queue'].insert(0, {
            'title': title,
            'torrent_url': link,
            'publish_date': published,
            'size': size,
            'seeders': seeders,
            'leechers': leechers,
            'info_hash': info_hash,
            'category': category,
            'force': True
        })
        LOGS.info(f"Manual task queued at front. Queue size: {len(ani_cache['torrent_queue'])}")
        
    except Exception as e:
        await rep.report(f"Error in addtask: {str(e)}", "error")
        await sendMessage(message, f"<b>Error adding task:</b> {str(e)}")


@bot.on_message(command('postdb') & private & user([Var.OWNER] + Var.ADMINS))
@new_task
async def post_database_video_cmd(client, message):
    """Post a random video from DATABASE_CHANNEL to MAIN_CHANNEL"""
    try:
        from bot.core.database_poster import post_database_video
        
        temp = await sendMessage(message, "<b><blockquote>ғᴇᴛᴄʜɪɴɢ ᴀ ʀᴀɴᴅᴏᴍ ᴠɪᴅᴇᴏ...</blockquote></b>")
        
        result = await post_database_video()
        
        if result:
            await editMessage(temp, "<b><blockquote>✓ ᴠɪᴅᴇᴏ ᴘᴏsᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</blockquote></b>")
            LOGS.info(f"Database video posted by {message.from_user.id}")
        else:
            await editMessage(temp, "<b><blockquote>✗ ғᴀɪʟᴇᴅ ᴛᴏ ғɪɴᴅ ᴀ sᴜɪᴛᴀʙʟᴇ ᴠɪᴅᴇᴏ.</blockquote></b>")
            
    except Exception as e:
        LOGS.error(f"Error in post_database_video_cmd: {str(e)}")
        await sendMessage(message, f"<b><blockquote>ᴇʀʀᴏʀ: {str(e)}</blockquote></b>")


# quick add from database using /db<msgid> format
@bot.on_message(private & user([Var.OWNER] + Var.ADMINS))
async def quick_db_add(client, message):
    text = message.text or ''
    if not text.lower().startswith('/db'):
        return
    import re
    m = re.match(r'^/db(\d+)', text.lower())
    if not m:
        return
    msg_id = int(m.group(1))

    if not Var.DATABASE_CHANNEL or Var.DATABASE_CHANNEL == 0:
        return await sendMessage(message, "<b>DATABASE_CHANNEL not configured!</b>")
    try:
        db_msg = await bot.get_messages(Var.DATABASE_CHANNEL, message_ids=msg_id)
    except Exception as e:
        LOGS.error(f"Error fetching message {msg_id} from DATABASE_CHANNEL: {e}")
        return await sendMessage(message, "<b>Error accessing DATABASE_CHANNEL</b>")
    if not db_msg or db_msg.empty:
        return await sendMessage(message, "<b>No message found with that ID in DATABASE_CHANNEL!</b>")

    if db_msg.video:
        title = db_msg.video.file_name or f"Video_{msg_id}"
        file_id = db_msg.video.file_id
        file_size = db_msg.video.file_size
    elif db_msg.document:
        title = db_msg.document.file_name or f"Doc_{msg_id}"
        file_id = db_msg.document.file_id
        file_size = db_msg.document.file_size
    else:
        return await sendMessage(message, "<b>Specified message does not contain a video/document</b>")

    size_gb = file_size / (1024**3)
    if size_gb >= 1:
        size_str = f"{size_gb:.2f} GB"
    else:
        size_mb = file_size / (1024**2)
        size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{file_size / 1024:.2f} KB"

    await sendMessage(message, f"<i><b>Database File Task Added!</b></i>\n\n    • <b>File Name :</b> {title}\n    • <b>Size :</b> {size_str}\n    • <b>Source ID :</b> {msg_id}")
    
    ani_cache['torrent_queue'].insert(0, {
        'title': title,
        'file_id': file_id,
        'file_size': file_size,
        'is_telegram': True,
        'size': size_str,
        'category': None,
        'seeders': 0,
        'leechers': 0,
        'info_hash': None,
        'torrent_url': None,
        'publish_date': None,
        'force': True
    })
    LOGS.info(f"Database file queued via quick command: {title[:50]} (msg {msg_id}). Queue size: {len(ani_cache['torrent_queue'])}")
