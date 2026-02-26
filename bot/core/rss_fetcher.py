from asyncio import gather, create_task, sleep as asleep, Event
from asyncio.subprocess import PIPE
from os import path as ospath, system, listdir
from os.path import isdir, isfile, join
from shutil import rmtree
from aiofiles import open as aiopen
from aiofiles.os import remove as aioremove
from traceback import format_exc
from base64 import urlsafe_b64encode
from time import time
from datetime import datetime, timedelta, timezone
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot import bot, bot_loop, Var, ani_cache, ffQueue, ffLock, ff_queued, LOGS
from .tordownload import TorDownloader
from .database import db
from .func_utils import getfeed, encode, editMessage, sendMessage, convertBytes
from .text_utils import TextEditor, TorrentInfo, censor_content
from .ffencoder import FFEncoder
from .tguploader import TgUploader
from .reporter import rep


btn_formatter = {
    'CODE':'✦ 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗 𝗡𝗢𝗪 ✦', 
}

last_torrent_id = None


def parse_size_to_gb(size_str):
    if not size_str:
        return None
    
    try:
        size_str = str(size_str).strip()
        parts = size_str.split()
        if len(parts) < 2:
            return None
            
        size_value = float(parts[0])
        unit = parts[1].upper()
        
        if unit in ['B', 'BYTES']:
            return size_value / (1024**3)
        elif unit in ['KB', 'KIBIBYTES']:
            return size_value / (1024**2)
        elif unit in ['MB', 'MEBIBYTES']:
            return size_value / 1024
        elif unit in ['GB', 'GIBIBYTES', 'GIB']:
            return size_value
        elif unit in ['TB', 'TEBIBYTES']:
            return size_value * 1024
        else:
            return None
    except (ValueError, IndexError):
        return None


def find_video_files(directory):
    video_extensions = ('.mp4', '.mkv', '.av1', '.avi', '.mov', '.m4v', '.flv', '.wmv', '.webm')
    video_files = []
    
    try:
        if isdir(directory):
            for item in listdir(directory):
                item_path = join(directory, item)
                if isfile(item_path) and item.lower().endswith(video_extensions):
                    video_files.append(item_path)
                elif isdir(item_path):
                    video_files.extend(find_video_files(item_path))
        elif isfile(directory) and directory.lower().endswith(video_extensions):
            video_files.append(directory)
    except Exception as e:
        LOGS.error(f"Error finding video files: {str(e)}")
    
    return sorted(video_files)


def calculate_total_size(file_paths):
    from os.path import getsize
    total_bytes = 0
    
    try:
        for file_path in file_paths:
            if ospath.isfile(file_path):
                total_bytes += getsize(file_path)
            elif ospath.isdir(file_path):
                from os import walk as oswalk
                for root, dirs, files in oswalk(file_path):
                    for file in files:
                        try:
                            total_bytes += getsize(join(root, file))
                        except:
                            pass
    except Exception as e:
        LOGS.error(f"Error calculating file size: {str(e)}")
        return None
    
    size_gb = total_bytes / (1024**3)
    
    if size_gb >= 1:
        return f"{size_gb:.2f} GB"
    else:
        size_mb = total_bytes / (1024**2)
        if size_mb >= 1:
            return f"{size_mb:.2f} MB"
        else:
            size_kb = total_bytes / 1024
            return f"{size_kb:.2f} KB"


def reset_daily_upload_counter():
    last_date = ani_cache.get('LAST_UPLOAD_DATE')
    ist = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(ist).date()
    
    if last_date is None or last_date != str(today):
        ani_cache['LAST_UPLOAD_DATE'] = str(today)
        ani_cache['UPLOADS_TODAY'] = 0
        return True
    return False


def should_auto_upload():
    if not ani_cache.get('AUTO_UPLOAD_ENABLED', False):
        LOGS.info("Auto upload is disabled, allowing unlimited uploads")
        return True
    
    try:
        reset_daily_upload_counter()
        
        day_limit = ani_cache.get('UPLOAD_DAY_LIMIT', 1)
        uploads_today = ani_cache['UPLOADS_TODAY']
        
        if uploads_today >= day_limit:
            LOGS.info(f"Daily upload limit reached: {uploads_today}/{day_limit}")
            return False
        
        ist = timezone(timedelta(hours=5, minutes=30))
        current_dt = datetime.now(ist)
        current_time = current_dt.time()
        
        upload_time_str = ani_cache.get('UPLOAD_TIME', '12:00')
        
        try:
            time_obj = datetime.strptime(upload_time_str, "%H:%M").time()
        except ValueError:
            time_clean = upload_time_str.replace('AM', '').replace('PM', '').strip()
            try:
                time_obj = datetime.strptime(time_clean, "%H:%M").time()
            except ValueError:
                LOGS.warning(f"Could not parse upload time: {upload_time_str}, skipping upload")
                return False
        
        if current_time >= time_obj:
            ani_cache['UPLOADS_TODAY'] += 1
            LOGS.info(f"Upload allowed - Time: {current_time.hour:02d}:{current_time.minute:02d}, Scheduled: {time_obj.hour:02d}:{time_obj.minute:02d}, Uploaded: {ani_cache['UPLOADS_TODAY']}/{day_limit}")
            return True
        else:
            LOGS.info(f"Before upload time. Current: {current_time.hour:02d}:{current_time.minute:02d}, Scheduled: {time_obj.hour:02d}:{time_obj.minute:02d}")
            return False
    
    except Exception as e:
        LOGS.error(f"Error checking auto upload settings: {str(e)}")
        return False


async def torrent_processor():
    LOGS.info("Torrent Processor Started!")
    while True:
        await asleep(2)
        if not ani_cache['processing_torrent'] and len(ani_cache['torrent_queue']) > 0:
            torrent_data = ani_cache['torrent_queue'].pop(0)
            ani_cache['processing_torrent'] = True
            LOGS.info(f"Starting torrent from queue: {torrent_data['title'][:50]} (Queue remaining: {len(ani_cache['torrent_queue'])})")
            await get_rss(
                title=torrent_data['title'],
                torrent_url=torrent_data.get('torrent_url'),
                publish_date=torrent_data.get('publish_date'),
                size=torrent_data.get('size'),
                seeders=torrent_data.get('seeders', 0),
                leechers=torrent_data.get('leechers', 0),
                info_hash=torrent_data.get('info_hash'),
                category=torrent_data.get('category'),
                force=torrent_data.get('force', False),
                is_telegram=torrent_data.get('is_telegram', False),
                file_id=torrent_data.get('file_id'),
                file_size=torrent_data.get('file_size')
            )
            ani_cache['processing_torrent'] = False

async def fetch_rss():
    global last_torrent_id
    
    await rep.report("Fetching has been Started.", "info")
    while True:
        await asleep(60)
        if ani_cache['fetch_rss']:
            for link in Var.RSS_ITEMS:
                if (info := await getfeed(link, 0)):
                    torrent_hash = info.get('info_hash', '')
                    torrent_url = info.get('link', '')
                    torrent_title = info.get('title', 'Unknown')
                    
                    torrent_id = torrent_hash or torrent_url
                    
                    if torrent_id != last_torrent_id:
                        last_torrent_id = torrent_id
                        LOGS.info(f"New torrent detected at position 0: {torrent_title[:50]}")
                        
                        if should_auto_upload():
                            ani_cache['torrent_queue'].append({
                                'title': torrent_title,
                                'torrent_url': torrent_url,
                                'publish_date': info.get('published'),
                                'size': info.get('size'),
                                'seeders': info.get('seeders', 0),
                                'leechers': info.get('leechers', 0),
                                'info_hash': torrent_hash,
                                'category': info.get('category')
                            })
                            LOGS.info(f"Torrent queued. Queue size: {len(ani_cache['torrent_queue'])}")
                        else:
                            LOGS.info(f"Torrent skipped due to auto upload restrictions: {torrent_title[:50]}")
                    else:
                        LOGS.debug(f"Same torrent at position 0, skipping: {torrent_title[:50]}")

async def get_rss(title: str, torrent_url: str, publish_date=None, size=None, 
                  seeders=0, leechers=0, info_hash=None, category=None, force=False,
                  is_telegram=False, file_id=None, file_size=None):
    try:
        if is_telegram and file_id:
            LOGS.info(f"[Telegram] Processing: {title} (File ID: {file_id})")
            
            torrent_id = file_id
            
            if not force and await db.getTorrent(torrent_id):
                LOGS.info(f"Telegram file already processed: {title}")
                return
            
            torrent_info = TorrentInfo(
                title=title,
                link=file_id,
                publish_date=publish_date,
                size=size or "Unknown",
                seeders=0,
                leechers=0,
                info_hash=file_id,
                category=category or "Telegram"
            )
            
            text_editor = TextEditor(torrent_info, is_telegram=True)
            
            LOGS.info(f"Downloading telegram file: {title}")
            
            try:
                dl_dir = "./downloads/telegram"
                from os import makedirs
                makedirs(dl_dir, exist_ok=True)
                
                dl = await bot.download_media(file_id, file_name=join(dl_dir, title))
                if not dl or not ospath.exists(dl):
                    LOGS.error(f"✗ Telegram file download failed for: {title}")
                    await rep.report(f"Telegram File Download Incomplete", "error")
                    return
                    
                LOGS.info(f"✓ Telegram file downloaded: {dl}")
            except Exception as e:
                LOGS.error(f"✗ Error downloading telegram file: {str(e)}")
                await rep.report(f"Telegram Download Error: {str(e)}", "error")
                return
        else:
            torrent_info = TorrentInfo(
                title=title,
                link=torrent_url,
                publish_date=publish_date,
                size=size,
                seeders=seeders,
                leechers=leechers,
                info_hash=info_hash,
                category=category
            )
            
            if torrent_info.removed_items:
                removed_str = " | ".join(torrent_info.removed_items)
                LOGS.info(f"✓ Cleaned: {removed_str}")
                await rep.report(f"Title Cleaned!\n\n{removed_str}\n\nFinal: {torrent_info.original_title}", "info")
            
            torrent_id = info_hash or torrent_url
            
            if not force and await db.getTorrent(torrent_id):
                return
            
            if "[Batch]" in title:
                await rep.report(f"Torrent Skipped!\n\n{title}", "warning")
                return
            
            size_gb = parse_size_to_gb(size)
            if size_gb and size_gb > 1.9:
                await rep.report(f"Torrent Skipped (Size > 1.9GB)!\n\nTitle: {title}\nSize: {size}", "warning")
                return
            
            await rep.report(f"New Torrent Found!\n\n{title}", "info")
            
            text_editor = TextEditor(torrent_info, is_telegram=False)
            
            LOGS.info(f"[1/7] Starting download for: {title}")
            
            dl = await TorDownloader("./downloads").download(torrent_url, title)
            if not dl or not ospath.exists(dl):
                LOGS.error(f"✗ Download failed for: {title}")
                await rep.report(f"File Download Incomplete, Try Again", "error")
                return

        torrent_info_dict = torrent_info.to_dict()
        await db.saveTorrent(torrent_info_dict)

        ffEvent = Event()
        ff_queued[torrent_id] = ffEvent
        if ffLock.locked():
            await rep.report("Added Task to Queue...", "info")
        
        await ffQueue.put(torrent_id)
        await ffEvent.wait()
        
        await ffLock.acquire()
        btns = []
        batch_first_msg_id = None
        batch_last_msg_id = None
        first_video_file = None
        
        video_files = find_video_files(dl)
        
        if not video_files:
            await rep.report(f"No video files found in: {dl}", "error")
            ffLock.release()
            return
        
        actual_size = calculate_total_size(video_files)
        if actual_size:
            torrent_info.size = actual_size
            await db.updateTorrentStatus(torrent_id, {'size': actual_size})
        
        first_video_file = video_files[0]
        
        for video_idx, video_file in enumerate(video_files, 1):
            for qual in Var.QUALS:
                is_batch = len(video_files) > 1
                
                if is_batch:
                    filename = await text_editor.get_upname(qual)
                    base, ext = ospath.splitext(filename)
                    filename = f"{base}{ext}"
                else:
                    filename = await text_editor.get_upname(qual)
                
                await rep.report(f"Starting Encode for video {video_idx}/{len(video_files)}...", "info")
                try:
                    out_path = await FFEncoder(None, video_file, filename, qual).start_encode()
                except Exception as e:
                    LOGS.error(f"✗ Encoding failed: {e}")
                    await rep.report(f"Error: {e}, Cancelled,  Retry Again !", "error")
                    ffLock.release()
                    return
                await rep.report("Successfully Compressed Now Going To Upload...", "info")
                
                if is_batch:
                    try:
                        msg = await TgUploader(None).upload(out_path, qual)
                        msg_id = msg.id
                        
                        if batch_first_msg_id is None:
                            batch_first_msg_id = msg_id
                        batch_last_msg_id = msg_id
                        
                        await rep.report(f"Successfully Uploaded to FILE_STORE: {msg_id}", "info")
                    except Exception as e:
                        LOGS.error(f"✗ Upload failed: {e}")
                        await rep.report(f"Error uploading to FILE_STORE: {e}", "error")
                        ffLock.release()
                        return
                else:
                    try:
                        msg = await TgUploader(None).upload(out_path, qual)
                        msg_id = msg.id
                        await rep.report("Successfully Uploaded File into Tg...", "info")
                    except Exception as e:
                        LOGS.error(f"✗ Upload failed: {e}")
                        await rep.report(f"Error: {e}, Cancelled,  Retry Again !", "error")
                        ffLock.release()
                        return
                
                if is_batch:
                    pass
                else:
                    link = f"https://telegram.me/{(await bot.get_me()).username}?start={await encode('get-'+str(msg_id * abs(Var.FILE_STORE)))}"
                    
                    if len(btns) != 0 and len(btns[-1]) == 1:
                        btns[-1].insert(1, InlineKeyboardButton(f"{btn_formatter[qual]}", url=link))
                    else:
                        btns.append([InlineKeyboardButton(f"{btn_formatter[qual]}", url=link)])
                    
                await db.updateTorrentStatus(torrent_id, {
                    'qual': qual,
                    'video_index': video_idx,
                    'uploaded': True,
                    'msg_id': msg_id,
                    'file_size': msg.document.file_size if hasattr(msg.document, 'file_size') else 0
                })
        
        await rep.report("Generating screenshot...", "info")
        screenshot_path = await text_editor.get_screenshot(first_video_file)
        
        if screenshot_path and ospath.exists(screenshot_path):
            LOGS.info(f"Screenshot generated: {screenshot_path}")
        else:
            await rep.report(f"Error: Screenshot generation failed, using default poster", "error")
            screenshot_path = await text_editor.get_poster()
        
        batch_btns = None
        if len(video_files) > 1 and batch_first_msg_id is not None:
            batch_string = f"get-{batch_first_msg_id * abs(Var.FILE_STORE)}-{batch_last_msg_id * abs(Var.FILE_STORE)}"
            batch_link = f"https://telegram.me/{(await bot.get_me()).username}?start={await encode(batch_string)}"
            batch_btns = [[InlineKeyboardButton(f"{btn_formatter['CODE']}", url=batch_link)]]
            LOGS.info(f"Batch link created: {batch_string[:50]}...")
        
        LOGS.info(f"Sending final post to MAIN_CHANNEL...")
        try:
            caption = await text_editor.get_caption()
            
            if ani_cache.get('FONT_CHANGER', False):
                caption = censor_content(caption)
            
            post_msg = await bot.send_photo(
                Var.MAIN_CHANNEL,
                photo=screenshot_path,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(batch_btns if batch_btns else btns) if (batch_btns or btns) else None,
                has_spoiler=True
            )
            
            torrent_info_dict = torrent_info.to_dict()
            torrent_info_dict['post_id'] = post_msg.id
            await db.saveTorrent(torrent_info_dict)
            
            await rep.report(f"Upload Complete! Posted to channel", "info")

        except Exception as e:
            LOGS.error(f"Error sending final post: {e}")
            await rep.report(f"Error sending final post: {e}", "error")
            ffLock.release()
            return
        
        ffLock.release()
        
        if ospath.exists(screenshot_path) and screenshot_path.startswith("thumbs/"):
            try:
                await aioremove(screenshot_path)
            except:
                pass
        if isdir(dl):
            rmtree(dl, ignore_errors=True)
        else:
            await aioremove(dl)
    except Exception as error:
        LOGS.error(f"FATAL ERROR in torrent processing: {str(error)}")
        LOGS.error(f"Traceback: {format_exc()}")
        await rep.report(format_exc(), "error")
