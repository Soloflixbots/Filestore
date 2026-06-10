import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from helper.helper_func import encode, get_redirect_link

async def is_not_numeric_reply(_, __, message: Message):
    if message.text and message.text.isdigit():
        return False
    return True

not_numeric_filter = filters.create(is_not_numeric_reply)

@Client.on_message(
    filters.private &
    ~filters.command(['start', 'settings', 'users', 'broadcast', 'batch', 'genlink', 'usage', 'pbroadcast', 'ban', 'unban', 'autobatch', 'database', 'createpost', 'dbroadcast', 'reset', 'anime', 'search', 'progress', 'verify', 'connect', 'connections']) &
    not_numeric_filter
)
async def channel_post(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    if not client.db:
        return await message.reply("❌ <b>𝖭𝗈 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾 𝖼𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾𝖽.</b>", parse_mode=ParseMode.HTML)
    reply_text = await message.reply_text("⏳ <b>𝖯𝗋𝗈𝖼𝖾𝗌𝗌𝗂𝗇𝗀 𝖿𝗂𝗅𝖾...</b>", quote=True, parse_mode=ParseMode.HTML)
    try:
        post_message = await message.copy(chat_id=client.db, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id=client.db, disable_notification=True)
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error: {e}")
        await reply_text.edit_text(f"❌ <b>𝖴𝗉𝗅𝗈𝖺𝖽 𝖿𝖺𝗂𝗅𝖾𝖽:</b> <code>{e}</code>", parse_mode=ParseMode.HTML)
        return
    string = f"single_{post_message.chat.id}_{post_message.id}"
    base64_string = await encode(string)
    current_bot_link = await get_redirect_link(client, base64_string)
    response_text = (
        f"<b>✅ 𝖥𝗂𝗅𝖾 𝖴𝗉𝗅𝗈𝖺𝖽𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒!</b>\n\n"
        f"<b>🔗 𝖣𝗂𝗋𝖾𝖼𝗍 𝖫𝗂𝗇𝗄:</b>\n"
        f"<code>{current_bot_link}</code>\n\n"
        f"<b>🆔 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖨𝖽:</b> <code>{post_message.id}</code>"
    )
    buttons = [
        [InlineKeyboardButton("✦ 𝖢𝗅𝗂𝖼𝗄 𝖧𝖾𝗋𝖾 𝖿𝗈𝗋 𝖥𝗂𝗅𝖾𝗌 •", url=current_bot_link)]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await reply_text.edit_text(
        response_text,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML
    )
    backup_db_id = client.databases.get('backup')
    if backup_db_id:
        try:
            backup_msg = await post_message.copy(backup_db_id)
            await client.mongodb.add_backup_mapping(
                post_message.chat.id,
                post_message.id,
                backup_msg.id
            )
            client.LOGGER(__name__, client.name).info(
                f"✅ Instant backup: {post_message.id} → backup:{backup_msg.id}"
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            try:
                backup_msg = await post_message.copy(backup_db_id)
                await client.mongodb.add_backup_mapping(
                    post_message.chat.id,
                    post_message.id,
                    backup_msg.id
                )
            except Exception as retry_error:
                client.LOGGER(__name__, client.name).warning(f"Backup failed: {retry_error}")
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Backup failed: {e}")
    if not client.disable_btn:
        db_channel_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("✦ 𝖦𝖾𝗍 𝖥𝗂𝗅𝖾", url=current_bot_link)]
        ])
        try:
            await post_message.edit_reply_markup(db_channel_markup)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Could not add button: {e}")

@Client.on_message(filters.channel & filters.incoming)
async def new_post(client: Client, message: Message):
    if message.chat.id not in client.all_db_ids:
        return
    if client.disable_btn:
        return

    string = f"single_{message.chat.id}_{message.id}"
    base64_string = await encode(string)
    current_bot_link = await get_redirect_link(client, base64_string)
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✦ 𝖦𝖾𝗍 𝖥𝗂𝗅𝖾", url=current_bot_link)]
    ])
    try:
        await message.edit_reply_markup(reply_markup)
        client.LOGGER(__name__, client.name).info(f"Added button to message {message.id}")
    except Exception as e:
        client.LOGGER(__name__, client.name).warning(f"Could not add button: {e}")
