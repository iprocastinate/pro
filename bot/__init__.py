from os import path as ospath, mkdir, system, getenv
from logging import INFO, ERROR, FileHandler, StreamHandler, basicConfig, getLogger
from traceback import format_exc
from asyncio import Queue, Lock

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from pyrogram.enums import ParseMode
from dotenv import load_dotenv
from uvloop import install

install()
basicConfig(format="[%(asctime)s] [%(name)s | %(levelname)s] - %(message)s [%(filename)s:%(lineno)d]",
            datefmt="%m/%d/%Y, %H:%M:%S %p",
            handlers=[FileHandler('log.txt'), StreamHandler()],
            level=INFO)

getLogger("pyrogram").setLevel(ERROR)
LOGS = getLogger(__name__)

load_dotenv('config.env')

ani_cache = {
    'fetch_rss': True,
    'ongoing': set(),
    'completed': set(),
    'torrent_queue': [],
    'processing_torrent': False,
    'pending_action': None,
    'addtask_cooldown': {},
    'whitelist_cooldown': {},
    'FONT_CHANGER': False,
    'AUTO_UPLOAD_ENABLED': False,
    'UPLOAD_DAY_LIMIT': 1,
    'UPLOAD_TIME': '12:00',
    'UPLOADS_TODAY': 0,
    'LAST_UPLOAD_DATE': None,
    'LAST_UPLOAD_TIME': None
}
ffpids_cache = list()

ffLock = Lock()
ffQueue = Queue()
ff_queued = dict()

class Var:
    API_ID, API_HASH, BOT_TOKEN = getenv("API_ID"), getenv("API_HASH"), getenv("BOT_TOKEN")
    MONGO_URI = getenv("MONGO_URI")
    MONGO_DB = getenv("MONGO_DB")
    
    if not BOT_TOKEN or not API_HASH or not API_ID or not MONGO_URI:
        LOGS.critical('Important Variables Missing. Fill Up and Retry..!! Exiting Now...')
        exit(1)


    RSS_ITEMS = getenv("RSS_ITEMS", "https://subsplease.org/rss/?r=1080").split()
    FSUB_CHATS = list(map(int, getenv('FSUB_CHATS').split()))
    MAIN_CHANNEL = int(getenv("MAIN_CHANNEL"))
    LOG_CHANNEL = int(getenv("LOG_CHANNEL") or 0)
    FILE_STORE = int(getenv("FILE_STORE"))
    DATABASE_CHANNEL = int(getenv("DATABASE_CHANNEL") or 0)
    FILESTORE_BOT_USERNAME = getenv("FILESTORE_BOT_USERNAME", "GenAnimeOfcBot")
    ADMINS = list(map(int, getenv("ADMINS", "1242011540").split()))
    OWNER = int(getenv("OWNER", "7086472788"))
    BOT_USERNAME = getenv("BOT_USERNAME", "GenAnimeOfcBot")
    
    FFCODE_CODE = 'ffmpeg -i "{}" -progress "{}" -nostats -loglevel warning -c copy -map 0:v -map 0:a? -map 0:s? -metadata title="GenAnimeOfc [t.me/GenAnimeOfc]" -metadata:s:s title="[GenAnimeOfc]" -metadata:s:a title="[GenAnimeOfc]" -metadata:s:v title="[GenAnimeOfc]" "{}" -y'
    QUALS = getenv("QUALS", "CODE").split()
    
    AS_DOC = getenv("AS_DOC", "True").lower() == "true"
    THUMB = getenv("THUMB", "https://te.legra.ph/file/621c8d40f9788a1db7753.jpg")
    AUTO_DEL = getenv("AUTO_DEL", "True").lower() == "true"
    DEL_TIMER = int(getenv("DEL_TIMER", "600"))
    START_PHOTO = getenv("START_PHOTO", "https://te.legra.ph/file/120de4dbad87fb20ab862.jpg")
    START_MSG = getenv("START_MSG", "<b>Hey {first_name}</b>,\n\n    <i>I am Auto Animes Store & Automater Encoder Build with ❤️ !!</i>")
    HELP_PHOTO = getenv("HELP_PHOTO", "https://te.legra.ph/file/120de4dbad87fb20ab862.jpg")
    ABOUT_PHOTO = getenv("ABOUT_PHOTO", "https://te.legra.ph/file/120de4dbad87fb20ab862.jpg")

if Var.THUMB and not ospath.exists("thumb.jpg"):
    system(f"wget -q {Var.THUMB} -O thumb.jpg")
    LOGS.info("Thumbnail has been Saved!!")
if not ospath.isdir("encode/"):
    mkdir("encode/")
if not ospath.isdir("thumbs/"):
    mkdir("thumbs/")
if not ospath.isdir("downloads/"):
    mkdir("downloads/")

try:
    bot = Client(name="AutoPorn", api_id=Var.API_ID, api_hash=Var.API_HASH, bot_token=Var.BOT_TOKEN, plugins=dict(root="bot/modules"), parse_mode=ParseMode.HTML)
    bot_loop = bot.loop
    sch = AsyncIOScheduler(timezone="Asia/Kolkata", event_loop=bot_loop)
except Exception as ee:
    LOGS.error(str(ee))
    exit(1)
