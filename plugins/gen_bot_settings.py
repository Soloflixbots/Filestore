from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout
from plugins.settings import send_settings_panel

async def gen_bot_settings_panel(client: Client, query: CallbackQuery):
    """Generates and displays the Link Generation Bot Settings panel."""
    link_gen_bot = getattr(client, 'link_gen_bot', None)

    status = f"@{link_gen_bot}" if link_gen_bot else "𝖣𝖾𝖿𝖺𝗎𝗅𝗍 (𝖱𝖺𝗇𝖽𝗈𝗆/𝖢𝗎𝗋𝗋𝖾𝗇𝗍)"

    caption = f"""<blockquote><b>✧ 𝖫𝗂𝗇𝗄 𝖦𝖾𝗇𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖡𝗈𝗍</b></blockquote>
<pre><b>🤖 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖡𝗈𝗍: {status}</b></pre>

<i>𝖲𝖾𝗍 𝖺 𝗌𝗉𝖾𝖼𝗂𝖿𝗂𝖼 𝖻𝗈𝗍 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾 𝗍𝗈 𝖻𝖾 𝗎𝗌𝖾𝖽 𝖿𝗈𝗋 𝖺𝗅𝗅 𝗀𝖾𝗇𝖾𝗋𝖺𝗍𝖾𝖽 𝗅𝗂𝗇𝗄𝗌. 𝖨𝖿 𝗇𝗈𝗍 𝗌𝖾𝗍, 𝗍𝗁𝖾 𝖻𝗈𝗍 𝗐𝗂𝗅𝗅 𝗎𝗌𝖾 𝗋𝖾𝖽𝗂𝗋𝖾𝖼𝗍𝗈𝗋 𝖻𝗈𝗍𝗌 𝗈𝗋 𝗂𝗍𝗌𝖾𝗅𝖿.</i>

<b>𝖢𝗅𝗂𝖼𝗄 𝖡𝖾𝗅𝗈𝗐 𝖡𝗎𝗍𝗍𝗈𝗇𝗌 𝖳𝗈 𝖢𝗁𝖺𝗇𝗀𝖾 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌</b>"""

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✦ 𝖲𝖾𝗍 𝖡𝗈𝗍 𝖴𝗌𝖾𝗋𝗇𝖺𝗆𝖾", callback_data="set_gen_bot")],
        [InlineKeyboardButton("✦ 𝖱𝖾𝗌𝖾𝗍 𝖳𝗈 𝖣𝖾𝖿𝖺𝗎𝗅𝗍", callback_data="reset_gen_bot")],
        [InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="settings_pg2"), InlineKeyboardButton("✦ 𝖢𝗅𝗈𝗌𝖾 ✘", callback_data="close")]
    ])
    await send_settings_panel(client, query, caption, reply_markup)

@Client.on_callback_query(filters.regex("^set_gen_bot$"))
async def set_gen_bot(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()

    prompt = await client.send_message(
        query.from_user.id,
        "<b>𝖯𝗅𝖾𝖺𝗌𝖾 𝗌𝖾𝗇𝖽 𝗍𝗁𝖾 𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾 𝗈𝖿 𝗍𝗁𝖾 𝖻𝗈𝗍 (𝖾.𝗀., <code>MyFileBot</code> 𝗈𝗋 <code>@MyFileBot</code>).</b>",
        parse_mode=ParseMode.HTML
    )

    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=60)
        username = res.text.strip().replace("@", "")

        client.link_gen_bot = username
        await client.mongodb.save_bot_setting('link_gen_bot', username)
        await res.reply(f"✅ 𝖫𝗂𝗇𝗄 𝗀𝖾𝗇𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖻𝗈𝗍 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗌𝖾𝗍 𝗍𝗈 <b>@{username}</b>.", parse_mode=ParseMode.HTML)
    except ListenerTimeout:
        await prompt.edit("<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍! 𝖭𝗈 𝖼𝗁𝖺𝗇𝗀𝖾𝗌 𝗐𝖾𝗋𝖾 𝗆𝖺𝖽𝖾.</b>")

    await gen_bot_settings_panel(client, query)

@Client.on_callback_query(filters.regex("^reset_gen_bot$"))
async def reset_gen_bot(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)

    client.link_gen_bot = None
    await client.mongodb.save_bot_setting('link_gen_bot', None)
    await query.answer("✅ 𝖫𝗂𝗇𝗄 𝗀𝖾𝗇𝖾𝗋𝖺𝗍𝗂𝗈𝗇 𝖻𝗈𝗍 𝗋𝖾𝗌𝖾𝗍 𝗍𝗈 𝖽𝖾𝖿𝖺𝗎𝗅𝗍.", show_alert=True)
    await gen_bot_settings_panel(client, query)
