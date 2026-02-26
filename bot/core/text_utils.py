from datetime import datetime
from aiohttp import ClientSession
from anitopy import parse
from typing import Optional, Dict
import asyncio
from random import uniform
import re
from os import path as ospath
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE

from bot import Var, LOGS
from .ffencoder import ffargs
from .reporter import rep

CAPTION_FORMAT = """
<blockquote expandable><b>✦ {title} ✦</blockquote expandable>
━━━━━━━━━━━━━━━━━━━━
<blockquote>・ {rating_label}: {rating}
・ {size_label}: {size}</blockquote>
<blockquote>・ {category_label}: {category}
・ {recommendation_label}: {recommendation}</blockquote>
<blockquote expandable>・ {description_label}: {full_title}</blockquote expandable>
━━━━━━━━━━━━━━━━━━━━
<blockquote>≡ {powered_label}: <a href="https://t.me/MIRAGE_BOTZ">𝗠𝗜𝗥𝗔𝗚𝗘— 𝗕𝗢𝗧𝗭</a></b></blockquote>
"""

def truncate_title(title: str, max_length: int = 50) -> str:
    if not title:
        return "Unknown"
    if len(title) <= max_length:
        return title
    return title[:max_length].rstrip() + "....."


def normalize_size(size: str) -> str:
    if not size or size == "Unknown":
        return size
    
    size = str(size).strip()
    size = size.replace("MiB", "MB").replace("GiB", "GB").replace("TiB", "TB").replace("KiB", "KB")
    return size


def generate_random_rating() -> float:
    return round(uniform(7.0, 9.9), 1)


def get_recommendation(rating: float) -> str:
    if rating >= 9.5:
        return "#MUST_WATCH #HOTTEST_VIDEO #100%_WATCH"
    elif rating >= 9.0:
        return "#MUST_WATCH #HOTTEST_VIDEO #RECOMMANDED"
    elif rating >= 8.5:
        return "#MUST_WATCH #RECOMMANDED"
    elif rating >= 8.0:
        return "#RECOMMANDED"
    else:
        return "#WATCH_NOW"


def clean_title(title: str) -> tuple:
    if not title:
        return title, []
    
    removed = []
    original = title

    match = re.search(r'\[.*?(?:264|265|1080|720|480|h\.|hevc|av1).*?\]', title, flags=re.IGNORECASE)
    if match:
        removed.append(f"Quality: {match.group()}")
    title = re.sub(r'\[.*?(?:264|265|1080|720|480|h\.|hevc|av1).*?\]', '', title, flags=re.IGNORECASE)

    quality_match = re.search(r'\b(?:\d+p|4k|fhd|hd|sd|480|720|1080)\b', title, flags=re.IGNORECASE)
    if quality_match:
        removed.append(f"Quality: {quality_match.group()}")
    title = re.sub(r'\b(?:\d+p|4k|fhd|hd|sd|480|720|1080)\b', '', title, flags=re.IGNORECASE)
    
    ext_match = re.search(r'\.(mp4|mkv|avi|mov|m4v|flv|wmv|webm|jp4)\b', title, flags=re.IGNORECASE)
    if ext_match:
        removed.append(f"Ext: {ext_match.group()}")
    title = re.sub(r'\.(mp4|mkv|avi|mov|m4v|flv|wmv|webm|jp4)\b', '', title, flags=re.IGNORECASE)
    
    date_match = re.search(r'\b(?:\d{4}[-.]\d{1,2}[-.]\d{1,2}|\d{1,2}[-.]\d{1,2}[-.]\d{4}|\d{1,2}/\d{1,2}/\d{4})\b', title)
    if date_match:
        removed.append(f"Date: {date_match.group()}")
    title = re.sub(r'\b(?:\d{4}[-.]\d{1,2}[-.]\d{1,2}|\d{1,2}[-.]\d{1,2}[-.]\d{4}|\d{1,2}/\d{1,2}/\d{4})\b', '', title)
    
    code_pattern = re.search(r'\b[A-Z]+[-_]?\d+\b', title)
    if code_pattern:
        removed.append(f"Code: {code_pattern.group()}")
    title = re.sub(r'\b[A-Z]+[-_]?\d+\b', '', title)
    
    short_qual = re.search(r'\b(?:rq|hq|lq|uhd|webdl|webrip)\b', title, flags=re.IGNORECASE)
    if short_qual:
        removed.append(f"Quality: {short_qual.group()}")
    title = re.sub(r'\b(?:rq|hq|lq|uhd|webdl|webrip)\b', '', title, flags=re.IGNORECASE)
    episode_pattern = re.search(r'\b(?:episode|ep|e)\s*\.?\s*\d+\b', title, flags=re.IGNORECASE)
    if episode_pattern:
        removed.append(f"Episode: {episode_pattern.group()}")
    title = re.sub(r'\b(?:episode|ep|e)\s*\.?\s*\d+\b', '', title, flags=re.IGNORECASE)
    
    raw_pattern = re.search(r'\bRAW\b', title, flags=re.IGNORECASE)
    if raw_pattern:
        removed.append(f"Format: {raw_pattern.group()}")
    title = re.sub(r'\bRAW\b', '', title, flags=re.IGNORECASE)
    
    sub_pattern = re.search(r'\b(?:subbed|dubbed|english\s+subbed|english)\b', title, flags=re.IGNORECASE)
    if sub_pattern:
        removed.append(f"Sub: {sub_pattern.group()}")
    title = re.sub(r'\b(?:subbed|dubbed|english\s+subbed|english)\b', '', title, flags=re.IGNORECASE)
    
    title = re.sub(r'[★★●◎〇等]', '', title)
    title = re.sub(r'\s*\(\s*\)\s*', ' ', title)
    title = re.sub(r'_', ' ', title)
    title = re.sub(r'-', ' ', title)
    title = re.sub(r'\s+', ' ', title)
    
    cleaned = title.strip()
    return cleaned, removed if cleaned != original else []


def to_bold_sans_serif(text: str) -> str:
    if not text:
        return text
    
    bold_upper = "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭"
    bold_digits = "𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵𝟬"
    
    normal_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    normal_digits = "1234567890"
    
    result = ""
    for char in text.upper():
        if char in normal_upper:
            result += bold_upper[normal_upper.index(char)]
        elif char in normal_digits:
            result += bold_digits[normal_digits.index(char)]
        elif char == " ":
            result += " "
        else:
            result += char
    
    return result


def obfuscate_word(word: str) -> str:
    replacements = {
        'A': '@', 'a': '@',
        'O': '0', 'o': '0',
        'S': '$', 's': '$',
        'R': 'π', 'r': 'π',
        'C': '¢', 'c': '¢',
    }
    
    result = ""
    for i, char in enumerate(word):
        if char in replacements:
            if i % 3 == 0:
                result += replacements[char]
            elif i % 3 == 1 and char.upper() == 'O':
                result += '0'
            elif i % 3 == 1 and char.upper() == 'A':
                result += '@'
            elif i % 3 == 2 and char.upper() == 'I':
                result += 'l'
            else:
                result += replacements[char]
        else:
            result += char
    
    return result


def censor_content(text: str) -> str:
    if not text:
        return text
    
    censor_words = [
        'anal', 'pussy', 'sex', 'porn', 'xxx', 'hardcore', 'softcore',
        'cum', 'cock', 'dick', 'cunt', 'ass', 'fuck', 'slut', 'whore',
        'creampie', 'gangbang', 'ebony', 'latin', 'amateur', 'bondage',
        'fetish', 'orgy', 'swallow', 'blowjob', 'deepthroat', 'cumshot',
        'bitch', 'whores', 'sluts', 'fucks', 'fucking', 'motherfucker',
        'cumming', 'bitch', 'doggy style', 'doggystyle', 'doggie style',
        'dildo', 'erotic', 'ejaculation', 'horny', 'jerk off',
        'nude', 'nudity', 'penis', 'pornography', 'vagina',
        'tit', 'tits', 'butt', 'threesome',
    ]
    
    result = text
    for word in censor_words:
        pattern = r'\b' + word + r'\b'
        obfuscated = obfuscate_word(word)
        result = re.sub(pattern, obfuscated.upper(), result, flags=re.IGNORECASE)
    
    return result


async def generate_screenshot(video_path: str, output_path: str = "thumbs/screenshot.jpg", timestamp: int = None, is_telegram: bool = False) -> Optional[str]:
    try:
        if not ospath.exists(video_path):
            LOGS.error(f"Video file not found: {video_path}")
            return None
        
        if not ospath.exists("thumbs"):
            from os import mkdir
            mkdir("thumbs")
        
        if timestamp is None:
            try:
                from .func_utils import mediainfo
                duration = await mediainfo(video_path, get_duration=True)
                if duration and isinstance(duration, (int, float)) and duration > 0:
                    percentage = 0.50 if is_telegram else 0.35
                    timestamp = int(duration * percentage)
                else:
                    timestamp = 30
            except Exception as e:
                LOGS.debug(f"mediainfo failed, using default timestamp: {str(e)}")
                timestamp = 30
        
        ffmpeg_cmd = f'ffmpeg -i "{video_path}" -ss {timestamp} -vframes 1 -q:v 2 "{output_path}" -y'
        proc = await create_subprocess_shell(ffmpeg_cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = await proc.communicate()
        
        if ospath.exists(output_path):
            LOGS.info(f"Screenshot generated at {timestamp}s: {output_path}")
            return output_path
        else:
            LOGS.error(f"Failed to generate screenshot from {video_path}, ffmpeg output: {stderr.decode()[-200:]}")
            return None
    except Exception as e:
        LOGS.error(f"Error generating screenshot: {str(e)}")
        return None


class Translator:
    
    def __init__(self):
        self.__cache = {}
    
    async def translate(self, text: str, target_lang: str = "en") -> str:
        if not text or text.isascii():
            return text
        
        cache_key = f"{text}:{target_lang}"
        if cache_key in self.__cache:
            return self.__cache[cache_key]
        
        try:
            params = {
                "q": text[:500],
                "langpair": f"auto|{target_lang}"
            }
            async with ClientSession() as sess:
                async with sess.get("https://api.mymemory.translated.net/get", params=params, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("responseStatus") == 200:
                            translated = data.get("responseData", {}).get("translatedText", text)
                            if translated and translated != text:
                                self.__cache[cache_key] = translated
                                LOGS.info(f"Translated: {text[:60]}... -> {translated[:60]}...")
                                return translated
        except Exception as e:
            LOGS.debug(f"MyMemory translation failed: {str(e)}")
        
        try:
            async with ClientSession() as sess:
                url = f"https://translate.googleapis.com/translate_a/element.js?cb=googleTranslateElementInit"
                async with sess.get(url, timeout=5) as resp:
                    pass
            
            google_url = f"https://translate.google.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={text}"
            async with ClientSession() as sess:
                async with sess.get(google_url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data and len(data) > 0:
                            translated = data[0][0][0] if data[0] and data[0][0] else text
                            if translated and translated != text:
                                self.__cache[cache_key] = translated
                                LOGS.info(f"Translated (Google): {text[:60]}... -> {translated[:60]}...")
                                return translated
        except Exception as e:
            LOGS.debug(f"Google translate failed: {str(e)}")
        
        self.__cache[cache_key] = text
        return text

translator = Translator()

class TorrentInfo:
    
    def __init__(self, title: str, link: str, publish_date: str = None, 
                 size: str = None, seeders: int = 0, leechers: int = 0,
                 info_hash: str = None, category: str = None):
        cleaned_title, removed_items = clean_title(title)
        self.original_title = cleaned_title
        self.removed_items = removed_items
        self.link = link
        self.publish_date = publish_date or datetime.utcnow().isoformat()
        self.size = size or "Unknown"
        self.seeders = seeders
        self.leechers = leechers
        self.info_hash = info_hash
        self.category = category or "Unknown"
        self.translated_title = None
        self.rating = generate_random_rating()
        self.parsed_info = parse(self.original_title)
    
    def get_parsed_title(self) -> Optional[str]:
        return self.parsed_info.get("anime_title")
    
    def get_episode_number(self) -> Optional[int]:
        return self.parsed_info.get("episode_number")
    
    def to_dict(self) -> Dict:
        return {
            "title": self.original_title,
            "translated_title": self.translated_title or self.original_title,
            "link": self.link,
            "publish_date": self.publish_date,
            "size": self.size,
            "seeders": self.seeders,
            "leechers": self.leechers,
            "info_hash": self.info_hash,
            "category": self.category,
            "rating": self.rating,
            "parsed_title": self.get_parsed_title(),
            "episode_number": self.get_episode_number()
        }

class TextEditor:
    
    def __init__(self, torrent_info: TorrentInfo, is_telegram: bool = False):
        self.info = torrent_info
        self.parsed_data = torrent_info.parsed_info
        self.is_telegram = is_telegram
    
    async def load_translation(self):
        title = self.info.original_title
        if title and not title.isascii():
            self.info.translated_title = await translator.translate(title, "en")
        else:
            self.info.translated_title = title
    
    async def get_caption(self) -> str:
        await self.load_translation()
        
        display_title = self.info.translated_title or self.info.original_title
        truncated_title = truncate_title(display_title, 50)
        if self.is_telegram:
            full_title = "𝗡𝗨𝗟𝗟"
        else:
            full_title = display_title
        
        return CAPTION_FORMAT.format(
            title=to_bold_sans_serif(truncated_title),
            full_title=to_bold_sans_serif(full_title),
            rating=to_bold_sans_serif(str(self.info.rating)),
            size=to_bold_sans_serif(normalize_size(str(self.info.size))),
            category=to_bold_sans_serif(str(self.info.category)),
            recommendation=to_bold_sans_serif(get_recommendation(self.info.rating)),
            rating_label=to_bold_sans_serif("RATING"),
            size_label=to_bold_sans_serif("SIZE"),
            category_label=to_bold_sans_serif("CATEGORY"),
            recommendation_label=to_bold_sans_serif("RECOMMENDATION"),
            description_label=to_bold_sans_serif("DESCRIPTION"),
            powered_label=to_bold_sans_serif("POWERED BY"),
        )
    
    async def get_upname(self, qual: str = "") -> str:
        await self.load_translation()
        
        title = self.info.get_parsed_title() or self.info.translated_title or self.info.original_title
        codec = 'HEVC' if 'libx265' in ffargs.get(qual, '') else 'AV1' if 'libaom-av1' in ffargs.get(qual, '') else 'H264'
        
        try:
            parts = [title.strip()]
            
            if qual:
                parts.append(f"[{qual}]")
            
            if codec:
                parts.append(f"[{codec}]")
            
            parts.append("@MIRAGE_BOTZ")
            
            filename = " ".join(parts) + ".mkv"
            filename = " ".join(filename.split())
            return filename
        except Exception as e:
            LOGS.error(f"Error generating filename: {str(e)}")
            return f"{self.info.translated_title or self.info.original_title}.mkv"
    
    async def get_screenshot(self, video_path: str) -> Optional[str]:
        return await generate_screenshot(video_path, f"thumbs/screenshot_{int(uniform(1, 999999))}.jpg", is_telegram=self.is_telegram)
    
    async def get_poster(self) -> str:
        return Var.THUMB or "https://telegra.ph/file/112ec08e59e73b6189a20.jpg"
    
    def get_episode_number(self) -> Optional[int]:
        return self.parsed_data.get("episode_number")
