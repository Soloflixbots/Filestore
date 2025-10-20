from aiohttp import web
from plugins import web_server

from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import LOGGER, PORT, OWNER_ID
from helper import MongoDB

version = "v1.0.0"


class Bot(Client):
    def __init__(self, session, workers, db, fsub, token, admins, messages, auto_del, db_uri, db_name, api_id, api_hash, protect, disable_btn):
        super().__init__(
            name=session,
            api_hash=api_hash,
            api_id=api_id,
            plugins={
                "root": "plugins"
            },
            workers=workers,
            bot_token=token
        )
        self.LOGGER = LOGGER
        self.name = session
        self.db = db
        self.fsub = fsub
        self.owner = OWNER_ID
        self.fsub_dict = {}
        self.admins = admins + [OWNER_ID] if OWNER_ID not in admins else admins
        self.messages = messages
        self.auto_del = auto_del
        self.protect = protect
        self.req_fsub = {}
        self.disable_btn = disable_btn
        self.reply_text = messages.get('REPLY', 'Do not send any useless message in the bot.')
        self.mongodb = MongoDB(db_uri, db_name)
        self.req_channels = []

    async def save_settings(self):
        """Saves current bot settings to the database."""
        self.messages['REPLY'] = self.reply_text
        settings = {
            'admins': self.admins,
            'fsubs': self.fsub,
            'messages': self.messages,
            'auto_del': self.auto_del,
            'protect': self.protect,
            'disable_btn': self.disable_btn,
        }
        await self.mongodb.update_bot_settings(self.name, settings)
    
    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        # Load settings from DB
        bot_settings = await self.mongodb.get_bot_settings(self.name)
        if bot_settings:
            self.LOGGER(__name__, self.name).info("Found saved settings in DB. Loading them.")
            db_admins = bot_settings.get('admins', self.admins)
            if self.owner not in db_admins:
                db_admins.append(self.owner)
            self.admins = db_admins
            self.fsub = bot_settings.get('fsubs', self.fsub)
            self.messages = bot_settings.get('messages', self.messages)
            self.auto_del = bot_settings.get('auto_del', self.auto_del)
            self.protect = bot_settings.get('protect', self.protect)
            self.disable_btn = bot_settings.get('disable_btn', self.disable_btn)
            self.reply_text = self.messages.get('REPLY', self.reply_text)
        else:
            self.LOGGER(__name__, self.name).info("No saved settings found in DB. Saving current settings.")
            await self.save_settings()

        if len(self.fsub) > 0:
            for channel in self.fsub:
                try:
                    chat = await self.get_chat(channel[0])
                    name = chat.title
                    link = None
                    if not channel[1]:
                        link = chat.invite_link
                    if not link and not channel[2]:
                        chat_link = await self.create_chat_invite_link(channel[0], creates_join_request=channel[1])
                        link = chat_link.invite_link
                    if not channel[1]:
                        self.fsub_dict[channel[0]] = [name, link, False, 0]
                    if channel[1]:
                        self.fsub_dict[channel[0]] = [name, link, True, 0]
                        self.req_channels.append(channel[0])
                    if channel[2] > 0:
                        self.fsub_dict[channel[0]] = [name, None, channel[1], channel[2]]
                except Exception as e:
                    self.LOGGER(__name__, self.name).warning("Bot can't Export Invite link from Force Sub Channel!")
                    self.LOGGER(__name__, self.name).warning(e)
                    
            await self.mongodb.set_channels(self.req_channels)
        try:
            db_channel = await self.get_chat(self.db)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Testing Message by @VOATcb")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__, self.name).warning(e)
            self.LOGGER(__name__, self.name).warning(f"Make Sure bot is Admin in DB Channel, and Double check the database channel Value, Current Value {self.db}")
            self.LOGGER(__name__, self.name).info("\nBot Stopped. Join https://t.me/Yugen_Bots_Support for support")
            sys.exit()
        self.LOGGER(__name__, self.name).info("Bot Started!!")
        
        self.username = usr_bot_me.username
    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__, self.name).info("Bot stopped.")


async def web_app():
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
