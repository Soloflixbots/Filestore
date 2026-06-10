from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout
from helper.helper_func import is_bot_admin
from plugins.settings import send_settings_panel

async def get_db_settings_panel(client: Client):
    """Generates the text, and markup for the DB settings panel."""
    databases = client.databases
    primary_db = databases.get('primary')
    secondary_dbs = databases.get('secondary', [])
    backup_db = databases.get('backup')

    async def get_chat_title(chat_id):
        if not chat_id: return "Not Set"
        try:
            chat = await client.get_chat(chat_id)
            return f"{chat.title} (<code>{chat_id}</code>)"
        except Exception:
            return f"Invalid Channel (<code>{chat_id}</code>)"

    primary_text = await get_chat_title(primary_db)
    backup_text = await get_chat_title(backup_db)
    secondary_lines = []
    if secondary_dbs:
        for db_id in secondary_dbs:
            secondary_lines.append(f"› {await get_chat_title(db_id)}")
    secondary_text = "\n".join(secondary_lines) if secondary_lines else "› <i>None</i>"

    caption_text = f"""<blockquote><b>✧ 𝖣𝖺𝗍𝖺𝖻𝖺𝗌𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌</b></blockquote>
<b>❆ 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖯𝗋𝗂𝗆𝖺𝗋𝗒 𝖣𝖺𝗍𝖺𝖻𝖺𝗌𝖾 :</b>
›› {primary_text}

<b>❆ 𝖲𝖾𝖼𝗈𝗇𝖽𝖺𝗋𝗒 𝖣𝖺𝗍𝖺𝖻𝖺𝗌𝖾𝗌 :</b>
›› {secondary_text}

<b>❆ 𝖡𝖺𝖼𝗄𝗎𝗉 𝖣𝖺𝗍𝖺𝖻𝖺𝗌𝖾 :</b>
›› {backup_text}

<i>𝖴𝗌𝖾 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇𝗌 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝗆𝖺𝗇𝖺𝗀𝖾 𝗒𝗈𝗎𝗋 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾 𝖼𝗁𝖺𝗇𝗇𝖾𝗅𝗌.</i>
"""
    buttons = [
        [InlineKeyboardButton('✦ 𝖠𝖽𝖽 𝖣𝖻 𝖢𝗁𝖺𝗇𝗇𝖾𝗅', 'add_db'), InlineKeyboardButton('✦ 𝖱𝖾𝗆𝗈𝗏𝖾 𝖣𝖻 𝖢𝗁𝖺𝗇𝗇𝖾𝗅', 'rm_db')],
        [InlineKeyboardButton('✦ 𝖲𝖾𝗍 𝖯𝗋𝗂𝗆𝖺𝗋𝗒', 'set_primary_db'), InlineKeyboardButton('✦ 𝖲𝖾𝗍 𝖡𝖺𝖼𝗄𝗎𝗉', 'set_backup_db')],
    ]
    if not client.name.startswith("clone_"):
        buttons.append([InlineKeyboardButton('✦ 𝖬𝗈𝗇𝗀𝗈𝖣𝖡 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌', 'mongo_settings')])
    buttons.append([InlineKeyboardButton('✦ 𝖡𝖺𝖼𝗄', 'settings_pg1')])
    reply_markup = InlineKeyboardMarkup(buttons)
    return caption_text, reply_markup

@Client.on_message(filters.command('database') & filters.private)
async def db_settings_command(client: Client, message: Message):
    """Handles the /database command."""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    caption, reply_markup = await get_db_settings_panel(client)
    class FakeQuery:
        def __init__(self, message): self.message = message
    await send_settings_panel(client, FakeQuery(message), caption, reply_markup)

async def db_settings(client: Client, query: CallbackQuery):
    """
    Displays the main Database Channels settings menu from a callback.
    """
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    caption, reply_markup = await get_db_settings_panel(client)
    await send_settings_panel(client, query, caption, reply_markup)

async def update_db_channel(client, query, action):
    """Helper to add, remove, or set DB channels."""
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    prompts = {
        "add_db": "𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝖽 𝖿𝗈𝗋 𝗍𝗁𝖾 𝗇𝖾𝗐 <b>𝖲𝖾𝖼𝗈𝗇𝖽𝖺𝗋𝗒</b> 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾.",
        "rm_db": "𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝖽 𝗈𝗿 𝗍𝗁𝖾 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾 𝗍𝗈 𝗋𝖾𝗆𝗈𝗏𝖾.",
        "set_primary_db": "𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝖽 𝗍𝗈 𝗌𝖾𝗍 𝖺𝗌 <b>𝖯𝗋𝗂𝗆𝖺𝗋𝗒</b>.\n(𝖬𝗎𝗌𝗍 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝖻𝖾 𝖺 𝗌𝖾𝖼𝗈𝗇𝖽𝖺𝗋𝗒 𝖼𝗁𝖺𝗇𝗇𝖾𝗅)",
        "set_backup_db": "𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝖽 𝗍𝗈 𝗌𝖾𝗍 𝖺𝗌 <b>𝖡𝖺𝖼𝗄𝗎𝗉</b>."
    }
    prompt_msg_text = f"<blockquote>{prompts[action]}</blockquote>"

    if query.message.photo:
        await query.message.edit_caption(caption=prompt_msg_text)
        prompt_msg = query.message
    else:
        prompt_msg = await query.message.edit_text(prompt_msg_text, reply_markup=None, parse_mode=ParseMode.HTML)

    try:
        response = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=90)
        channel_id = int(response.text.strip())

        if action == "add_db":
            is_admin, reason = await is_bot_admin(client, channel_id)
            if not is_admin:
                return await response.reply(f"<b>Error:</b> {reason}", parse_mode=ParseMode.HTML)
            if 'secondary' not in client.databases: client.databases['secondary'] = []
            if channel_id in client.databases['secondary']:
                return await response.reply("𝖳𝗁𝗂𝗌 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗂𝗌 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝖺 𝗌𝖾𝖼𝗈𝗇𝖽𝖺𝗋𝗒 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾.", parse_mode=ParseMode.HTML)
            client.databases['secondary'].append(channel_id)
            await response.reply(f"✅ 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 <code>{channel_id}</code> 𝖺𝖽𝖽𝖾𝖽 𝖺𝗌 𝖺 𝗌𝖾𝖼𝗈𝗇𝖽𝖺𝗋𝗒 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾.", parse_mode=ParseMode.HTML)

        elif action == "rm_db":
            found = False
            if client.databases.get('primary') == channel_id:
                return await response.reply("𝖢𝖺𝗇𝗇𝗈𝗍 𝗋𝖾𝗆𝗈𝗏𝖾 𝗍𝗁𝖾 𝗉𝗋𝗂𝗆𝖺𝗋𝗒 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾. 𝖲𝖾𝗍 𝖺 𝗇𝖾𝗐 𝗉𝗋𝗂𝗆𝖺𝗋𝗒 𝖿𝗂𝗋𝗌𝗍.", parse_mode=ParseMode.HTML)
            if client.databases.get('backup') == channel_id:
                client.databases['backup'] = None
                found = True
            if channel_id in client.databases.get('secondary', []):
                client.databases['secondary'].remove(channel_id)
                found = True
            if found:
                await response.reply(f"✅ 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 <code>{channel_id}</code> 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗋𝖾𝗆𝗈𝗏𝖾𝖽.", parse_mode=ParseMode.HTML)
            else:
                await response.reply("❌ 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝗇𝗈𝗍 𝖿𝗈𝗎𝗇𝖽 𝗂𝗇 𝖺𝗇𝗒 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾 𝖼𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖺𝗍𝗂𝗈𝗇.", parse_mode=ParseMode.HTML)
        elif action == "set_primary_db":
            if channel_id not in client.databases.get('secondary', []):
                return await response.reply("𝖳𝗁𝗂𝗌 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗆𝗎𝗌𝗍 𝖻𝖾 𝖺 𝗌𝖾𝖼𝗈𝗇𝖽𝖺𝗋𝗒 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾 𝖿𝗂𝗋𝗌𝗍.", parse_mode=ParseMode.HTML)
            old_primary = client.databases.get('primary')
            client.databases['primary'] = channel_id
            client.databases['secondary'].remove(channel_id)
            if old_primary:
                client.databases['secondary'].append(old_primary)
            await response.reply(f"✅ <code>{channel_id}</code> 𝗂𝗌 𝗇𝗈𝗐 𝗍𝗁𝖾 𝗉𝗋𝗂𝗆𝖺𝗋𝗒 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾.", parse_mode=ParseMode.HTML)

        elif action == "set_backup_db":
            is_admin, reason = await is_bot_admin(client, channel_id)
            if not is_admin:
                return await response.reply(f"<b>𝖤𝗋𝗋𝗈𝗋:</b> {reason}", parse_mode=ParseMode.HTML)
            client.databases['backup'] = channel_id
            await response.reply(f"✅ <code>{channel_id}</code> 𝗂𝗌 𝗇𝗈𝗐 𝗍𝗁𝖾 𝖻𝖺𝖼𝗄𝗎𝗉 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾.", parse_mode=ParseMode.HTML)

        client.db = client.databases.get('primary')
        client.all_db_ids = [db_id for db_id in [client.databases.get('primary')] + client.databases.get('secondary', []) if db_id]
        await client.refresh_db_usernames()
        await client.mongodb.save_settings(client.name, client.get_current_settings())
    except ListenerTimeout:
         pass
    except (ValueError, TypeError):
        await query.message.reply("<b>𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖨𝖽 𝖿𝗈𝗋𝗆𝖺𝗍.</b> 𝖯𝗅𝖾𝖺𝗌𝖾 𝗌𝖾𝗇𝖽 𝖺 𝖼𝗈𝗋𝗋𝖾𝗊𝗍 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝖽.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await query.message.reply(f"𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽: <code>{e}</code>", parse_mode=ParseMode.HTML)
    await db_settings(client, query)

@Client.on_callback_query(filters.regex("^(add|rm|set_primary|set_backup)_db$"))
async def db_callbacks(client: Client, query: CallbackQuery):
    await update_db_channel(client, query, query.data)

@Client.on_callback_query(filters.regex("^mongo_settings$"))
async def mongo_settings_cb(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    uris = client.mongodb.uris

    text = "<b><blockquote>🍃 𝖬𝗈𝗇𝗀𝗈𝖣𝖡 𝖴𝖱𝖨 𝖲𝗍𝖺𝗍𝗎𝗌</blockquote>\n\n𝖲𝗍𝖺𝗍𝗎𝗌 𝖮𝖿 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾𝖽 𝖬𝗈𝗇𝗀𝗈𝖣𝖡 𝖴𝖱𝖨𝗌:</b>\n\n"

    import motor.motor_asyncio

    buttons = []
    for i, uri in enumerate(uris):
        status = "🔴"
        try:
            test_client = motor.motor_asyncio.AsyncIOMotorClient(uri, serverSelectionTimeoutMS=2000)
            await test_client.admin.command('ping')
            status = "🟢"
        except:
            pass

        truncated_uri = uri[:20] + "..." if len(uri) > 20 else uri
        text += f"{i+1}. <code>{truncated_uri}</code> - {status}\n"

    buttons.append([InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="db_settings")])

    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)


