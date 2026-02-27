"""
Module to handle automatic posting of videos from DATABASE_CHANNEL to MAIN_CHANNEL
"""
from random import randint
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait

from bot import bot, Var, LOGS
from .func_utils import sendMessage, editMessage, convertBytes
from .text_utils import TextEditor, TorrentInfo
from .database import db
from .rss_fetcher import should_auto_upload


async def post_database_video():
    """
    Fetch a random video from DATABASE_CHANNEL and post it to MAIN_CHANNEL
    with the same format as RSS posts
    """
    try:
        if not Var.DATABASE_CHANNEL or Var.DATABASE_CHANNEL == 0:
            LOGS.warning("DATABASE_CHANNEL not configured, skipping database video post")
            return None
        
        # Check if auto-upload is allowed (respects daily limits)
        if not await should_auto_upload():
            LOGS.info("Database video skipped: Daily upload limit reached or before scheduled time")
            return None
        
        # Get the latest message ID in the database channel
        max_msg_id = 10000
        try:
            async for msg in bot.search_messages(Var.DATABASE_CHANNEL, limit=1):
                max_msg_id = msg.id
                break
        except Exception as e:
            LOGS.debug(f"Error getting max message ID: {str(e)}")
        
        # Try to find a video message with retries
        max_attempts = 15
        for attempt in range(max_attempts):
            try:
                random_msg_id = randint(1, max(max_msg_id, 5000))
                msg = await bot.get_messages(Var.DATABASE_CHANNEL, message_ids=random_msg_id)
                
                if msg and msg.video:
                    LOGS.info(f"Found database video: {msg.video.file_name}")
                    
                    # Create torrent info from the video
                    file_name = msg.video.file_name or f"Video_{msg.id}"
                    file_size = msg.video.file_size
                    
                    torrent_info = TorrentInfo(
                        title=file_name,
                        link=str(msg.id),
                        publish_date=msg.date,
                        size=format_file_size(file_size),
                        seeders=0,
                        leechers=0,
                        info_hash=f"db_{msg.id}",
                        category="Database"
                    )
                    
                    # Create text editor for caption
                    text_editor = TextEditor(torrent_info, is_telegram=True)
                    caption = await text_editor.get_caption()
                    
                    # Get poster/thumbnail
                    poster_path = await text_editor.get_poster()
                    
                    # Create download link using filestore bot
                    link = f"https://telegram.me/{Var.FILESTORE_BOT_USERNAME}?start=get"
                    btns = [[InlineKeyboardButton("✦ 𝗘𝗡𝗧𝗘𝗥 ✦", url=link)]]
                    
                    # Post to main channel
                    post_msg = await bot.send_photo(
                        Var.MAIN_CHANNEL,
                        photo=poster_path,
                        caption=caption,
                        reply_markup=InlineKeyboardMarkup(btns),
                        has_spoiler=True
                    )
                    
                    # Save to database
                    torrent_info_dict = torrent_info.to_dict()
                    torrent_info_dict['post_id'] = post_msg.id
                    torrent_info_dict['source'] = 'database'
                    await db.saveTorrent(torrent_info_dict)
                    
                    # Get current upload count for logging
                    current_count = await db.get_daily_upload_count()
                    settings = await db.get_auto_upload_settings()
                    LOGS.info(f"Successfully posted database video to MAIN_CHANNEL: {file_name} | Upload Count: {current_count}/{settings['day_limit']}")
                    return post_msg
                    
            except Exception as e:
                LOGS.debug(f"Attempt {attempt + 1}/{max_attempts} failed: {str(e)}")
                continue
        
        LOGS.warning(f"Could not find suitable video after {max_attempts} attempts")
        return None
        
    except Exception as e:
        LOGS.error(f"Error posting database video: {str(e)}")
        return None


def format_file_size(size_bytes):
    """Convert bytes to human-readable format"""
    if not size_bytes:
        return "Unknown"
    
    size_gb = size_bytes / (1024**3)
    if size_gb >= 1:
        return f"{size_gb:.2f} GB"
    
    size_mb = size_bytes / (1024**2)
    if size_mb >= 1:
        return f"{size_mb:.2f} MB"
    
    size_kb = size_bytes / 1024
    return f"{size_kb:.2f} KB"
