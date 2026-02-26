from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bot import Var

class MongoDB:
    def __init__(self, uri, database_name):
        self.__client = AsyncIOMotorClient(uri)
        self.__db = self.__client[database_name]
        self.__rss = self.__db.torrents[Var.BOT_TOKEN.split(':')[0]]
        self.__whitelist = self.__db.whitelist
        self.__settings = self.__db.bot_settings
        self.__admins = self.__db.admins
        self.__bans = self.__db.bans

    async def saveTorrent(self, torrent_info):
        torrent_info['_id'] = torrent_info.get('info_hash', torrent_info['link'])
        torrent_info['saved_at'] = datetime.utcnow()
        await self.__rss.update_one({'_id': torrent_info['_id']}, {'$set': torrent_info}, upsert=True)
        return torrent_info['_id']

    async def getTorrent(self, torrent_id):
        return await self.__rss.find_one({'_id': torrent_id}) or {}

    async def getTorrentByHash(self, info_hash):
        return await self.__rss.find_one({'info_hash': info_hash}) or {}

    async def getAllTorrents(self, skip=0, limit=100):
        cursor = self.__rss.find().skip(skip).limit(limit).sort('saved_at', -1)
        return await cursor.to_list(length=limit)

    async def updateTorrentStatus(self, torrent_id, status_data):
        await self.__rss.update_one({'_id': torrent_id}, {'$set': status_data}, upsert=True)

    async def reboot(self):
        await self.__rss.drop()
    
    async def add_to_whitelist(self, user_id):
        result = await self.__whitelist.update_one(
            {'_id': user_id},
            {'$set': {'_id': user_id, 'added_at': datetime.utcnow()}},
            upsert=True
        )
        return result.upserted_id is not None or result.modified_count > 0

    async def remove_from_whitelist(self, user_id):
        result = await self.__whitelist.delete_one({'_id': user_id})
        return result.deleted_count > 0

    async def is_whitelisted(self, user_id):
        return await self.__whitelist.find_one({'_id': user_id}) is not None

    async def get_all_whitelisted(self):
        cursor = self.__whitelist.find().sort('added_at', -1)
        users = await cursor.to_list(length=None)
        return [user['_id'] for user in users]

    async def save_bot_settings(self, settings_dict):
        settings_dict['_id'] = 'bot_settings'
        settings_dict['updated_at'] = datetime.utcnow()
        await self.__settings.update_one({'_id': 'bot_settings'}, {'$set': settings_dict}, upsert=True)

    async def get_bot_settings(self):
        settings = await self.__settings.find_one({'_id': 'bot_settings'})
        return settings or {}

    async def update_bot_mode(self, mode):
        await self.__settings.update_one(
            {'_id': 'bot_settings'},
            {'$set': {'BOT_MODE': mode, 'updated_at': datetime.utcnow()}},
            upsert=True
        )

    async def update_font_changer(self, enabled: bool):
        await self.__settings.update_one(
            {'_id': 'bot_settings'},
            {'$set': {'FONT_CHANGER': enabled, 'updated_at': datetime.utcnow()}},
            upsert=True
        )

    async def get_font_changer_status(self):
        settings = await self.__settings.find_one({'_id': 'bot_settings'})
        return settings.get('FONT_CHANGER', False) if settings else False

    async def add_admin(self, admin_id):
        result = await self.__admins.update_one(
            {'_id': admin_id},
            {'$set': {'_id': admin_id, 'added_at': datetime.utcnow()}},
            upsert=True
        )
        return result.upserted_id is not None or result.modified_count > 0

    async def remove_admin(self, admin_id):
        result = await self.__admins.delete_one({'_id': admin_id})
        return result.deleted_count > 0

    async def is_admin(self, admin_id):
        return await self.__admins.find_one({'_id': admin_id}) is not None

    async def get_all_admins(self):
        cursor = self.__admins.find().sort('added_at', -1)
        admins = await cursor.to_list(length=None)
        return [admin['_id'] for admin in admins]

    async def add_ban(self, user_id):
        result = await self.__bans.update_one(
            {'_id': user_id},
            {'$set': {'_id': user_id, 'banned_at': datetime.utcnow()}},
            upsert=True
        )
        return result.upserted_id is not None or result.modified_count > 0

    async def remove_ban(self, user_id):
        result = await self.__bans.delete_one({'_id': user_id})
        return result.deleted_count > 0

    async def is_banned(self, user_id):
        return await self.__bans.find_one({'_id': user_id}) is not None

    async def get_all_bans(self):
        cursor = self.__bans.find().sort('banned_at', -1)
        bans = await cursor.to_list(length=None)
        return [ban['_id'] for ban in bans]

    async def set_auto_upload_enabled(self, enabled: bool):
        await self.__settings.update_one(
            {'_id': 'bot_settings'},
            {'$set': {'AUTO_UPLOAD_ENABLED': enabled, 'updated_at': datetime.utcnow()}},
            upsert=True
        )

    async def set_upload_day_limit(self, day_limit: int):
        await self.__settings.update_one(
            {'_id': 'bot_settings'},
            {'$set': {'UPLOAD_DAY_LIMIT': day_limit, 'updated_at': datetime.utcnow()}},
            upsert=True
        )

    async def set_upload_time(self, upload_time: str):
        await self.__settings.update_one(
            {'_id': 'bot_settings'},
            {'$set': {'UPLOAD_TIME': upload_time, 'updated_at': datetime.utcnow()}},
            upsert=True
        )

    async def get_auto_upload_settings(self):
        settings = await self.__settings.find_one({'_id': 'bot_settings'})
        if settings:
            return {
                'enabled': settings.get('AUTO_UPLOAD_ENABLED', False),
                'day_limit': settings.get('UPLOAD_DAY_LIMIT', 1),
                'upload_time': settings.get('UPLOAD_TIME', '12:00 PM')
            }
        return {'enabled': False, 'day_limit': 1, 'upload_time': '12:00 PM'}

    async def increment_daily_uploads(self):
        """Increment the daily upload counter for today"""
        today = datetime.utcnow().date()
        await self.__settings.update_one(
            {'_id': 'bot_settings'},
            {
                '$set': {
                    'LAST_UPLOAD_DATE': str(today),
                    'updated_at': datetime.utcnow()
                },
                '$inc': {'UPLOADS_TODAY': 1}
            },
            upsert=True
        )

    async def get_daily_upload_count(self):
        """Get the current daily upload count, resetting if date changed"""
        settings = await self.__settings.find_one({'_id': 'bot_settings'})
        if not settings:
            return 0
        
        today = datetime.utcnow().date()
        last_date = settings.get('LAST_UPLOAD_DATE')
        
        # Check if date has changed, reset if needed
        if last_date != str(today):
            await self.__settings.update_one(
                {'_id': 'bot_settings'},
                {
                    '$set': {
                        'UPLOADS_TODAY': 0,
                        'LAST_UPLOAD_DATE': str(today),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return 0
        
        return settings.get('UPLOADS_TODAY', 0)

    async def reset_daily_uploads(self):
        """Reset daily upload counter"""
        await self.__settings.update_one(
            {'_id': 'bot_settings'},
            {
                '$set': {
                    'UPLOADS_TODAY': 0,
                    'updated_at': datetime.utcnow()
                }
            },
            upsert=True
        )


db = MongoDB(Var.MONGO_URI, Var.MONGO_DB)
