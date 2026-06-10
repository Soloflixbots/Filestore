from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, Message
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout
from plugins.settings import send_settings_panel

DEFAULT_AUTOBATCH_TEMPLATE = """<b>𝖦𝖾𝗇𝖾𝗋𝖺𝗍𝖾𝖽 𝖫𝗂𝗇𝗄𝗌 ({totalfilecount} 𝖿𝗂𝗅𝖾𝗌)</b>

<b><u>𝖵𝗂𝖽𝖾𝗈 𝖰𝗎𝖺𝗅𝗂𝗍𝗒:</u></b>
<blockquote>{4k} ({4kfilecount}): {4klink}
{1080p} ({1080pfilecount}): {1080plink}
{720p} ({720pfilecount}): {720plink}
{540p} ({540pfilecount}): {540plink}
{480p} ({480pfilecount}): {480plink}</blockquote>
<b><u>𝖲𝗈𝗎𝗋𝖼𝖾/𝖤𝗇𝖼𝗈𝖽𝗂𝗇𝗀:</u></b>
<blockquote>{hdrip} ({hdripfilecount}): {hdriplink}
{bluray} ({blurayfilecount}): {bluraylink}
{webdl} ({webdlfilecount}): {webdllink}
{hevc} ({hevcfilecount}): {hevclink}</blockquote>
<b><u>𝖮𝗍𝗁𝖾𝗋:</u></b>
<blockquote>{other} ({otherfilecount}): {otherlink}</blockquote>"""

PLACEHOLDERS_TEXT = """<b><blockquote>✧ 𝖠𝗏𝖺𝗂𝗅𝖺𝖻𝗅𝖾 𝖯𝗅𝖺𝗖𝖾𝗁𝗈𝗅𝖽𝖾𝗋𝗌 ✧</blockquote></b>
𝖸𝗈𝗎 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗍𝗁𝖾𝗌𝖾 𝗉𝗅𝖺𝖼𝖾𝗁𝗈𝗅𝖽𝖾𝗋𝗌 𝗂𝗇 𝗒𝗈𝗎𝗋 𝖼𝗎𝗌𝗍𝗈𝗆 𝗍𝖾𝗆𝗉𝗅𝖺𝗍𝖾. 𝖨𝖿 𝖺 𝗊𝗎𝖺𝗅𝗂𝗍𝗒 𝗂𝗌 𝗇𝗈𝗍 𝖿𝗈𝗎𝗇𝖽, 𝗂𝗍𝗌 𝗅𝗂𝗇𝖾 𝗐𝗂𝗅𝗅 𝖻𝖾 𝗋𝖾𝗆𝗈𝗏𝖾𝖽.

<b><u>𝖦𝖾𝗇𝖾𝗋𝖺𝗅:</u></b>
• <code>{totalfilecount}</code> - 𝖳𝗈𝗍𝖺𝗅 𝗇𝗎𝗆𝖻𝖾𝗋 𝗈𝖿 𝖿𝗂𝗅𝖾𝗌.
• <code>{totalepisodes}</code> - 𝖳𝗈𝗍𝖺𝗅 𝗇𝗎𝗆𝖻𝖾𝗋 𝗈𝖿 𝗎𝗇𝗂𝗊𝗎𝖾 𝖾𝗉𝗂𝗌𝗈𝖽𝖾𝗌.
• <code>{season}</code> - 𝖳𝗁𝖾 𝖽𝖾𝗍𝖾𝖼𝗍𝖾𝖽 𝗌𝖾𝖺𝗌𝗈𝗇(𝗌) (𝖾.𝗀., "𝟢𝟣", "𝟢𝟣-𝟢𝟥", "𝟢𝟣, 𝟢𝟥").
• <code>{sharinglink}</code> - 𝖳𝗁𝖾 𝖼𝗈𝗆𝖻𝗂𝗇𝖾𝖽 𝗌𝗁𝖺𝗋𝗂𝗇𝗀 𝗅𝗂𝗇𝗄 (𝗋𝖾𝖽𝗂𝗋𝖾𝖼𝗍𝗈𝗋).

<b><u>𝖥𝗈𝗋 𝖤𝖺𝖼𝗁 𝖰𝗎𝖺𝗅𝗂𝗍𝗒:</u></b>
𝖴𝗌𝖾 𝗍𝗁𝖾 **𝗅𝗈𝗐𝖾𝗋𝖼𝖺𝗌𝖾** 𝗇𝖺𝗆𝖾 𝖿𝗈𝗋 𝗍𝗁𝖾 𝗊𝗎𝖺𝗅𝗂𝗍𝗒:
<code>𝟦𝗄</code>, <code>𝟣𝟢𝟪𝟢𝗉</code>, <code>𝟩𝟤𝟢𝗉</code>, <code>𝟧𝟦𝟢𝗉</code>, <code>𝟦𝟪𝟢𝗉</code>, <code>𝗁𝖽𝗋𝗂𝗉</code>, <code>𝖻𝗅𝗎𝗋𝖺𝗒</code>, <code>𝗐𝖾𝖻𝖽𝗅</code>, <code>𝗁𝖾𝗏𝖼</code>, 𝗈𝗋 <code>𝗈𝗍𝗁𝖾𝗋</code>.

• <code>{quality}</code> - 𝖳𝗁𝖾 𝗅𝖺𝖻𝖾𝗅 (𝖾.𝗀., "𝖧𝖽𝗋𝗂𝗉").
• <code>{qualitylink}</code> - 𝖳𝗁𝖾 𝖽𝗂𝗋𝖾𝗖𝗍 𝖻𝗈𝗍 𝗅𝗂𝗇𝗄.
• <code>{qualityfilecount}</code> - 𝖳𝗁𝖾 𝗇𝗎𝗆𝖻𝖾𝗋 𝗈𝖿 𝖿𝗂𝗅𝖾𝗌.

<b><u>𝖤𝗑𝖺𝗆𝗉𝗅𝖾 𝖿𝗈𝗋 𝖧𝖽𝗋𝗂𝗉:</u></b>
<code>{hdrip} ({hdripfilecount} 𝖿𝗂𝗅𝖾𝗌) - {hdriplink}</code>"""

async def show_autobatch_panel(client: Client, message: Message):
    """Displays the Autobatch settings panel."""
    current_template = getattr(client, 'autobatch_template', DEFAULT_AUTOBATCH_TEMPLATE)
    caption = f"""<b><blockquote>✧ 𝖠𝗎𝗍𝗈𝖻𝖺𝗍𝖼𝗁 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌</blockquote></b>
<b>›› 𝖢𝗎𝗋𝗋𝖾𝗇𝗍 𝖳𝖾𝗆𝗉𝗅𝖺𝗍𝖾:</b>
<pre>{current_template}</pre>"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✦ 𝖲𝖾𝗍 𝖭𝖾𝗐 𝖳𝖾𝗆𝗉𝗅𝖺𝗍𝖾", callback_data="autobatch_set_template"), InlineKeyboardButton("✦ 𝖵𝗂𝖾𝗐 𝖯𝗅𝖺𝖼𝖾𝗁𝗈𝗅𝖽𝖾𝗋𝗌", callback_data="autobatch_placeholders")],
        [InlineKeyboardButton("✦ 𝖱𝖾𝗌𝖾𝗍 𝖳𝗈 𝖣𝖾𝖿𝖺𝗎𝗅𝗍", callback_data="autobatch_reset")],
        [InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="settings_pg1")]
    ])

    class FakeQuery:
        def __init__(self, message):
            self.message = message
    await send_settings_panel(client, FakeQuery(message), caption, reply_markup)

@Client.on_callback_query(filters.regex("^autobatch_settings$"))
async def autobatch_settings_cb(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    await show_autobatch_panel(client, query.message)

@Client.on_callback_query(filters.regex("^autobatch_set_template$"))
async def set_autobatch_template(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    await query.message.delete()

    prompt = await client.send_message(
        query.from_user.id,
        "𝖯𝗅𝖾𝖺𝗌𝖾 𝗌𝖾𝗇𝖽 𝗍𝗁𝖾 𝗇𝖾𝗐 𝗍𝖾𝗆𝗉𝗅𝖺𝗍𝖾 𝖿𝗈𝗋 𝗍𝗁𝖾 𝖺𝗎𝗍𝗈𝖻𝖺𝗍𝖼𝗁 𝖼𝗈𝗆𝗆𝖺𝗇𝖽. 𝖸𝗈𝗎 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗌𝗍𝖺𝗇𝖽𝖺𝗋𝖽 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗆 𝖧𝗍𝗆𝗅 𝖿𝗈𝗋𝗆𝖺𝗍𝗍𝗂𝗇𝗀 (𝖾.𝗀., `<b>`, `<code>`).\n\n𝖳𝗒𝗉𝖾 /𝖼𝖺𝗇𝼨𝖾𝗅 𝗍𝗈 𝖺𝖻𝗈𝗋𝗍.",
        parse_mode=ParseMode.HTML
    )
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=300)
        if res.text and res.text.lower() == "/cancel":
            await res.reply("🚫 𝖠𝖼𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝼨𝖾𝗅𝗅𝖾𝖽.")
        else:
            client.autobatch_template = res.text
            await client.mongodb.save_bot_setting('autobatch_template', client.autobatch_template)
            await res.reply("✅ 𝖠𝗎𝗍𝗈𝖻𝖺𝗍𝖼𝗁 𝗍𝖾𝗆𝗉𝗅𝖺𝗍𝖾 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗎𝗉𝖽𝖺𝗍𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒!")
    except ListenerTimeout:
        await prompt.reply("<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍! 𝖭𝗈 𝖼𝗁𝖺𝗇𝗀𝖾𝗌 𝗐𝖾𝗋𝖾 𝗆𝖺𝖽𝖾.</b>")
    await show_autobatch_panel(client, await client.send_message(query.from_user.id, "𝖫𝗈𝖺𝖽𝗂𝗇𝗀 𝗆𝖾𝗇𝗎..."))

@Client.on_callback_query(filters.regex("^autobatch_placeholders$"))
async def view_autobatch_placeholders(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    if query.message.photo:
        await query.message.edit_caption(
            caption=PLACEHOLDERS_TEXT,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="autobatch_settings")]])
        )
    else:
        await query.message.edit_text(
            text=PLACEHOLDERS_TEXT,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✦ 𝖡𝖺𝖼𝗄", callback_data="autobatch_settings")]]),
            parse_mode=ParseMode.HTML
        )

@Client.on_callback_query(filters.regex("^autobatch_reset$"))
async def reset_autobatch_template(client: Client, query: CallbackQuery):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    client.autobatch_template = DEFAULT_AUTOBATCH_TEMPLATE
    await client.mongodb.save_bot_setting('autobatch_template', client.autobatch_template)
    await query.answer("✅ 𝖳𝖾𝗆𝗉𝗅𝖺𝗍𝖾 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗋𝖾𝗌𝖾𝗍 𝗍𝗈 𝖽𝖾𝖿𝖺𝗎𝗅𝗍.", show_alert=True)
    await show_autobatch_panel(client, query.message)

