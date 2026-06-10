
import os
import sys
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout
from config import OWNER_ID, DEFAULT_MESSAGES
from plugins.settings import send_settings_panel

@Client.on_callback_query(filters.regex("^clone_bot$"))
async def clone_bot_cb(client, query):
    if client.name.startswith("clone_"):
        return await query.answer("𝖳𝗁𝗂𝗌 𝖠𝖼𝗍𝗂𝗈𝗇 𝖨𝗌 𝖭𝗈𝗍 𝖠𝗅𝗅𝗈𝗐𝖾𝖽 𝖥𝗈𝗋 𝖢𝗅𝗈𝗇𝖾 𝖡𝗈𝗍𝗌!", show_alert=True)
    if query.from_user.id != OWNER_ID:
        return await query.answer("𝖳𝗁𝗂𝗌 𝖠𝖼𝗍𝗂𝗈𝗇 𝖨𝗌 𝖮𝗇𝗅𝗒 𝖥𝗈𝗋 𝖮𝗐𝗇𝖾𝗋!", show_alert=True)

    await query.answer()

    msg = await query.message.edit_text(
        "<b><blockquote>🤖 𝖢𝗅𝗈𝗇𝖾 𝖡𝗈𝗍 𝖲𝖾𝗍𝗎𝗉</blockquote>\n\n𝖲𝖾𝗇𝖽 𝖳𝗁𝖾 𝖡𝗈𝗍 𝖳𝗈𝗄𝖾𝗇 𝖮𝖿 𝖳𝗁𝖾 𝖡𝗈𝗍 𝖸𝗈𝗎 𝖶𝖺𝗇𝗍 𝖳𝗈 𝖢𝗅𝗈𝗇𝖾.</b>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✦ 𝖢𝖺𝗇𝖼𝖾𝗅", callback_data="settings_pg2")]]),
        parse_mode=ParseMode.HTML
    )

    try:
        token_msg = await client.listen(chat_id=query.from_user.id, timeout=120)
        bot_token = token_msg.text.strip()
        await token_msg.delete()
    except ListenerTimeout:
        return await msg.edit_text("<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍! 𝖯𝗅𝖾𝖺𝗌𝖾 𝖳𝗋𝗒 𝖠𝗀𝖺𝗂𝗇.</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="settings_pg2")]]))

    db_uri = client.raw_config['db_uri']
    db_name = client.raw_config['db_name']

    wait_msg = await msg.edit_text("<b>𝖵𝖺𝗅𝗂𝖽𝖺𝗍𝗂𝗇𝗀 𝖳𝗈𝗄𝖾𝗇... 𝖯𝗅𝖾𝖺𝗌𝖾 𝖶𝖺𝗂𝗍.</b>")

    try:
        temp_client = Client(
            name=f"temp_{query.from_user.id}",
            api_id=client.raw_config['api_id'],
            api_hash=client.raw_config['api_hash'],
            bot_token=bot_token,
            in_memory=True
        )
        await temp_client.start()
        me = await temp_client.get_me()
        await temp_client.stop()
    except Exception as e:
        return await wait_msg.edit_text(f"<b>❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖳𝗈𝗄𝖾𝗇 𝖮𝗋 𝖠𝖯𝖨 𝖤𝗋𝗋𝗈𝗋:</b>\n<code>{e}</code>")

    clone_config = {
        "session": f"clone_{me.id}",
        "token": bot_token,
        "username": me.username,
        "api_id": client.raw_config['api_id'],
        "api_hash": client.raw_config['api_hash'],
        "workers": 8,
        "db_uri": db_uri,
        "db_name": db_name,
        "fsubs": [],
        "databases": {"primary": 0, "secondary": [], "backup": None},
        "auto_del": 600,
        "messages": DEFAULT_MESSAGES,
        "admins": [],
        "disable_btn": True,
        "protect": False
    }

    await client.mongodb.add_clone(bot_token, clone_config)

    redirectors = getattr(client, 'redirector_username', [])
    if not isinstance(redirectors, list):
        redirectors = [redirectors] if redirectors else []

    if me.username not in redirectors:
        redirectors.append(me.username)
        client.redirector_username = redirectors
        await client.mongodb.save_bot_setting('redirector_username', redirectors)

    await wait_msg.edit_text(
        f"<b>✅ 𝖡𝗈𝗍 𝖢𝗅𝗈𝗇𝖾𝖽 𝖲𝗎𝖼𝖼𝖾𝗌𝖿𝗎𝗅𝗅𝗒!\n\n🤖 𝖡𝗈𝗍: @{me.username}\n\n𝖳𝗁𝖾 𝖡𝗈𝗍 𝖶𝗂𝗅𝗅 𝖡𝖾 𝖠𝖼𝗍𝗂𝗏𝖾 𝖠𝖿𝗍𝖾𝗋 𝖱𝖾𝗌𝗍𝖺𝗋𝗍.</b>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✦ 𝖱𝖾𝗌𝗍𝖺𝗋𝗍 𝖭𝗈𝗐", callback_data="restart_bot")]])
    )

async def clone_list(client, query):
    if client.name.startswith("clone_"):
        return await query.answer("𝖳𝗁𝗂𝗌 𝖠𝖼𝗍𝗂𝗈𝗇 𝖨𝗌 𝖭𝗈𝗍 𝖠𝗅𝗅𝗈𝗐𝖾𝖽 𝖥𝗈𝗋 𝖢𝗅𝗈𝗇𝖾 𝖡𝗈𝗍𝗌!", show_alert=True)
    if query.from_user.id != OWNER_ID:
        return await query.answer("𝖳𝗁𝗂𝗌 𝖠𝖼𝗍𝗂𝗈𝗇 𝖨𝗌 𝖮𝗇𝗅𝗒 𝖥𝗈𝗋 𝖮𝗐𝗇𝖾𝗋!", show_alert=True)
    await query.answer()
    clones = await client.mongodb.get_clones()
    if not clones:
        caption = "<b><blockquote>🤖 𝖢𝗅𝗈𝗇𝖾𝖽 𝖡𝗈𝗍𝗌 𝖫𝗂𝗌𝗍</blockquote>\n\n𝖭𝗈 𝖢𝗅𝗈𝗇𝖾𝖽 𝖡𝗈𝗍𝗌 𝖥𝗈𝗎𝗇𝖽!</b>"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="settings_pg2")]])
        return await send_settings_panel(client, query, caption, reply_markup)

    caption = "<b><blockquote>🤖 𝖢𝗅𝗈𝗇𝖾𝖽 𝖡𝗈𝗍𝗌 𝖫𝗂𝗌𝗍</blockquote>\n\n𝖫𝗂𝗌𝗍 𝖮𝖿 𝖠𝗅𝗅 𝖠𝖼𝗍𝗂𝗏𝖾 𝖢𝗅𝗈𝗇𝖾𝖽 𝖡𝗈𝗍𝗌:</b>\n\n"
    buttons = []
    for i, config in enumerate(clones):
        token = config.get('token', 'Unknown')
        username = config.get('username')
        display_name = f"@{username}" if username else (token[:10] + "..." + token[-5:] if len(token) > 15 else token)
        caption += f"{i+1}. <code>{display_name}</code>\n"
        buttons.append([InlineKeyboardButton(f"✦ 𝖱𝖾𝗆𝗈𝗏𝖾 {display_name}", callback_data=f"rm_clone_{token}")])

    buttons.append([InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="settings_pg2")])
    await send_settings_panel(client, query, caption, InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^rm_clone_"))
async def rm_clone_cb(client, query):
    if client.name.startswith("clone_"):
        return await query.answer("𝖳𝗁𝗂𝗌 𝖠𝖼𝗍𝗂𝗈𝗇 𝖨𝗌 𝖭𝗈𝗍 𝖠𝗅𝗅𝗈𝗐𝖾𝖽 𝖥𝗈𝗋 𝖢𝗅𝗈𝗇𝖾 𝖡𝗈𝗍𝗌!", show_alert=True)
    if query.from_user.id != OWNER_ID:
        return await query.answer("𝖳𝗁𝗂𝗌 𝖠𝖼𝗍𝗂𝗈𝗇 𝖨𝗌 𝖮𝗇𝗅𝗒 𝖥𝗈𝗋 𝖮𝗐𝗇𝖾𝗋!", show_alert=True)
    token = query.data.replace("rm_clone_", "")

    redirectors = getattr(client, 'redirector_username', [])
    if not isinstance(redirectors, list):
        redirectors = [redirectors] if redirectors else []

    clones = await client.mongodb.get_clones()
    for config in clones:
        if config.get('token') == token:
            username = config.get('username')
            if username and username in redirectors:
                redirectors.remove(username)
                client.redirector_username = redirectors
                await client.mongodb.save_bot_setting('redirector_username', redirectors)
            break

    await client.mongodb.remove_clone(token)
    await query.answer("𝖢𝗅𝗈𝗇𝖾 𝖱𝖾𝗆𝗈𝗏𝖾𝖽! 𝖱𝖾𝗌𝗍𝖺𝗋𝗍 𝖳𝗈 𝖠𝗉𝗉𝗅𝗒 𝖢𝗁𝖺𝗇𝗀𝖾𝗌.", show_alert=True)
    await clone_list(client, query)

@Client.on_callback_query(filters.regex("^restart_bot$"))
async def restart_bot_cb(client, query):
    if query.from_user.id != OWNER_ID:
        return await query.answer("𝖮𝗇𝗅𝗒 𝖮𝗐𝗇𝖾𝗋 𝖢𝖺𝗇 𝖱𝖾𝗌𝗍𝖺𝗋𝗍!", show_alert=True)
    await query.message.edit_text("<b>𝖱𝖾𝗌𝗍𝖺𝗋𝗍𝗂𝗇𝗀... 𝖯𝗅𝖾𝖺𝗌𝖾 𝖶𝖺𝗂𝗍 𝖠 𝖬𝗂𝗇𝗎𝗍𝖾.</b>")
    os.execl(sys.executable, sys.executable, *sys.argv)
