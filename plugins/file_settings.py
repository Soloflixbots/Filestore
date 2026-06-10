from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout
from plugins.settings import send_settings_panel

@Client.on_callback_query(filters.regex("^file_settings$"))
async def file_settings_entry(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    await file_settings_panel(client, query)

async def file_settings_panel(client: Client, query: CallbackQuery):
    """Generates and displays the Files Related Settings panel."""
    protect_enabled = getattr(client, 'protect', False)
    hide_caption_enabled = getattr(client, 'hide_caption', False)
    button_enabled = getattr(client, 'channel_button_enabled', False)
    button_name = getattr(client, 'button_name', "Not Set")
    button_url = getattr(client, 'button_url', "Not Set")

    protect_status = "𝖤𝗇𝖺𝖻𝗅𝖾𝖽 ✔" if protect_enabled else "𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽 ✘"
    caption_status = "𝖤𝗇𝖺𝖻𝗅𝖾𝖽 ✔" if hide_caption_enabled else "𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽 ✘"
    button_status = "𝖤𝗇𝖺𝖻𝗅𝖾𝖽 ✔" if button_enabled else "𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽 ✘"
    caption = f"""<blockquote><b>✧ 𝖥𝗂𝗅𝖾𝗌 𝖱𝖾𝗅𝖺𝗍𝖾𝖽 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌</b></blockquote>
<pre><b>🔒 𝖯𝗋𝗈𝗍𝖾𝖼𝗍 𝖢𝗈𝗇𝗍𝖾𝗇𝗍: {protect_status}</b></pre>
<pre><b>🫥 𝖧𝗂𝖽𝖾 𝖢𝖺𝗉𝗍𝗂𝗈𝗇: {caption_status}</b></pre>
<pre><b>🔘 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖡𝗎𝗍𝗍𝗈𝗇: {button_status}</b></pre>
<blockquote><b>›› 𝖡𝗎𝗍𝗍𝗈𝗇 𝖣𝖾𝗍𝖺𝗂𝗅𝗌</b>\n
<b>›› 𝖡𝗎𝗍𝗍𝗈𝗇 𝖭𝖺𝗆𝖾:</b> <code>{button_name}</code>
<b>›› 𝖡𝗎𝗍𝗍𝗈𝗇 𝖫𝗂𝗇𝗄:</b> <code>{button_url}</code></blockquote>\n
<b>𝖢𝗅𝗂𝖼𝗄 𝖡𝖾𝗅𝗈𝗐 𝖡𝗎𝗍𝗍𝗈𝗇𝗌 𝖳𝗈 𝖢𝗁𝖺𝗇𝗀𝖾 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌</b>"""

    protect_btn_text = f"✦ 𝖯𝗋𝗈𝗍𝖾𝖼𝗍 𝖢𝗈𝗇𝗍𝖾𝗇𝗍: {'✔' if not protect_enabled else '✘'}"
    caption_btn_text = f"✦ 𝖧𝗂𝖽𝖾 𝖢𝖺𝗉𝗍𝗂𝗈𝗇: {'✔' if not hide_caption_enabled else '✘'}"
    button_btn_text = f"✦ 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖡𝗎𝗍𝗍𝗈𝗇: {'✔' if not button_enabled else '✘'}"

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(protect_btn_text, callback_data="toggle_protect"), InlineKeyboardButton(caption_btn_text, callback_data="toggle_hide_caption")],
        [InlineKeyboardButton(button_btn_text, callback_data="toggle_channel_button"), InlineKeyboardButton("✦ 𝖲𝖾𝗍 𝖡𝗎𝗍𝗍𝗈𝗇 ➪", callback_data="set_button")],
        [InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="settings_pg2"), InlineKeyboardButton("✦ 𝖢𝗅𝗈𝗌𝖾 ✘", callback_data="close")]
    ])
    await send_settings_panel(client, query, caption, reply_markup)

@Client.on_callback_query(filters.regex("^toggle_protect$"))
async def toggle_protect_content(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    client.protect = not getattr(client, 'protect', False)
    await client.mongodb.save_bot_setting('protect_content', client.protect)
    await query.answer(f"𝖯𝗋𝗈𝗍𝖾𝖼𝗍 𝖢𝗈𝗇𝗍𝖾𝗇𝗍 𝗂𝗌 𝗇𝗈𝗐 {'𝖤𝗇𝖺𝖻𝗅𝖾𝖽' if client.protect else '𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽'}")
    await file_settings_panel(client, query)

@Client.on_callback_query(filters.regex("^toggle_hide_caption$"))
async def toggle_hide_caption(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    client.hide_caption = not getattr(client, 'hide_caption', False)
    await client.mongodb.save_bot_setting('hide_caption', client.hide_caption)
    await query.answer(f"𝖧𝗂𝖽𝖾 𝖢𝖺𝗉𝗍𝗂𝗈𝗇 𝗂𝗌 𝗇𝗈𝗐 {'𝖤𝗇𝖺𝖻𝗅𝖾𝖽' if client.hide_caption else '𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽'}")
    await file_settings_panel(client, query)

@Client.on_callback_query(filters.regex("^toggle_channel_button$"))
async def toggle_channel_button(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    client.channel_button_enabled = not getattr(client, 'channel_button_enabled', False)
    await client.mongodb.save_bot_setting('channel_button_enabled', client.channel_button_enabled)
    await query.answer(f"𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖡𝗎𝗍𝗍𝗈𝗇 𝗂𝗌 𝗇𝗈𝗐 {'𝖤𝗇𝖺𝖻𝗅𝖾𝖽' if client.channel_button_enabled else '𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽'}")
    await file_settings_panel(client, query)

@Client.on_callback_query(filters.regex("^set_button$"))
async def set_button_details(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    await query.message.delete()
    prompt = await client.send_message(
        query.from_user.id,
        "𝖯𝗅𝖾𝖺𝗌𝖾 𝗌𝖾𝗇𝖽 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇 𝖽𝖾𝗍𝖺𝗂𝗅𝗌 𝗂𝗇 𝗍𝗁𝖾 𝖿𝗈𝗅𝗅𝗈𝗐𝗂𝗇𝗀 𝖿𝗈𝗋𝗆𝖺𝗍:\n\n`𝖡𝗎𝗍𝗍𝗈𝗇 𝖭𝖺𝗆𝖾 | 𝗁𝗍𝗍𝗉𝗌://𝗒𝗈𝗎𝗋-𝗅𝗂𝗇𝗄.𝖼𝗈𝗆`",
        parse_mode=ParseMode.MARKDOWN
    )
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=120)
        parts = res.text.split('|', 1)
        if len(parts) == 2:
            button_name = parts[0].strip()
            button_url = parts[1].strip()
            if button_url.startswith("http"):
                client.button_name = button_name
                client.button_url = button_url
                await client.mongodb.save_bot_setting('button_name', button_name)
                await client.mongodb.save_bot_setting('button_url', button_url)
                await res.reply("✔ 𝖡𝗎𝗍𝗍𝗈𝗇 𝖽𝖾𝗍𝖺𝗂𝗅𝗌 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝗎𝗉𝖽𝖺𝗍𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒!")
            else:
                await res.reply("❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖴𝗋𝗅. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗆𝖺𝗄𝖾 𝗌𝗎𝗋𝖾 𝗍𝗁𝖾 𝗅𝗂𝗇𝗄 𝗌𝗍𝖺𝗋𝗍𝗌 𝗐𝗂𝗍𝗁 `𝗁𝗍𝗍𝗉` 𝗈𝗋 `𝗁𝗍𝗍𝗉𝗌`.")
        else:
            await res.reply("❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖿𝗈𝗋𝗆𝖺𝗍. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗎𝗌𝖾 `𝖭𝖺𝗆𝖾 | 𝖴𝗋𝗅`.")
    except ListenerTimeout:
        await prompt.edit("<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍! 𝖭𝗈 𝖼𝗁𝖺𝗇𝗀𝖾𝗌 𝗐𝖾𝗋𝖾 𝗆𝖺𝖽𝖾.</b>")
    await file_settings_panel(client, query)
