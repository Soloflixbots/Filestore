from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from plugins.settings import send_settings_panel

@Client.on_callback_query(filters.regex("^verification_settings$"))
async def verification_settings_cb(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    await show_verification_panel(client, query)

async def show_verification_panel(client, query):
    robot_check = getattr(client, 'robot_check', False)

    caption = f"""<blockquote><b>✧ 𝖵𝖾𝗋𝗂𝖿𝗂𝖼𝖺𝗍𝗂𝗈𝗇 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌</b></blockquote>

<b>›› 𝖱𝗈𝖻𝗈𝗍 𝖢𝗁𝖾𝖼𝗄:</b> <code>{'𝖤𝗇𝖺𝖻𝗅𝖾𝖽' if robot_check else '𝖣𝗂𝗌𝖺𝖻𝗅𝖾𝖽'}</code>

<i>𝖢𝗁𝗈𝗈𝗌𝖾 𝗁𝗈𝗐 𝗒𝗈𝗎 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗏𝖾𝗋𝗂𝖿𝗒 𝗒𝗈𝗎𝗋 𝗎𝗌𝖾𝗋𝗌.</i>"""

    buttons = [
        [
            InlineKeyboardButton(f"{'✅' if robot_check else '✦'} 𝖱𝗈𝖻𝗈𝗍 𝖢𝗁𝖾𝖼𝗄: {'𝖮𝖭' if robot_check else '𝖮𝖥𝖥'}", callback_data="toggle_robot_check")
        ],
        [InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="settings_pg2")]
    ]

    await send_settings_panel(client, query, caption, InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex("^toggle_robot_check$"))
async def toggle_robot_check_cb(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    client.robot_check = not getattr(client, 'robot_check', False)
    await client.mongodb.save_bot_setting('robot_check', client.robot_check)
    await query.answer(f"𝖱𝗈𝖻𝗈𝗍 𝖼𝗁𝖾𝖼𝗄 {'𝖾𝗇𝖺𝖻𝗅𝖾𝖽' if client.robot_check else '𝖽𝗂𝗌𝖺𝖻𝗅𝖾𝖽'}", show_alert=True)
    await show_verification_panel(client, query)
