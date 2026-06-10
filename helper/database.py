
import motor.motor_asyncio
import uuid
import base64
from datetime import datetime, timedelta, timezone

class MongoDB:
    _instances = {}

    def __new__(cls, uri: str, db_name: str, uri2: str = "", uri3: str = "", uri4: str = ""):
        key = (uri, uri2, uri3, uri4, db_name)
        if key not in cls._instances:
            instance = super().__new__(cls)
            instance.clients = []
            instance.uris = [u for u in [uri, uri2, uri3, uri4] if u]
            for u in instance.uris:
                instance.clients.append(motor.motor_asyncio.AsyncIOMotorClient(u))

            instance.client = instance.clients[0]
            instance.db = instance.client[db_name]
            instance.user_data = instance.db["users"]
            instance.channel_data = instance.db["channels"]
            instance.bot_settings = instance.db["bot_settings"]
            instance.batch_data = instance.db["batch_links"]
            instance.backup_map = instance.db["backup_map"]
            instance.mongodb_uris = instance.db["mongodb_uris"]
            instance.clones = instance.db["clones"]
            instance.link_channels = instance.db["link_sharing_channels"]
            instance.invite_links = instance.db["invite_links"]
            instance.verifications = instance.db["verifications"]
            instance.short_links = instance.db["short_links"]
            instance.aliases = instance.db["aliases"]
            instance.temp_links = instance.db["temp_links"]

            cls._instances[key] = instance
        return cls._instances[key]

    async def save_verification(self, payload: str, bot_username: str, captcha: int = None) -> str:
        temp_id = str(uuid.uuid4().hex[:10])
        data = {"_id": temp_id, "payload": payload, "bot_username": bot_username, "created_at": datetime.now(timezone.utc)}
        if captcha is not None:
            data["captcha"] = captcha
        await self.verifications.insert_one(data)
        return temp_id

    async def get_verification(self, temp_id: str) -> dict | None:
        return await self.verifications.find_one({"_id": temp_id})

    async def save_short_link(self, payload: str, bot_username: str) -> str:
        short_id = str(uuid.uuid4().hex[:10])
        data = {"_id": short_id, "payload": payload, "bot_username": bot_username, "created_at": datetime.now(timezone.utc)}
        await self.short_links.insert_one(data)
        return short_id

    async def get_short_link(self, short_id: str) -> dict | None:
        return await self.short_links.find_one({"_id": short_id})

    async def save_link_channel(self, channel_id: int):
        await self.link_channels.update_one({"_id": channel_id}, {"$set": {"_id": channel_id}}, upsert=True)

    async def remove_link_channel(self, channel_id: int) -> bool:
        res = await self.link_channels.delete_one({"_id": channel_id})
        return res.deleted_count > 0

    async def get_link_channels(self) -> list[int]:
        return [doc["_id"] async for doc in self.link_channels.find({})]

    async def is_link_channel(self, channel_id: int) -> bool:
        return await self.link_channels.find_one({"_id": channel_id}) is not None

    async def get_current_invite_link(self, channel_id: int | str, is_request: bool):
        return await self.invite_links.find_one({"_id": f"{channel_id}_{is_request}"})

    async def save_invite_link(self, channel_id: int | str, invite_link: str, is_request: bool, expires_at: datetime = None):
        data = {"channel_id": channel_id, "invite_link": invite_link, "is_request": is_request, "created_at": datetime.now(timezone.utc)}
        if expires_at:
            data["expires_at"] = expires_at
        await self.invite_links.update_one(
            {"_id": f"{channel_id}_{is_request}"},
            {"$set": data},
            upsert=True
        )

    async def save_batch(self, channel_id: int, file_ids: list) -> str:
        key = str(uuid.uuid4().hex[:8])
        await self.batch_data.insert_one(
            {"_id": key, "channel_id": channel_id, "ids": file_ids}
        )
        return key

    async def get_batch(self, key: str) -> tuple | None:
        data = await self.batch_data.find_one({"_id": key})
        return (data.get("channel_id"), data.get("ids")) if data else (None, None)

    async def add_backup_mapping(self, original_chat_id: int, original_msg_id: int, backup_msg_id: int):
        await self.backup_map.update_one(
            {"_id": f"{original_chat_id}:{original_msg_id}"},
            {"$set": {"backup_msg_id": backup_msg_id}},
            upsert=True
        )

    async def get_backup_msg_id(self, original_chat_id: int, original_msg_id: int) -> int | None:
        data = await self.backup_map.find_one({"_id": f"{original_chat_id}:{original_msg_id}"})
        return data.get("backup_msg_id") if data else None

    async def is_backed_up(self, original_chat_id: int, original_msg_id: int) -> bool:
        count = await self.backup_map.count_documents({"_id": f"{original_chat_id}:{original_msg_id}"})
        return count > 0

    async def save_settings(self, session_name: str, settings: dict):
        await self.bot_settings.update_one(
            {"_id": session_name},
            {"$set": {"settings": settings}},
            upsert=True
        )

    async def load_settings(self, session_name: str) -> dict | None:
        data = await self.bot_settings.find_one({"_id": session_name})
        return data.get("settings") if data else None

    async def save_bot_setting(self, key: str, value):
        await self.bot_settings.update_one({'_id': 'global_config'}, {'$set': {key: value}}, upsert=True)
    async def load_bot_setting(self, key: str, default=None):
        config = await self.bot_settings.find_one({'_id': 'global_config'})
        return config.get(key, default) if config else default
    async def set_channels(self, channels: list[int]):
        await self.user_data.update_one(
            {"_id": 1},
            {"$set": {"channels": channels}},
            upsert=True
        )
    async def get_channels(self) -> list[int]:
        data = await self.user_data.find_one({"_id": 1})
        return data.get("channels", []) if data else []
    async def add_channel_user(self, channel_id: int, user_id: int):
        await self.channel_data.update_one(
            {"_id": channel_id},
            {"$addToSet": {"users": user_id}},
            upsert=True
        )

    async def remove_channel_user(self, channel_id: int, user_id: int):
        await self.channel_data.update_one(
            {"_id": channel_id},
            {"$pull": {"users": user_id}}
        )

    async def get_channel_users(self, channel_id: int) -> list[int]:
        doc = await self.channel_data.find_one({"_id": channel_id})
        return doc.get("users", []) if doc else []
    async def is_user_in_channel(self, channel_id: int, user_id: int) -> bool:
        doc = await self.channel_data.find_one(
            {"_id": channel_id, "users": {"$in": [user_id]}},
            {"_id": 1}
        )
        return doc is not None

    async def present_user(self, user_id: int, bot_id: int = None) -> bool:
        if bot_id:
            found = await self.user_data.find_one({'_id': user_id, 'bots': {'$in': [bot_id]}})
        else:
            found = await self.user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int, bot_id: int, ban: bool = False):
        await self.user_data.update_one(
            {'_id': user_id},
            {
                '$setOnInsert': {'ban': ban},
                '$addToSet': {'bots': bot_id}
            },
            upsert=True
        )

    async def total_users_count(self) -> int:
        pipeline = [
            {"$match": {"_id": {"$ne": 1}, "bots": {"$exists": True}}},
            {"$project": {"bot_count": {"$size": "$bots"}}},
            {"$group": {"_id": None, "total": {"$sum": "$bot_count"}}}
        ]
        cursor = self.user_data.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        return result[0]['total'] if result else 0

    async def bot_users_count(self, bot_id: int) -> int:
        return await self.user_data.count_documents({'bots': {'$in': [bot_id]}})

    async def full_userbase(self) -> list[int]:
        user_docs = self.user_data.find({"_id": {"$ne": 1}})
        return [doc['_id'] async for doc in user_docs]

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})

    async def ban_user(self, user_id: int):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'ban': True}})

    async def unban_user(self, user_id: int):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'ban': False}})

    async def is_banned(self, user_id: int) -> bool:
        user = await self.user_data.find_one({'_id': user_id})
        return user.get('ban', False) if user else False

    async def decode_link_param(self, param: str) -> str:
        try:
            param = param.strip()
            base64_string = param.replace('-', '+').replace('_', '/')
            base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("utf-8")
            string_bytes = base64.b64decode(base64_bytes)
            return string_bytes.decode("utf-8")
        except (base64.binascii.Error, UnicodeDecodeError):
            return None
        except Exception as e:
            print(f"Unexpected decode error: {e}")
            return None

    async def add_mongo_uri(self, uri: str):
        await self.mongodb_uris.update_one({'_id': uri}, {'$set': {'uri': uri}}, upsert=True)

    async def get_mongo_uris(self):
        return [doc['uri'] async for doc in self.mongodb_uris.find({})]

    async def remove_mongo_uri(self, uri: str):
        await self.mongodb_uris.delete_one({'_id': uri})

    async def add_clone(self, bot_token: str, config: dict):
        await self.clones.update_one({'_id': bot_token}, {'$set': {'config': config}}, upsert=True)

    async def get_clones(self):
        return [doc['config'] async for doc in self.clones.find({})]

    async def remove_clone(self, bot_token: str):
        await self.clones.delete_one({'_id': bot_token})


    async def save_alias(self, alias: str, payload: str):
        await self.aliases.update_one(
            {"_id": alias},
            {"$set": {"payload": payload}},
            upsert=True
        )

    async def get_alias(self, alias: str):
        data = await self.aliases.find_one({"_id": alias})
        return data.get("payload") if data else None

    async def save_temp_link(self, payload: str, bot_username: str, expiry_mins: int) -> str:
        temp_id = str(uuid.uuid4().hex[:10])
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiry_mins)
        data = {
            "_id": temp_id,
            "payload": payload,
            "bot_username": bot_username,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc)
        }
        await self.temp_links.insert_one(data)
        return temp_id

    async def get_temp_link(self, temp_id: str) -> dict | None:
        data = await self.temp_links.find_one({"_id": temp_id})
        if not data:
            return None

        if datetime.now(timezone.utc) > data["expires_at"].replace(tzinfo=timezone.utc):
            return None

        return data
