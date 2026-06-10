from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait
from pyrogram.errors.pyromod import ListenerTimeout
from helper.helper_func import is_bot_admin

async def fsub(client, query):
    """
    Displays the Force Subscribe management menu with detailed status for each channel.
    """
    channel_list_text = ""
    if client.fsub_dict:
        channel_lines = []
        for channel_id, data in client.fsub_dict.items():
            name = data[0]
            is_request = data[2]
            timer = data[3]
            request_text = "✓ 𝖱𝖾𝗊𝗎𝖾𝗌𝗍" if is_request else "✗ 𝖣𝗂𝗋𝖾𝖼𝗍"
            timer_text = f"{timer}𝗆" if timer > 0 else "☠ 𝖯𝖾𝗋𝗆𝖺𝗇𝖾𝗇𝗍"
            line = f"• <b>{name}</b>\n(<code>{channel_id}</code>) - <b>{request_text}</b> - <b>𝖳𝗂𝗆𝖾𝗋:</b> {timer_text}"
            channel_lines.append(line)

        channel_list_text = "\n\n".join(channel_lines)
    else:
        channel_list_text = "› <i>𝖭𝗈𝗇𝖾 𝖼𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾𝖽.</i>"

    msg = f"""<blockquote><b>✧ 𝖥𝗈𝗋𝖼𝖾 𝖲𝗎𝖻𝗌𝖼𝗋𝗂𝗉𝗍𝗂𝗈𝗇 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌</b></blockquote>
<b>›› 𝖢𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾𝖽 𝖢𝗁𝖺𝗇𝗇𝖾𝗅𝗌:</b>
{channel_list_text}

<i>𝖴𝗌𝖾 𝗍𝗁𝖾 𝖺𝗉𝗉𝗋𝗈𝗉𝗋𝗂𝖺𝗍𝖾 𝖻𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗐 𝗍𝗈 𝖺𝖽𝖽 𝗈𝗋 𝗋𝖾𝗆𝗈𝗏𝖾 𝖺 𝖿𝗈𝗋𝖼𝖾 𝗌𝗎𝖻𝗌𝖼𝗋𝗂𝖻𝖾 𝖼𝗁𝖺𝗇𝗇𝖾𝗅!</i>
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('✦ 𝖠𝖽𝖽 𝖢𝗁𝖺𝗇𝗇𝖾𝗅', 'add_fsub'), InlineKeyboardButton('✦ 𝖱𝖾𝗆𝗈𝗏𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅', 'rm_fsub')],
        [InlineKeyboardButton('✦ 𝖡𝖺𝖼𝗄', 'settings_pg1')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex('^add_fsub$'))
async def add_fsub(client: Client, query: CallbackQuery):
    """
    Handles adding a new channel to the force subscribe list and updates the live dictionary.
    """
    await query.answer()
    prompt_message = await query.message.edit_text(
        """<blockquote><b>➕ 𝖠𝖽𝖽 𝖠 𝖥𝗈𝗋𝖼𝖾 𝖲𝗎𝖻 𝖢𝗁𝖺𝗇𝗇𝖾𝗅</b></blockquote>
𝖯𝗅𝖾𝖺𝗌𝖾 𝗌𝖾𝗇𝖽 𝗍𝗁𝖾 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝖽𝖾𝗍𝖺𝗂𝗅𝗌 𝗂𝗇 𝗍𝗁𝗂𝗌 𝖿𝗈𝗋𝗆𝖺𝗍:
<code>𝖢𝗁𝖺𝗇𝗇𝖾𝗅_𝖨𝖽 𝖱𝖾𝗊𝗎𝖾𝗌𝗍_𝖤𝗇𝖺𝖻𝗅𝖾𝖽 𝖳𝗂𝗆𝖾𝗋_𝗂𝗇_𝖬𝗂𝗇𝗎𝗍𝖾𝗌</code>

<b>𝖤𝗑𝖺𝗆𝗉𝗅𝖾:</b> <code>-𝟣𝟢𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫 𝗒𝖾𝗌 𝟧</code>
› <code>-𝟣𝟢𝟢...</code> 𝗂𝗌 𝗍𝗁𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝖽.
› <code>𝗒𝖾𝗌</code> 𝖾𝗇𝖺𝖻𝗅𝖾𝗌 𝗋𝖾𝗊𝗎𝖾𝗌𝗍-𝗍𝗈-𝗃𝗈𝗂𝗇 𝗅𝗂𝗇𝗄𝗌. 𝖴𝗌𝖾 <code>𝗇𝗈</code> 𝖿𝗈𝗋 𝗉𝗎𝖻𝗅𝗂𝖼 𝗂𝗇𝗏𝗂𝗍𝖾 𝗅𝗂𝗇𝗄𝗌.
› <code>𝟧</code> 𝗆𝖾𝖺𝗇𝗌 𝗍𝗁𝖾 𝗅𝗂𝗇𝗄 𝗐𝗂𝗅𝗅 𝖾𝗑𝗉𝗂𝗋𝖾 𝖺𝖿𝗍𝖾𝗋 𝟧 𝗆𝗂𝗇𝗎𝗍𝖾𝗌. 𝖴𝗌𝖾 <code>𝟢</code> 𝖿𝗈𝗋 𝖺 𝗇𝗈𝗇-𝖾𝗑𝗉𝗂𝗋𝗂𝗇𝗀 𝗅𝗂𝗇𝗄.
""", parse_mode=ParseMode.HTML)
    try:
        response_message = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=90)
        channel_info = response_message.text.split()
        if len(channel_info) != 3:
            return await response_message.reply("<b>𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖿𝗈𝗋𝗆𝖺𝗍.</b> 𝖯𝗅𝖾𝖺𝗌𝖾 𝗉𝗋𝗈𝗏𝗂𝖽𝖾 𝖺𝗅𝗅 𝗍𝗁𝗋𝖾𝖾 𝗏𝖺𝗅𝗎𝖾𝗌 𝖺𝗌 𝗋𝖾𝗊𝗎𝖾𝗌𝗍𝖾𝖽.", parse_mode=ParseMode.HTML)
        channel_id_str, request_str, timer_str = channel_info
        channel_id = int(channel_id_str)
        if any(channel[0] == channel_id for channel in client.fsub):
            return await response_message.reply("<b>𝖳𝗁𝗂𝗌 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝖽 𝖺𝗅𝗋𝖾𝖺𝖽𝗒 𝖾𝗑𝗂𝗌𝗍𝗌 𝗂𝗇 𝗍𝗁𝖾 𝖿𝗈𝗋𝖼𝖾 𝗌𝗎𝖻 𝗅𝗂𝗌𝗍.</b>", parse_mode=ParseMode.HTML)
        val, res = await is_bot_admin(client, channel_id)
        if not val:
            return await response_message.reply(f"<b>𝖤𝗋𝗋𝗈𝗋:</b> <code>{res}</code>", parse_mode=ParseMode.HTML)
        request = request_str.lower() in ('true', 'on', 'yes')
        timer = int(timer_str)

        client.fsub.append([channel_id, request, timer])
        chat = await client.get_chat(channel_id)
        name = chat.title
        link = None
        if timer <= 0:
            try:
                if not request and chat.invite_link:
                    link = chat.invite_link
                else:
                    invite = await client.create_chat_invite_link(channel_id, creates_join_request=request)
                    link = invite.invite_link
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Couldn't create invite link for {channel_id}: {e}")
        client.fsub_dict[channel_id] = [name, link, request, timer]
        await client.mongodb.save_settings(client.name, client.get_current_settings())
        await response_message.reply(f"✅ 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 <b>{name}</b> (<code>{channel_id}</code>) 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝖺𝖽𝖽𝖾𝖽 𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒.", parse_mode=ParseMode.HTML)
    except ListenerTimeout:
        await prompt_message.edit_text("<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍! 𝖭𝗈 𝖼𝗁𝖺𝗇𝗀𝖾𝗌 𝗐𝖾𝗋𝖾 𝗆𝖺𝖽𝖾.</b>")
    except Exception as e:
        await query.message.reply(f"<b>𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽:</b> <code>{e}</code>", parse_mode=ParseMode.HTML)
    await fsub(client, query)

@Client.on_callback_query(filters.regex('^rm_fsub$'))
async def rm_fsub(client: Client, query: CallbackQuery):
    await query.answer()
    prompt_message = await query.message.edit_text(
        "<blockquote><b>➖ 𝖱𝖾𝗆𝗈𝗏𝖾 𝖺 𝖥𝗈𝗋𝖼𝖾 𝖲𝗎𝖻 𝖢𝗁𝖺𝗇𝗇𝖾𝗅</b></blockquote>\n𝖯𝗅𝖾𝖺𝗌𝖾 𝗌𝖾𝗇𝖽 𝗍𝗁𝖾 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝖽 𝗈𝖿 𝗍𝗁𝖾 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝗐𝖺𝗇𝗍 𝗍𝗈 𝗋𝖾𝗆𝗈𝗏𝖾.",
        parse_mode=ParseMode.HTML
    )
    try:
        response_message = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=60)
        channel_id = int(response_message.text)
        if not any(channel[0] == channel_id for channel in client.fsub):
            return await response_message.reply("<b>𝖳𝗁𝗂𝗌 𝖼𝗁𝖺𝗇𝗇𝖾𝗅 𝖨𝖽 𝗂𝗌 𝗇𝗈𝗍 𝗂𝗇 𝗍𝗁𝖾 𝖿𝗈𝗋𝖼𝖾 𝗌𝗎𝖻 𝗅𝗂𝗌𝗍!</b>", parse_mode=ParseMode.HTML)
        client.fsub = [channel for channel in client.fsub if channel[0] != channel_id]
        removed_channel = client.fsub_dict.pop(channel_id, None)
        await client.mongodb.save_settings(client.name, client.get_current_settings())
        channel_name = f"<b>{removed_channel[0]}</b> " if removed_channel else ""
        await response_message.reply(f"✅ 𝖢𝗁𝖺𝗇𝗇𝖾𝗅 {channel_name}(<code>{channel_id}</code>) 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗋𝖾𝗆𝗈𝗏𝖾𝖽.", parse_mode=ParseMode.HTML)
    except ListenerTimeout:
        await prompt_message.edit_text("<b>𝖳𝗂𝗆𝖾𝗈𝗎𝗍! 𝖭𝗈 𝖼𝗁𝖺𝗇𝗀𝖾𝗌 𝗐𝖾𝗋𝖾 𝗆𝖺𝖽𝖾.</b>")
    except Exception as e:
        await query.message.reply(f"<b>𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽:</b> <code>{e}</code>", parse_mode=ParseMode.HTML)
    await fsub(client, query)

