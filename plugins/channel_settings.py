from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout
from plugins.settings import send_settings_panel

async def channel_settings_panel(client: Client, query: CallbackQuery):
    """Generates and displays the Channel Related Settings panel."""
    expiry_mins = getattr(client, 'channel_link_expiry', 10)

    caption = f"""<blockquote><b>✧ 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖫𝗂𝗇𝗄 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌</b></blockquote>
<pre><b>⏰ 𝖫𝗂𝗇𝗄 𝖤𝗑𝗉𝗂𝗋𝗒: {expiry_mins} 𝖬𝗂𝗇𝗎𝗍𝖾𝗌</b></pre>

<i>𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝗅𝗂𝗇𝗄𝗌 (𝖭𝗈𝗋𝗆𝖺𝗅 & 𝖱𝖾𝗊𝗎𝖾𝗌𝗍) 𝗐𝗂𝗅𝗅 𝖺𝗎𝗍𝗈𝗆𝖺𝗍𝗂𝖼𝖺𝗅𝗅𝗒 𝖾𝗑𝗉𝗂𝗋𝖾 𝖺𝖿𝗍𝖾𝗋 𝗍𝗁𝗂𝗌 𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇.</i>

<b>𝖢𝗅𝗂𝖼𝗄 𝖡𝖾𝗅𝗈𝗐 𝖡𝗎𝗍𝗍𝗈𝗇𝗌 𝖳𝗈 𝖢𝗁𝖺𝗇𝗀𝖾 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌</b>"""

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✦ 𝖲𝖾𝗍 𝖤𝗑𝗉𝗂𝗋𝗒 𝖳𝗂𝗆𝖾", callback_data="set_channel_expiry")],
        [InlineKeyboardButton("✦ 𝖠𝖽𝖽 𝖢𝗁𝖺𝗇𝗇𝖾𝗅", callback_data="add_ch"), InlineKeyboardButton("✦ 𝖣𝖾𝗅𝖾𝗍𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅", callback_data="del_ch")],
        [InlineKeyboardButton("✦ 𝖲𝗁𝗈𝗐 𝖢𝗁𝖺𝗇𝗇𝖾𝗅𝗌", callback_data="show_chs"), InlineKeyboardButton("✦ 𝖲𝗁𝗈𝗐 𝖫𝗂𝗇𝗄𝗌", callback_data="show_lnks")],
        [InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="settings_pg2"), InlineKeyboardButton("✦ 𝖢𝗅𝗈𝗌𝖾 ✘", callback_data="close")]
    ])
    await send_settings_panel(client, query, caption, reply_markup)

@Client.on_callback_query(filters.regex("^set_channel_expiry$"))
async def set_channel_expiry(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()

    prompt = await client.send_message(
        query.from_user.id,
        "<b>𝖯𝗅𝖾𝖺𝗌𝖾 𝗌𝖾𝗇𝖽 𝗍𝗁𝖾 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗅𝗂𝗇𝗄 𝖾𝗑𝗉𝗂𝗋𝗒 𝖽𝗎𝗋𝖺𝗍𝗂𝗈𝗇 𝗂𝗇 𝗆𝗂𝗇𝗎𝗍𝖾𝗌 (𝖾.𝗀., 𝟧 𝗈𝗋 𝟣𝟢).</b>\n\n"
        "<i>𝖴𝗌𝖾 `𝟢` 𝖿𝗈𝗋 𝗉𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍 𝗅𝗂𝗇𝗄𝗌 (𝗇𝗈𝗍 𝗋𝖾𝖼𝗈𝗆𝗆𝖾𝗇𝖽𝖾𝖽).</i>",
        parse_mode=ParseMode.HTML
    )

    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=60)
        try:
            duration = int(res.text)
            if duration < 0:
                raise ValueError

            client.channel_link_expiry = duration
            await client.mongodb.save_bot_setting('channel_link_expiry', duration)
            await res.reply(f"✅ 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝗅𝗂𝗇𝗄 𝖾𝗑𝗉𝗂𝗋𝗒 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗌𝖾𝗍 𝗍𝗈 <b>{duration} 𝗆𝗂𝗇𝗎𝗍𝖾𝗌</b>.", parse_mode=ParseMode.HTML)
        except ValueError:
            await res.reply("❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗂𝗇𝗉𝗎𝗍. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗌𝖾𝗇𝖽 𝖺 𝗉𝗈𝗌𝗂𝗍𝗂𝗏𝖾 𝗇𝗎𝗆𝖾𝗋𝗂𝖼 𝗏𝖺𝗅𝗎𝖾.")
    except ListenerTimeout:
        await prompt.edit("<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍! 𝖭𝗈 𝖼𝗁𝖺𝗇𝗀𝖾𝗌 𝗐𝖾𝗋𝖾 𝗆𝖺𝖽𝖾.</b>")

    await channel_settings_panel(client, query)
