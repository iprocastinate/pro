from asyncio import create_task, create_subprocess_exec, create_subprocess_shell, run as asyrun, all_tasks, gather, sleep as asleep
from aiofiles import open as aiopen
from pyrogram import idle
from pyrogram.filters import command, user
from os import path as ospath, execl, kill
from sys import executable
from signal import SIGKILL
import time

from bot import bot, Var, bot_loop, sch, LOGS, ffQueue, ffLock, ffpids_cache, ff_queued, ani_cache
from bot.core.rss_fetcher import fetch_rss
from bot.core.func_utils import clean_up, new_task, editMessage
from bot.core.database import db

@bot.on_message(command('restart') & user([Var.OWNER]))
@new_task
async def restart(client, message):
    rmessage = await message.reply('<b><blockquote>ʀᴇsᴛᴀʀᴛɪɴɢ...</b></blockquote>')
    if sch.running:
        sch.shutdown(wait=False)
    await clean_up()
    if len(ffpids_cache) != 0: 
        for pid in ffpids_cache:
            try:
                LOGS.info(f"Process ID : {pid}")
                kill(pid, SIGKILL)
            except (OSError, ProcessLookupError):
                LOGS.error("Killing Process Failed !!")
                continue
    async with aiopen(".restartmsg", "w") as f:
        await f.write(f"{rmessage.chat.id}\n{rmessage.id}\n")
    execl(executable, executable, "-m", "bot")

async def restart():
    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text="<i>Restarted !</i>")
        except Exception as e:
            LOGS.error(e)
            
async def queue_loop():
    LOGS.info("Queue Loop Started !!")
    while True:
        if not ffQueue.empty():
            post_id = await ffQueue.get()
            await asleep(1.5)
            ff_queued[post_id].set()
            await asleep(1.5)
            async with ffLock:
                ffQueue.task_done()
        await asleep(10)

async def load_bot_settings():
    LOGS.info("Loading bot settings from database...")
    try:
        settings = await db.get_bot_settings()
        
        bot_mode = settings.get('BOT_MODE', 'default')
        ani_cache['BOT_MODE'] = bot_mode
        LOGS.info(f"Loaded BOT_MODE: {bot_mode}")
        
        font_changer = settings.get('FONT_CHANGER', False)
        ani_cache['FONT_CHANGER'] = font_changer
        LOGS.info(f"Loaded FONT_CHANGER: {font_changer}")
        
        auto_upload_settings = await db.get_auto_upload_settings()
        ani_cache['AUTO_UPLOAD_ENABLED'] = auto_upload_settings['enabled']
        ani_cache['UPLOAD_DAY_LIMIT'] = auto_upload_settings['day_limit']
        upload_time = auto_upload_settings['upload_time']

        if 'AM' in upload_time or 'PM' in upload_time:
            LOGS.info(f"Converting old time format: {upload_time}")
            time_clean = upload_time.replace('AM', '').replace('PM', '').strip()
            ani_cache['UPLOAD_TIME'] = time_clean
            await db.set_upload_time(time_clean)
            LOGS.info(f"Converted to new format: {time_clean}")
        else:
            ani_cache['UPLOAD_TIME'] = upload_time
        
        LOGS.info(f"Loaded AUTO_UPLOAD: {auto_upload_settings}")
        
        LOGS.info("Bot settings loaded successfully!")
    except Exception as e:
        LOGS.error(f"Error loading bot settings: {str(e)}")
        if 'BOT_MODE' not in ani_cache:
            ani_cache['BOT_MODE'] = 'default'
        if 'FONT_CHANGER' not in ani_cache:
            ani_cache['FONT_CHANGER'] = False
        if 'AUTO_UPLOAD_ENABLED' not in ani_cache:
            ani_cache['AUTO_UPLOAD_ENABLED'] = False
        LOGS.info("Using default bot settings")

async def main():
    # Check if we're recovering from recent crash (prevent flood wait)
    startup_delay_file = ".startup_delay"
    if ospath.isfile(startup_delay_file):
        try:
            with open(startup_delay_file, 'r') as f:
                last_start = float(f.read().strip())
            time_since_last = time.time() - last_start
            if time_since_last < 30:  # If less than 30 seconds since last start
                wait_time = 30 - time_since_last
                LOGS.warning(f"Recent restart detected. Waiting {wait_time:.1f}s to avoid Telegram flood wait...")
                await asleep(wait_time)
        except:
            pass
    
    # Record startup time
    with open(startup_delay_file, 'w') as f:
        f.write(str(time.time()))
    
    await bot.start()
    await restart()
    LOGS.info('Auto Adult Bot Started!')
    await load_bot_settings()
    
    bot_loop.create_task(queue_loop())
    
    from bot.core.rss_fetcher import torrent_processor
    bot_loop.create_task(torrent_processor())
    
    await fetch_rss()
    await idle()
    LOGS.info('Auto Adult Bot Stopped!')
    await bot.stop()
    for task in all_tasks:
        task.cancel()
    await clean_up()
    LOGS.info('Finished AutoCleanUp !!')
    
if __name__ == '__main__':
    bot_loop.run_until_complete(main())
