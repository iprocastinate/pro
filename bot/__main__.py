from asyncio import all_tasks, sleep as asleep, gather
from aiofiles import open as aiopen
from pyrogram import idle
from pyrogram.filters import command, user
from pyrogram.errors import FloodWait
from os import path as ospath, execl, kill
from sys import executable
from signal import SIGKILL

from bot import bot, Var, bot_loop, sch, LOGS, ffQueue, ffLock, ffpids_cache, ff_queued, ani_cache
from bot.core.rss_fetcher import fetch_rss
from bot.core.func_utils import clean_up, new_task
from bot.core.database import db
from bot.health_check_standalone import start_health_server


# ==========================
# RESTART COMMAND HANDLER
# ==========================
@bot.on_message(command("restart") & user([Var.OWNER]))
@new_task
async def restart_cmd(client, message):
    rmessage = await message.reply("<b><blockquote>Restarting...</blockquote></b>")

    if sch.running:
        sch.shutdown(wait=False)

    await clean_up()

    if ffpids_cache:
        for pid in ffpids_cache:
            try:
                LOGS.info(f"Killing Process ID: {pid}")
                kill(pid, SIGKILL)
            except (OSError, ProcessLookupError):
                LOGS.error("Failed to kill process")

    async with aiopen(".restartmsg", "w") as f:
        await f.write(f"{rmessage.chat.id}\n{rmessage.id}\n")

    execl(executable, executable, "-m", "bot")


# ==========================
# POST-RESTART MESSAGE EDIT
# ==========================
async def restart_notify():
    if ospath.isfile(".restartmsg"):
        try:
            with open(".restartmsg") as f:
                chat_id, msg_id = map(int, f)

            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg_id,
                text="<i>Restarted Successfully!</i>"
            )
        except Exception as e:
            LOGS.error(f"Restart notify failed: {e}")


# ==========================
# QUEUE LOOP
# ==========================
async def queue_loop():
    LOGS.info("Queue Loop Started")

    while True:
        try:
            if not ffQueue.empty():
                post_id = await ffQueue.get()
                await asleep(1.5)

                ff_queued[post_id].set()

                await asleep(1.5)
                async with ffLock:
                    ffQueue.task_done()

            await asleep(10)

        except Exception as e:
            LOGS.error(f"Queue Loop Error: {e}")
            await asleep(5)


# ==========================
# LOAD SETTINGS
# ==========================
async def load_bot_settings():
    LOGS.info("Loading bot settings...")

    try:
        settings = await db.get_bot_settings()

        ani_cache["BOT_MODE"] = settings.get("BOT_MODE", "default")
        ani_cache["FONT_CHANGER"] = settings.get("FONT_CHANGER", False)

        auto_upload = await db.get_auto_upload_settings()

        ani_cache["AUTO_UPLOAD_ENABLED"] = auto_upload.get("enabled", False)
        ani_cache["UPLOAD_DAY_LIMIT"] = auto_upload.get("day_limit", 0)
        ani_cache["UPLOAD_TIME"] = auto_upload.get("upload_time", "00:00")
        ani_cache["UPLOAD_TIME_WINDOW_ENABLED"] = auto_upload.get("time_window_enabled", False)
        ani_cache["UPLOAD_START_TIME"] = auto_upload.get("upload_start_time", "00:00")
        ani_cache["UPLOAD_STOP_TIME"] = auto_upload.get("upload_stop_time", "23:59")

        LOGS.info("Bot settings loaded successfully")

    except Exception as e:
        LOGS.error(f"Settings load error: {e}")
        ani_cache.setdefault("BOT_MODE", "default")
        ani_cache.setdefault("FONT_CHANGER", False)
        ani_cache.setdefault("AUTO_UPLOAD_ENABLED", False)


# ==========================
# SAFE BOT START (FLOOD PROOF)
# ==========================
async def safe_start():
    while True:
        try:
            await bot.start()
            LOGS.info("Bot started successfully")
            break

        except FloodWait as e:
            wait_time = e.value + 60
            LOGS.error(f"FloodWait detected. Waiting {wait_time} seconds...")
            await asleep(wait_time)

        except Exception as e:
            LOGS.error(f"Startup failed: {e}")
            LOGS.warning("Retrying in 30 seconds...")
            await asleep(30)


# ==========================
# MAIN FUNCTION
# ==========================
async def main():
    # Start health check server in background (runs independently)
    health_task = bot_loop.create_task(start_health_server())
    
    await safe_start()

    await restart_notify()

    LOGS.info("Auto Adult Bot Started")

    await load_bot_settings()

    bot_loop.create_task(queue_loop())

    from bot.core.rss_fetcher import torrent_processor
    bot_loop.create_task(torrent_processor())

    await fetch_rss()

    await idle()

    LOGS.info("Bot stopping...")

    await bot.stop()

    for task in all_tasks():
        task.cancel()

    await clean_up()

    LOGS.info("Shutdown complete")


# ==========================
# ENTRY POINT
# ==========================
if __name__ == "__main__":
    bot_loop.run_until_complete(main())
