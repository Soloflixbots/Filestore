from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout
import re

async def send_settings_panel(client, query, caption, reply_markup):
    """Utility to send or edit the settings panel with optional photo."""
    settings_photo = client.messages.get('SETTINGS_PHOTO')

    message = getattr(query, 'message', query)

    try:
        if settings_photo:
            if message.photo:
                await message.edit_media(
                    media=InputMediaPhoto(media=settings_photo, caption=caption),
                    reply_markup=reply_markup
                )
            else:
                await message.delete()
                await client.send_photo(
                    chat_id=message.chat.id,
                    photo=settings_photo,
                    caption=caption,
                    reply_markup=reply_markup
                )
        else:
            if message.photo:
                await message.delete()
                await client.send_message(
                    chat_id=message.chat.id,
                    text=caption,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
            else:
                await message.edit_text(
                    text=caption,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML
                )
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error in send_settings_panel: {e}")
        try:
            if not message.photo:
                await message.edit_text(text=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await client.send_message(chat_id=message.chat.id, text=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
        except:
            pass

@Client.on_message(filters.command("settings") & filters.private)
async def settings_cmd(client, message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    await settings_page_1(client, message)

@Client.on_callback_query(filters.regex("^settings$"))
async def settings_main(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await settings_page_1(client, query)

@Client.on_callback_query(filters.regex("^settings_pg1$"))
async def settings_page_1_cb(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await settings_page_1(client, query)

async def settings_page_1(client, query):
    await query.answer()
    caption = """<blockquote><b>⚙️ 𝖡𝗈𝗍 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌 (𝖯𝖺𝗀𝖾 𝟣/𝟤)</b></blockquote>
𝖴𝗌𝖾 𝖳𝗁𝖾 𝖡𝗎𝗍𝗍𝗈𝗇𝗌 𝖡𝖾𝗅𝗈𝗐 𝖳𝗈 𝖬𝖺𝗇𝖺𝗀𝖾 𝖳𝗁𝖾 𝖡𝗈𝗍'𝖲 𝖢𝗈𝗋𝖾 𝖥𝖾𝖺𝗍𝗎𝗋𝖾𝗌.
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✦ 𝖥𝗌𝗎𝖻 𝖢𝗁𝖺𝗇𝗇𝖾𝗅𝗌", callback_data="fsub"), InlineKeyboardButton("✦ 𝖣𝖻 𝖢𝗁𝖺𝗇𝗇𝖾𝗅𝗌", callback_data="db_settings")],
        [InlineKeyboardButton("✦ 𝖠𝖽𝗆𝗂𝗇𝗌", callback_data="admins"), InlineKeyboardButton("✦ 𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾", callback_data="auto_del")],
        [InlineKeyboardButton("✦ 𝖠𝗎𝗍𝗈𝖻𝖺𝗍𝖼𝗁 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌", callback_data="autobatch_settings")],
        [InlineKeyboardButton("✦ 𝖧𝗈𝗆𝖾", callback_data="home"), InlineKeyboardButton("✦ 𝖭𝖾𝗑𝗍", callback_data="settings_pg2")]
    ])
    await send_settings_panel(client, query, caption, reply_markup)

@Client.on_callback_query(filters.regex("^settings_pg2$"))
async def settings_page_2(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    caption = """<blockquote><b>⚙️ 𝖡𝗈𝗍 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌 (𝖯𝖺𝗀𝖾 𝟤/𝟤)</b></blockquote>
𝖴𝗌𝖾 𝖳𝗁𝖾 𝖡𝗎𝗍𝗍𝗈𝗇𝗌 𝖡𝖾𝗅𝗈𝗐 𝖳𝗈 𝖬𝖺𝗇𝖺𝗀𝖾 𝖳𝗁𝖾 𝖡𝗈𝗍'𝖲 𝖢𝗈𝗋𝖾 𝖥𝖾𝖺𝗍𝗎𝗋𝖾𝗌.
"""
    buttons = [
        [InlineKeyboardButton("✦ 𝖥𝗂𝗅𝖾𝗌 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌", callback_data="file_settings"), InlineKeyboardButton("✦ 𝖯𝗁𝗈𝗍𝗈𝗌", callback_data="photos")],
        [InlineKeyboardButton("✦ 𝖳𝖾𝗑𝗍𝗌", callback_data="texts"), InlineKeyboardButton("✦ 𝖵𝖾𝗋𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇", callback_data="verification_settings")],
        [InlineKeyboardButton("✦ 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌", callback_data="channel_settings"), InlineKeyboardButton("✦ 𝖱𝖾𝖽𝗂𝗋𝖾𝖼𝗍", callback_data="redirect")],
        [InlineKeyboardButton("✦ 𝖫𝗂𝗇𝗄 𝖡𝗈𝗍", callback_data="gen_bot_settings")]
    ]
    if not client.name.startswith("clone_"):
        buttons.append([InlineKeyboardButton("✦ 𝖢𝗅𝗈𝗇𝖾 𝖡𝗈𝗍", callback_data="clone_bot"), InlineKeyboardButton("✦ 𝖢𝗅𝗈𝗇𝖾 𝖫𝗂𝗌𝗍", callback_data="clone_list")])
    buttons.append([InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="settings_pg1"), InlineKeyboardButton("✦ 𝖧𝗈𝗆𝖾", callback_data="home")])
    reply_markup = InlineKeyboardMarkup(buttons)
    await send_settings_panel(client, query, caption, reply_markup)

@Client.on_callback_query(filters.regex("^photos$"))
async def photos(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    caption = f"""<blockquote><b>🖼️ 𝖬𝖾𝖽𝗂𝖺 & 𝖯𝗁𝗈𝗍𝗈𝗌</b></blockquote>
𝖲𝖾𝗍 𝗈𝗋 𝗋𝖾𝗆𝗈𝗏𝖾 𝗍𝗁𝖾 𝗂𝗆𝖺𝗀𝖾𝗌 𝗎𝗌𝖾𝖽 𝗂𝗇 𝗍𝗁𝖾 𝖻𝗈𝗍'𝗌 𝗆𝖾𝗌𝗌𝖺𝖦𝖾𝗌.

<b>›› 𝖲𝗍𝖺𝗋𝗍 𝖯𝗂𝖼 :</b> <code>{'𝖠𝖽𝖽𝖾𝖽' if client.messages.get('START_PHOTO') else '𝖭𝗈𝗍 𝖺𝖽𝖽𝖾𝖽'}</code>
<b>›› 𝖥𝗌𝗎𝖻 𝖯𝗂𝖼 :</b> <code>{'𝖠𝖽𝖽𝖾𝖽' if client.messages.get('FSUB_PHOTO') else '𝖭𝗈𝗍 𝖺𝖽𝖽𝖾𝖽'}</code>
<b>›› 𝖠𝖻𝗈𝗎𝗍 𝖯𝗂𝖼 :</b> <code>{'𝖠𝖽𝖽𝖾𝖽' if client.messages.get('ABOUT_PHOTO') else '𝖭𝗈𝗍 𝖺𝖽𝖽𝖾𝖽'}</code>
<b>›› 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌 𝖯𝗂𝖼 :</b> <code>{'𝖠𝖽𝖽𝖾𝖽' if client.messages.get('SETTINGS_PHOTO') else '𝖭𝗈𝗍 𝖺𝖽𝖽𝖾𝖽'}</code>
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✦ 𝖲𝗍𝖺𝗋𝗍 𝖯𝗂𝖼", callback_data="update_photo_START_PHOTO"), InlineKeyboardButton("✦ 𝖥𝗌𝗎𝖻 𝖯𝗂𝖼", callback_data="update_photo_FSUB_PHOTO")],
        [InlineKeyboardButton("✦ 𝖠𝖻𝗈𝗎𝗍 𝖯𝗂𝖼", callback_data="update_photo_ABOUT_PHOTO"), InlineKeyboardButton("✦ 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌 𝖯𝗂𝖼", callback_data="update_photo_SETTINGS_PHOTO")],
        [InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="settings_pg2")]
    ])
    await send_settings_panel(client, query, caption, reply_markup)

@Client.on_callback_query(filters.regex("^update_photo_"))
async def update_photo(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    key = query.data.replace("update_photo_", "")
    await query.answer()
    prompt_text = f"<blockquote>𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝖯𝗁𝗈𝗍𝗈 𝗈𝗋 𝖴𝖱𝖫 𝖿𝗈𝗋 **{key.replace('_', ' ').title()}**.\n𝖲𝖾𝗇𝖽 `𝗋𝖾𝗆𝗈𝗏𝖾` 𝗍𝗈 𝖽𝖾𝗅𝖾𝗍𝖾 𝗂𝗍.</blockquote>"
    if query.message.photo:
        msg = await query.message.edit_caption(caption=prompt_text, parse_mode=ParseMode.HTML)
    else:
        msg = await query.message.edit_text(prompt_text, parse_mode=ParseMode.HTML)

    try:
        res = await client.listen(chat_id=query.from_user.id, timeout=60)
        if res.text and res.text.lower() == "remove":
            client.messages[key] = ""
            await client.mongodb.save_settings(client.name, client.get_current_settings())
            await res.reply(f"✅ **{key.replace('_', ' ').title()}** 𝗋𝖾𝗆𝗈𝗏𝖾𝖽!")
        elif res.photo:
            client.messages[key] = res.photo.file_id
            await client.mongodb.save_settings(client.name, client.get_current_settings())
            await res.reply(f"✅ **{key.replace('_', ' ').title()}** 𝗎𝗉𝖽𝖺𝗍𝖾𝖽!")
        elif res.text and res.text.startswith("http"):
            client.messages[key] = res.text
            await client.mongodb.save_settings(client.name, client.get_current_settings())
            await res.reply(f"✅ **{key.replace('_', ' ').title()}** 𝗎𝗉𝖽𝖺𝗍𝖾𝖽!")
        else:
            await res.reply("❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗂𝗇𝗉𝗎𝗍!")
    except ListenerTimeout:
        if query.message.photo:
            await query.message.edit_caption("<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍!</b>")
        else:
            await query.message.edit_text("<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍!</b>")
    await photos(client, query)

@Client.on_callback_query(filters.regex("^clone_list$"))
async def clone_list_cb(client, query):
    from plugins.clone import clone_list
    await clone_list(client, query)

@Client.on_callback_query(filters.regex("^file_settings$"))
async def file_settings_cb(client, query):
    from plugins.file_settings import file_settings_panel
    await file_settings_panel(client, query)

@Client.on_callback_query(filters.regex("^fsub$"))
async def fsub_settings_cb(client, query):
    from plugins.force_sub import fsub
    await fsub(client, query)

@Client.on_callback_query(filters.regex("^db_settings$"))
async def db_settings_cb(client, query):
    from plugins.database_settings import db_settings
    await db_settings(client, query)

@Client.on_callback_query(filters.regex("^channel_settings$"))
async def channel_settings_cb(client, query):
    from plugins.channel_settings import channel_settings_panel
    await channel_settings_panel(client, query)

@Client.on_callback_query(filters.regex("^gen_bot_settings$"))
async def gen_bot_settings_cb(client, query):
    from plugins.gen_bot_settings import gen_bot_settings_panel
    await gen_bot_settings_panel(client, query)

@Client.on_callback_query(filters.regex("^admins$"))
async def admins_settings_cb(client, query):
    from plugins.admins import admins
    await admins(client, query)

@Client.on_callback_query(filters.regex("^texts$"))
async def texts_settings_cb(client, query):
    from plugins.texts import texts
    await texts(client, query)

@Client.on_callback_query(filters.regex("^redirect$"))
async def redirect_cb(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()

    try:
        payload_msg = await client.ask(
            query.from_user.id,
            "<b>𝖲𝖾𝗇𝖽 𝗆𝖾 𝗍𝗁𝖾 𝖯𝖺𝗒𝗅𝗈𝖺𝖽 𝗈𝗋 𝗍.𝗆𝖾 𝖫𝗂𝗇𝗄 (𝖾.𝗀. payload).</b>\n\n𝖳𝗒𝗉𝖾 `cancel` 𝗍𝗈 𝖺𝖻𝗈𝗋𝗍.",
            timeout=60,
            filters=filters.text
        )
        if not payload_msg or not payload_msg.text:
            return await settings_page_2(client, query)

        if payload_msg.text.lower() == "cancel":
            await payload_msg.reply("🚫 𝖠𝖼𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝼨𝖾𝗅𝗅𝖾𝖽.")
            return await settings_page_2(client, query)

        payload = payload_msg.text.strip()
        if "start=" in payload:
            payload = payload.split("start=")[1]

        alias_msg = await client.ask(
            query.from_user.id,
            "<b>𝖲𝖾𝗇𝖽 𝗆𝖾 𝗍𝗁𝖾 𝖢𝗎𝗌𝗍𝗈𝗆 𝖠𝗅𝗂𝖺𝗌 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗎𝗌𝖾 (𝖾.𝗀. Tom).</b>\n\n𝖳𝗒𝗉𝖾 `cancel` 𝗍𝗈 𝖺𝖻𝗈𝗋𝗍.",
            timeout=60,
            filters=filters.text
        )
        if not alias_msg or not alias_msg.text:
            return await settings_page_2(client, query)

        if alias_msg.text.lower() == "cancel":
            await alias_msg.reply("🚫 𝖠𝖼𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝼨𝖾𝗅𝗅𝖾𝖽.")
            return await settings_page_2(client, query)

        alias = alias_msg.text.strip()
        if not re.match(r'^[a-zA-Z0-9_]+$', alias):
            await alias_msg.reply("❌ <b>𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖠𝗅𝗂𝖺𝗌.</b> 𝖴𝗌𝖾 𝗈𝗇𝗅𝗒 𝖺𝗅𝗉𝗁𝖺𝗇𝗎𝗆𝖾𝗋𝗂𝖼 𝖼𝗁𝖺𝗋𝖺𝖼𝗍𝖾𝗋𝗌 𝖺𝗇𝖽 𝗎𝗇𝖽𝖾𝗋𝗌𝖼𝗈𝗋𝖾𝗌.")
            return await settings_page_2(client, query)

        await client.mongodb.save_alias(alias, payload)

        new_link = f"https://t.me/{client.username}?start={alias}"
        await alias_msg.reply(
            f"<b>✅ 𝖢𝗎𝗌𝗍𝗈𝗆 𝖱𝖾𝖽𝗂𝗋𝖾𝖼𝗍 𝖫𝗂𝗇𝗄 𝖦𝖾𝗇𝖾𝗋𝖺𝗍𝖾𝖽!</b>\n\n"
            f"<b>🔗 𝖮𝗋𝗂𝗀𝗂𝗇𝖺𝗅 𝖯𝖺𝗒𝗅𝗈𝖺𝖽:</b> <code>{payload}</code>\n"
            f"<b>🔗 𝖢𝗎𝗌𝗍𝗈𝗆 𝖫𝗂𝗇𝗄:</b> <code>{new_link}</code>\n\n"
            f"<i>𝖭𝗈𝗍𝖾: 𝖳𝗁𝗂𝗌 𝖺𝗅𝗂𝖺𝗌 𝗐𝗂𝗅𝗅 𝗐𝗈𝗋𝗄 𝗈𝗇 𝖺𝗅𝗅 𝖻𝗈𝗍𝗌 𝗌𝗁𝖺𝗋𝗂𝗇𝗀 𝗍𝗁𝖾 𝗌𝖺𝗆𝖾 𝖽𝖺𝗍𝖺𝖻𝖺𝗌𝖾.</i>",
            disable_web_page_preview=True,
            parse_mode=ParseMode.HTML
        )
    except ListenerTimeout:
        await client.send_message(query.from_user.id, "<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍!</b>")

    await settings_page_2(client, query)
