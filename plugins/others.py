from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.enums import ParseMode
from config import MSG_EFFECT

async def send_start_message(client: Client, message_or_query):
    """
    A single, robust function to send the start message.
    Handles both /start command (Message) and Home button (CallbackQuery)
    and correctly manages transitions between photo and text messages.
    """
    is_callback = isinstance(message_or_query, CallbackQuery)
    if is_callback:
        message = message_or_query.message
        user = message_or_query.from_user
        await message_or_query.answer()
    else:
        message = message_or_query
        user = message_or_query.from_user

    start_photo = client.messages.get('START_PHOTO', '')
    buttons = [[InlineKeyboardButton("✦ 𝖠𝖻𝗈𝗎𝗍", callback_data="about"), InlineKeyboardButton("✦ 𝖢𝗅𝗈𝗌𝖾", callback_data="close")]]
    if user.id in client.admins:
        buttons.insert(0, [InlineKeyboardButton("✦ 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌 ⛩️", callback_data="settings")])
    start_text = client.messages.get('START', '𝖭𝗈 𝖲𝗍𝖺𝗋𝗍 𝖬𝖾𝗌𝗌𝖺𝗀𝖾').format(
        first=user.first_name,
        last=user.last_name or "",
        username=f'@{user.username}' if user.username else 'None',
        mention=user.mention,
        id=user.id
    )
    reply_markup = InlineKeyboardMarkup(buttons)

    if start_photo:
        if is_callback and message.photo:
            await message.edit_media(media=InputMediaPhoto(media=start_photo, caption=start_text), reply_markup=reply_markup)
        else:
            if is_callback: await message.delete()
            await client.send_photo(chat_id=message.chat.id, photo=start_photo, caption=start_text, reply_markup=reply_markup)
    else:
        if is_callback and not message.photo:
            await message.edit_text(text=start_text, reply_markup=reply_markup)
        else:
            if is_callback: await message.delete()
            await client.send_message(chat_id=message.chat.id, text=start_text, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex('^home$'))
async def home(client: Client, query: CallbackQuery):
    """Handles the 'Home' button by calling the master start message function."""
    await send_start_message(client, query)

@Client.on_callback_query(filters.regex('^about$'))
async def about(client: Client, query: CallbackQuery):
    await query.answer()
    buttons = [[InlineKeyboardButton("✦ 𝖧𝗈𝗆𝖾", callback_data="home"), InlineKeyboardButton("✦ 𝖢𝗅𝗈𝗌𝖾", callback_data="close")]]
    about_text = client.messages.get('ABOUT', '𝖭𝗈 𝖠𝖻𝗈𝗎𝗍 𝖬𝖾𝗌𝗌𝖺𝗀𝖾').format(
        owner_id=client.owner,
        bot_username=client.username,
        bot_name=getattr(client, 'bot_name', 'File Store Bot'),
        first=query.from_user.first_name,
        last=query.from_user.last_name or "",
        username=f'@{query.from_user.username}' if query.from_user.username else 'None',
        mention=query.from_user.mention,
        id=query.from_user.id
    )
    about_photo = client.messages.get('ABOUT_PHOTO', '')
    if about_photo:
        if query.message.photo:
            await query.message.edit_media(media=InputMediaPhoto(media=about_photo, caption=about_text), reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await query.message.delete()
            await client.send_photo(chat_id=query.message.chat.id, photo=about_photo, caption=about_text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        if query.message.photo:
            await query.message.delete()
            await client.send_message(query.message.chat.id, about_text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await query.message.edit_text(text=about_text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_message(filters.command('ban'))
async def ban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id_str in user_ids.split():
            user_id = int(user_id_str)
            c += 1
            if user_id in client.admins: continue
            if not await client.mongodb.present_user(user_id, client.me.id):
                await client.mongodb.add_user(user_id, client.me.id, True)
            else:
                await client.mongodb.ban_user(user_id)
        return await message.reply(f"__{c} 𝗎𝗌𝖾𝗋𝗌 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖻𝖺𝗇𝗇𝖾𝖽!__")
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")

@Client.on_message(filters.command('unban'))
async def unban(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    try:
        user_ids = message.text.split(maxsplit=1)[1]
        c = 0
        for user_id_str in user_ids.split():
            user_id = int(user_id_str)
            c += 1
            if user_id in client.admins: continue
            if not await client.mongodb.present_user(user_id, client.me.id):
                await client.mongodb.add_user(user_id, client.me.id)
            else:
                await client.mongodb.unban_user(user_id)
        return await message.reply(f"__{c} 𝗎𝗌𝖾𝗋𝗌 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝗎𝗇𝖻𝖺𝗇𝗇𝖾𝖽!__")
    except Exception as e:
        return await message.reply(f"**Error:** `{e}`")

@Client.on_callback_query(filters.regex('^close$'))
async def close(client: Client, query: CallbackQuery):
    await query.message.delete()
    try:
        if query.message.reply_to_message:
            await query.message.reply_to_message.delete()
    except:
        pass