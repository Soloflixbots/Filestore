from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout
from datetime import timedelta
from plugins.settings import send_settings_panel

def get_readable_time_string(seconds: int) -> str:
    """Converts seconds into a human-readable string like '15 Minutes'."""
    if not seconds or seconds == 0:
        return "𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽"
    delta = timedelta(seconds=seconds)
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, sec = divmod(rem, 60)

    if days > 0: return f"{days} 𝖣𝖺𝗒{'𝗌' if days > 1 else ''}"
    if hours > 0: return f"{hours} 𝖧𝗈𝗎𝗋{'𝗌' if hours > 1 else ''}"
    if minutes > 0: return f"{minutes} 𝖬𝗂𝗇𝗎𝗍𝖾{'𝗌' if minutes > 1 else ''}"
    return f"{sec} 𝖲𝖾𝖼𝗈𝗇𝖽{'𝗌' if sec > 1 else ''}"

@Client.on_callback_query(filters.regex("^auto_del$"))
async def auto_del_entry(client: Client, query: CallbackQuery):
    """Main entry point for the Auto Delete settings panel."""
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    await auto_del_panel(client, query)

async def auto_del_panel(client: Client, query: CallbackQuery):
    """Generates and displays the Auto Delete settings panel."""
    is_enabled = client.auto_del > 0
    status_text = "𝖤𝗇𝖺𝖻𝗅𝖾𝖽 ✅" if is_enabled else "𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽 ❌"
    timer_text = get_readable_time_string(client.auto_del)

    del_text = client.messages.get('AUTO_DEL_TEXT', '𝖭𝗈𝗍 𝖲𝖾𝗍')
    del_pic = '𝖠𝖽𝖽𝖾𝖽' if client.messages.get('AUTO_DEL_PHOTO') else '𝖭𝗈𝗍 𝖠𝖽𝖽𝖾𝖽'

    caption = f"""<blockquote><b>✧ 𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌</b></blockquote>

<b><blockquote>🗑️ 𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖬𝗈𝖽𝖾: {status_text}</blockquote></b>
<b><blockquote>⏱ 𝖣𝖾𝗅𝖾𝗍𝖾 𝖳𝗂𝗆𝖾𝗋: {timer_text}</blockquote></b>
<b><blockquote>🖼️ 𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖯𝗂𝖼: {del_pic}</blockquote></b>

<b><blockquote>📝 𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖳𝖾𝗑𝗍:</blockquote></b>
<pre>{del_text}</pre>

<b>𝖢𝗅𝗂𝖼𝗄 𝖡𝖾𝗅𝗈𝗐 𝖡𝗎𝗍𝗍𝗈𝗇𝗌 𝖳𝗈 𝖢𝗁𝖺𝗇𝗀𝖾 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌</b>"""

    toggle_button_text = "𝖣𝗂𝗌𝖺𝖻𝗅𝖾 𝖬𝗈𝖽𝖾 ❌" if is_enabled else "𝖤𝗇𝖺𝖻𝗅𝖾 𝖬𝗈𝖽𝖾 ✅"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_button_text, callback_data="auto_del_toggle"), InlineKeyboardButton("✦ 𝖲𝖾𝗍 𝖳𝗂𝗆𝖾𝗋", callback_data="auto_del_set_timer")],
        [InlineKeyboardButton("✦ 𝖲𝖾𝗍 𝖳𝖾𝗑𝗍", callback_data="auto_del_set_text"), InlineKeyboardButton("✦ 𝖲𝖾𝗍 𝖯𝗂𝖼", callback_data="auto_del_set_pic")],
        [InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="settings_pg1"), InlineKeyboardButton("✦ 𝖢𝗅𝗈𝗌𝖾", callback_data="close")]
    ])
    await send_settings_panel(client, query, caption, reply_markup)

@Client.on_callback_query(filters.regex("^auto_del_toggle$"))
async def auto_del_toggle(client: Client, query: CallbackQuery):
    """Toggles the auto-delete mode on or off."""
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    if client.auto_del > 0:
        client.auto_del = 0
        await query.answer("𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽!", show_alert=True)
    else:
        client.auto_del = 900
        await query.answer("𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖤𝗇𝖺𝖻𝗅𝖾𝖽! (𝖣𝖾𝖿𝖺𝗎𝗅𝗍: 𝟣𝟧 𝖬𝗂𝗇𝗎𝗍𝖾𝗌)", show_alert=True)

    await client.mongodb.save_settings(client.name, client.get_current_settings())
    await auto_del_panel(client, query)

@Client.on_callback_query(filters.regex("^auto_del_set_timer$"))
async def set_auto_del_timer(client: Client, query: CallbackQuery):
    """Prompts the user to set a new auto-delete timer."""
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.message.delete()
    prompt_message = await client.send_message(
        chat_id=query.from_user.id,
        text="<blockquote><b>⏱️ 𝖲𝖾𝗍 𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖳𝗂𝗆𝖾𝗋</b></blockquote>\n\n𝖤𝗇𝗍𝖾𝗋 𝗍𝗁𝖾 𝗇𝖾𝗐 𝗍𝗂𝗆𝖾𝗋 𝗏𝖺𝗅𝗎𝖾 𝗂𝗇 <b>𝗌𝖾𝖼𝗈𝗇𝖽𝗌</b>.\n\n𝖥𝗈𝗋 𝖾𝗑𝖺𝗆𝗉𝗅𝖾, 𝗍𝗈 𝗌𝖾𝗍 𝗂𝗍 𝗍𝗈 𝟣𝟧 𝗆𝗂𝗇𝗎𝗍𝖾𝗌, 𝖾𝗇𝗍𝖾𝗋 `𝟫𝟢𝟢`.",
        parse_mode=ParseMode.HTML
    )
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=60)
        timer_str = res.text.strip()
        if timer_str.lower() == 'cancel':
            await res.reply("🚫 𝖠𝖼𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝼨𝖾𝗅𝗅𝖾𝖽.")
        else:
            timer = int(timer_str)
            if timer >= 0:
                client.auto_del = timer
                await client.mongodb.save_settings(client.name, client.get_current_settings())
                await res.reply(f'✅ 𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝗍𝗂𝗆𝖾𝗋 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗌𝖾𝗍 𝗍𝗈 <b>{get_readable_time_string(timer)}</b>!', parse_mode=ParseMode.HTML)
            else:
                await res.reply("❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗂𝗇𝗉𝗎𝗍. 𝖯𝗅𝖾𝖺𝗌𝖾 𝖾𝗇𝗍𝖾𝗋 𝖺 𝗇𝗈𝗇-𝗇𝖾𝗀𝖺𝗍𝗂𝗏𝖾 𝗇𝗎𝗆𝖻𝖾𝗋.")
    except ListenerTimeout:
        await prompt_message.edit("<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍! 𝖭𝗈 𝖼𝗁𝖺𝗇𝗀𝖾𝗌 𝗐𝖾𝗋𝖾 𝗆𝖺𝖽𝖾.</b>")
    except ValueError:
        await prompt_message.reply("<b>❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗂𝗇𝗉𝗎𝗍. 𝖯𝗅𝖾𝖺𝗌𝖾 𝖾𝗇𝗍𝖾𝗋 𝖺 𝗏𝖺𝗅𝗂𝖽 𝗇𝗎𝗆𝖻𝖾𝗋 𝗈𝖿 𝗌𝖾𝖼𝗈𝗇𝖽𝗌.</b>")
    dummy_message = await client.send_message(query.from_user.id, "𝖫𝗈𝖺𝖽𝗂𝗇𝗀 𝗌𝖾𝗍𝗍𝗂𝗇𝗀𝗌...")
    query.message = dummy_message
    await auto_del_panel(client, query)
    await dummy_message.delete()

@Client.on_callback_query(filters.regex("^auto_del_set_text$"))
async def auto_del_set_text(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    try:
        ask = await client.ask(query.from_user.id, "𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝗇𝖾𝗐 **𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖶𝖺𝗋𝗇𝗂𝗇𝗀 𝖳𝖾𝗑𝗍**.\n𝖴𝗌𝖾 `{time}` 𝗉𝗅𝖺𝖼𝖾𝗁𝗈𝗅𝖽𝖾𝗋 𝖿𝗈𝗋 𝗍𝗁𝖾 𝗍𝗂𝗆𝖾𝗋. 𝖳𝗒𝗉𝖾 `cancel` 𝗍𝗈 𝖺𝖻𝗈𝗋𝗍.", timeout=120)
        if ask.text:
            if ask.text.lower() == 'cancel':
                await ask.reply("🚫 𝖠𝖼𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝼨𝖾𝗅𝗅𝖾𝖽.")
            else:
                client.messages['AUTO_DEL_TEXT'] = ask.text
                await client.mongodb.save_settings(client.name, client.get_current_settings())
                await ask.reply("✅ **𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖳𝖾𝗑𝗍** 𝗎𝗉𝖽𝖺𝗍𝖾𝖽!")
        else:
            await ask.reply("❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗂𝗇𝗉𝗎𝗍! 𝖯𝗅𝖾𝖺𝗌𝖾 𝗌𝖾𝗇𝖽 𝗍𝖾𝗑𝗍.")
    except ListenerTimeout:
        await client.send_message(query.from_user.id, "<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍!</b>")
    await auto_del_panel(client, query)

@Client.on_callback_query(filters.regex("^auto_del_set_pic$"))
async def auto_del_set_pic(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    try:
        ask = await client.ask(query.from_user.id, "𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝗇𝖾𝗐 **𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖶𝖺𝗋𝗇𝗂𝗇𝗀 𝖯𝗂𝖼** (𝖯𝗁𝗈𝗍𝗈 𝗈𝗋 𝖴𝖱𝖫).\n𝖲𝖾𝗇𝖽 `remove` 𝗍𝗈 𝖽𝖾𝗅𝖾𝗍𝖾 𝗂𝗍. 𝖳𝗒𝗉𝖾 `cancel` 𝗍𝗈 𝖺𝖻𝗈𝗋𝗍.", timeout=120)
        if ask.text and ask.text.lower() == 'cancel':
            await ask.reply("🚫 𝖠𝖼𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝼨𝖾𝗅𝗅𝖾𝖽.")
        elif ask.text and ask.text.lower() == "remove":
            client.messages['AUTO_DEL_PHOTO'] = ""
            await client.mongodb.save_settings(client.name, client.get_current_settings())
            await ask.reply("✅ **𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖯𝗂𝖼** 𝗋𝖾𝗆𝗈𝗏𝖾𝖽!")
        elif ask.photo:
            client.messages['AUTO_DEL_PHOTO'] = ask.photo.file_id
            await client.mongodb.save_settings(client.name, client.get_current_settings())
            await ask.reply("✅ **𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖯𝗂𝖼** 𝗎𝗉𝖽𝖺𝗍𝖾𝖽!")
        elif ask.text and ask.text.startswith("http"):
            client.messages['AUTO_DEL_PHOTO'] = ask.text
            await client.mongodb.save_settings(client.name, client.get_current_settings())
            await ask.reply("✅ **𝖠𝗎𝗍𝗈 𝖣𝖾𝗅𝖾𝗍𝖾 𝖯𝗂𝖼** 𝗎𝗉𝖽𝖺𝗍𝖾𝖽!")
        else:
            await ask.reply("❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗂𝗇𝗉𝗎𝗍!")
    except ListenerTimeout:
        await client.send_message(query.from_user.id, "<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍!</b>")
    await auto_del_panel(client, query)
