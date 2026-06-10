from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.pyromod import ListenerTimeout
from plugins.settings import send_settings_panel

async def texts(client, query):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    msg = f"""<blockquote>**✧ 𝖳𝖾𝗑𝗍 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖺𝗍𝗂𝗈𝗇:**</blockquote>
**›› 𝖲𝗍𝖺𝗋𝗍 𝖬𝖾𝗌𝗌𝖺𝗀𝖾::**
<pre>{client.messages.get('START', '𝖤𝗆𝗉𝗍𝗒')}</pre>
**›› 𝖥𝗈𝗋𝖼𝖾 𝖲𝗎𝖻 𝖬𝖾𝗌𝗌𝖺𝗀𝖾:**
<pre>{client.messages.get('FSUB', '𝖤𝗆𝗉𝗍𝗒')}</pre>
**›› 𝖠𝖻𝗈𝗎𝗍 𝖬𝖾𝗌𝗌𝖺𝗀𝖾:**
<pre>{client.messages.get('ABOUT', '𝖤𝗆𝗉𝗍𝗒')}</pre>
**›› 𝖱𝖾𝗉𝗅𝗒 𝖬𝖾𝗌𝗌𝖺𝗀𝖾:**
<pre>{client.reply_text}</pre>
    """
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f'✦ 𝖲𝗍𝖺𝗋𝗍 𝖳𝖾𝗑𝗍', 'start_txt'), InlineKeyboardButton(f'✦ 𝖥𝗌𝗎𝖻 𝖳𝖾𝗑𝗍', 'fsub_txt')],
        [InlineKeyboardButton('✦ 𝖱𝖾𝗉𝗅𝗒 𝖳𝖾𝗑𝗍', 'reply_txt'), InlineKeyboardButton('✦ 𝖠𝖻𝗈𝗎𝗍 𝖳𝖾𝗑𝗍', 'about_txt')],
        [InlineKeyboardButton('✦ 𝖡𝖺𝖼𝗄', 'settings_pg2')]
    ])
    await send_settings_panel(client, query, msg, reply_markup)

async def handle_text_update(client, query, key, prompt):
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    await query.answer()
    try:
        ask_text = await client.ask(query.from_user.id, prompt, filters=filters.text, timeout=60)
        text = ask_text.text
        if text.lower() == 'cancel':
            await ask_text.reply("🚫 𝖠𝖼𝗍𝗂𝗈𝗇 𝖼𝖺𝗇𝼨𝖾𝗅𝗅𝖾𝖽. 𝖭𝗈 𝖼𝗁𝖺𝗇𝗀𝖾𝗌 𝗐𝖾𝗋𝖾 𝗆𝖺𝖽𝖾.")
            await texts(client, query)
            return

        if key == 'REPLY':
            client.reply_text = text
        else:
            client.messages[key] = text
        await client.mongodb.save_settings(client.name, client.get_current_settings())
        await ask_text.reply(f"✅ **{key.replace('_', ' ').title()}** 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗎𝗉𝖽𝖺𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒!")
        await texts(client, query)
    except ListenerTimeout:
        await client.send_message(query.from_user.id, "**𝖳𝗂𝗆𝖾𝗈𝗎𝗍! 𝖭𝗈 𝖼𝗁𝖺𝗇𝗀𝖾𝗌 𝗐𝖾𝗋𝖾 𝗆𝖺𝖽𝖾.**")
    except Exception as e:
        client.LOGGER(__name__, client.name).error(e)
        await client.send_message(query.from_user.id, f"An error occurred: {e}")

@Client.on_callback_query(filters.regex("^start_txt$"))
async def start_txt(client: Client, query: CallbackQuery):
    await handle_text_update(client, query, 'START', "𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝗇𝖾𝗐 **𝖲𝗍𝖺𝗋𝗍 𝖬𝖾𝗌𝗌𝖺𝗀𝖾** 𝗍𝖾𝗑𝗍. 𝖳𝗒𝗉𝖾 `𝖼𝖺𝗇𝼨𝖾𝗅` 𝗍𝗈 𝖺𝖻𝗈𝗋𝗍.")

@Client.on_callback_query(filters.regex("^fsub_txt$"))
async def force_txt(client: Client, query: CallbackQuery):
    await handle_text_update(client, query, 'FSUB', "𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝗇𝖾𝗐 **𝖥𝗈𝗋𝖼𝖾 𝖲𝗎𝖻𝗌𝖼𝗋𝗂𝖻𝖾** 𝗍𝖾𝗑𝗍. 𝖳𝗒𝗉𝖾 `𝖼𝖺𝗇𝼨𝖾𝗅` 𝗍𝗈 𝖺𝖻𝗈𝗋𝗍.")

@Client.on_callback_query(filters.regex("^about_txt$"))
async def about_txt(client: Client, query: CallbackQuery):
    await handle_text_update(client, query, 'ABOUT', "𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝗇𝖾𝗐 **𝖠𝖻𝗈𝗎𝗍 𝖬𝖾𝗌𝗌𝖺𝗀𝖾** 𝗍𝖾𝗑𝗍. 𝖳𝗒𝗉𝖾 `𝖼𝖺𝗇𝼨𝖾𝗅` 𝗍𝗈 𝖺𝖻𝗈𝗋𝗍.")

@Client.on_callback_query(filters.regex("^reply_txt$"))
async def reply_txt(client: Client, query: CallbackQuery):
    await handle_text_update(client, query, 'REPLY', "𝖲𝖾𝗇𝖽 𝗍𝗁𝖾 𝗇𝖾𝗐 𝖽𝖾𝖿𝖺𝗎𝗅𝗍 **𝖱𝖾𝗉𝗅𝗒 𝖬𝖾𝗌𝗌𝖺𝗀𝖾** 𝗍𝖾𝗑𝗍 𝖿𝗈𝗋 𝗎𝗇𝖺𝗎𝗍𝗁𝗈𝗋𝗂𝗓𝖾𝖽 𝗎𝗌𝖾𝗋𝗌. 𝖳𝗒𝗉𝖾 `𝖼𝖺𝗇𝼨𝖾𝗅` 𝗍𝗈 𝖺𝖻𝗈𝗋𝗍.")
