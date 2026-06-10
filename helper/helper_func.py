
import base64
import re
import asyncio
import functools
import random
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.errors import UserNotParticipant, Forbidden, PeerIdInvalid, ChatAdminRequired, FloodWait
from datetime import datetime, timedelta, timezone
from pyrogram import errors

async def get_redirect_link(client: Client, payload: str, is_verify: bool = False, use_redirector: bool = True, expiry_mins: int = 0):
    link_gen_bot = getattr(client, 'link_gen_bot', None)
    if use_redirector and link_gen_bot:
        bot_username = link_gen_bot
    else:
        redirector = getattr(client, 'redirector_username', []) if use_redirector else []
        if not isinstance(redirector, list):
            redirector = [redirector] if redirector else []

        if redirector:
            others = [m for m in redirector if m.lower() != client.username.lower()]
            bot_username = random.choice(others) if others else random.choice(redirector)
        else:
            bot_username = client.username

    if expiry_mins > 0:
        temp_id = await client.mongodb.save_temp_link(payload, bot_username, expiry_mins)
        start_param = f"exp_{temp_id}"
    else:
        start_param = f"dl_{payload}" if is_verify else payload
        if len(start_param) > 64:
            short_id = await client.mongodb.save_short_link(payload, bot_username)
            start_param = f"dl_{short_id}" if is_verify else short_id

    return f"https://t.me/{bot_username}?start={start_param}"

async def encode(string):
    string_bytes = string.encode("utf-8")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("utf-8")).strip("=")
    return base64_string

async def decode(base64_string):
    try:
        base64_string = base64_string.strip("=")
        base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("utf-8")
        string_bytes = base64.urlsafe_b64decode(base64_bytes)
        string = string_bytes.decode("utf-8")
        return string
    except (base64.binascii.Error, UnicodeDecodeError):
        return None

async def get_messages(client, channel_id, message_ids):
    final_messages = {}
    ids_to_fetch = list(message_ids)
    try:
        all_raw_msgs = []
        for i in range(0, len(ids_to_fetch), 200):
            batch_ids = ids_to_fetch[i:i+200]
            try:
                msgs = await client.get_messages(chat_id=channel_id, message_ids=batch_ids)
                all_raw_msgs.extend(msgs)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                msgs = await client.get_messages(chat_id=channel_id, message_ids=batch_ids)
                all_raw_msgs.extend(msgs)

        successful_ids = {msg.id for msg in all_raw_msgs if msg}
        for msg in all_raw_msgs:
            if msg:
                final_messages[msg.id] = msg

        failed_ids = set(ids_to_fetch) - successful_ids
        backup_db_id = client.databases.get('backup')
        if backup_db_id and failed_ids:
            backup_map = {await client.mongodb.get_backup_msg_id(channel_id, o_id): o_id for o_id in failed_ids}
            backup_map = {k: v for k, v in backup_map.items() if k is not None}
            if backup_map:
                backup_msg_ids = list(backup_map.keys())
                for i in range(0, len(backup_msg_ids), 200):
                    batch_backup_ids = backup_msg_ids[i:i+200]
                    try:
                        backup_msgs = await client.get_messages(backup_db_id, batch_backup_ids)
                        for b_msg in backup_msgs:
                            if b_msg and b_msg.id in backup_map:
                                final_messages[backup_map[b_msg.id]] = b_msg
                    except FloodWait as e:
                        await asyncio.sleep(e.x)
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error in get_messages: {e}")
    return [final_messages.get(og_id) for og_id in message_ids if og_id in final_messages]

async def get_message_id(client, message: Message):
    chat_id, msg_id = (None, None)

    if message.forward_from_chat:
        chat_id = message.forward_from_chat.id
        msg_id = message.forward_from_message_id

    elif getattr(message, 'forward_origin', None) and message.forward_origin.chat:
        chat_id = message.forward_origin.chat.id
        msg_id = message.forward_origin.message_id

    if chat_id and chat_id in client.all_db_ids:
        return chat_id, msg_id

    if message.text:
        pattern = r"https://t.me/(?:c/)?(.*?)/(\d+)"
        matches = re.search(pattern, message.text)
        if matches:
            channel_str = matches.group(1)
            msg_id = int(matches.group(2))
            if channel_str.isdigit():
                db_id = int(f"-100{channel_str}")
                if db_id in client.all_db_ids:
                    return db_id, msg_id
            else:
                db_id = client.db_usernames.get(channel_str.lower())
                if db_id:
                    return db_id, msg_id
    return 0, 0

def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0: break
        time_list.append(int(result))
        seconds = int(remainder)
    for X in range(len(time_list)):
        time_list[X] = str(time_list[X]) + time_suffix_list[X]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

async def is_bot_admin(client, channel_id):
    try:
        bot = await client.get_chat_member(channel_id, "me")
        if bot.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
            if bot.privileges:
                required = ["can_invite_users", "can_delete_messages"]
                missing = [r for r in required if not getattr(bot.privileges, r, False)]
                if missing:
                    return False, f"Bot is missing rights: {', '.join(missing)}"
            return True, None
        return False, "Bot is not an admin in the channel."
    except errors.ChatAdminRequired:
        return False, "Bot can't access admin info in this channel."
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

async def check_subscription(client, user_id):
    statuses = {}
    for ch_id, (ch_name, ch_link, req, timer) in client.fsub_dict.items():
        if req and await client.mongodb.is_user_in_channel(ch_id, user_id):
            statuses[ch_id] = ChatMemberStatus.MEMBER
            continue
        try:
            user = await client.get_chat_member(ch_id, user_id)
            statuses[ch_id] = user.status
        except UserNotParticipant:
            statuses[ch_id] = ChatMemberStatus.BANNED
        except (Forbidden, ChatAdminRequired):
            client.LOGGER(__name__, client.name).warning(f"Permission error for {ch_name}.")
            statuses[ch_id] = None
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error checking {ch_name}: {e}")
            statuses[ch_id] = None
    return statuses

def is_user_subscribed(statuses):
    return all(
        s in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
        for s in statuses.values() if s is not None
    ) and bool(statuses)

def force_sub(func):
    async def wrapper(client: Client, message: Message):
        if not client.fsub_dict:
            return await func(client, message)
        photo = client.messages.get('FSUB_PHOTO', '')
        msg = await message.reply_photo(caption="<b>𝖶𝖺𝗂𝗍 𝖠 𝖲𝖾𝖼𝗈𝗇𝖽....</b>", photo=photo, parse_mode=ParseMode.HTML) if photo else await message.reply("<b>𝖶𝖺𝗂𝗍 𝖠 𝖲𝖾𝖼𝗈団....</b>", parse_mode=ParseMode.HTML)
        statuses = await check_subscription(client, message.from_user.id)
        if is_user_subscribed(statuses):
            await msg.delete()
            return await func(client, message)

        buttons = []
        status_lines = []
        for ch_id, (ch_name, ch_link, req, timer) in client.fsub_dict.items():
            status = statuses.get(ch_id)
            if status in {ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
                status_text = "<b>𝖩𝗈𝗂𝗇𝖾𝖽</b> ✅"
            else:
                status_text = "<i>𝖱𝖾𝗊𝗎𝗂𝗋𝖾𝖽</i> ❗️"
                if timer > 0:
                    fsub_id = f"fsub_{ch_id}"
                    link_info = await client.mongodb.get_current_invite_link(fsub_id, req)

                    if link_info:
                        ch_link = link_info.get("invite_link")
                        expires_at = link_info.get("expires_at")
                        if expires_at and datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc):
                            ch_link = None
                    else:
                        ch_link = None

                    if not ch_link:
                        expire_date = datetime.now(timezone.utc) + timedelta(minutes=timer)
                        invite = await client.create_chat_invite_link(
                            chat_id=ch_id,
                            expire_date=expire_date,
                            creates_join_request=req
                        )
                        ch_link = invite.invite_link
                        await client.mongodb.save_invite_link(fsub_id, ch_link, req, expires_at=expire_date)

                buttons.append(InlineKeyboardButton(f"𝖩𝗈𝗂𝗇 {ch_name}", url=ch_link))
            status_lines.append(f"› {ch_name} - {status_text}")
        fsub_text = client.messages.get('FSUB', "<blockquote><b>𝖩𝗈𝗂𝗇 𝖱𝖾𝗊𝗎𝗂𝗋𝖾𝖽</b></blockquote>\n𝖸𝗈𝗎 𝗆𝗎𝗌𝗍 𝗃𝗈𝗂𝗇 𝗍𝗁𝖾 𝖿𝗈𝗅𝗅𝗈𝗐𝗂𝗇𝗀 𝖼𝗁𝖺𝗇𝗇𝖾𝗅(𝗌) 𝗍𝗈 𝖼𝗈𝗇𝗍𝗂𝗇𝗎𝖾:")
        channels_message = f"{fsub_text}\n\n" + "\n".join(status_lines)

        try_again_button = []
        if len(message.text.split()) > 1:
            try:
                try_again_link = f"https://t.me/{client.username}/?start={message.text.split()[1]}"
                try_again_button = [InlineKeyboardButton("✦ 𝖳𝗋𝗒 𝖠𝗀𝖺𝗂𝗇", url=try_again_link)]
            except:
                pass

        button_layout = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
        if try_again_button:
            button_layout.append(try_again_button)
        try:
            await msg.edit(text=channels_message, reply_markup=InlineKeyboardMarkup(button_layout) if button_layout else None, parse_mode=ParseMode.HTML)
        except Exception as e:
            client.LOGGER(__name__, client.name).warning(f"Error updating FSUB message: {e}")
    return wrapper

async def delete_files(messages, client, k, enter):
    if client.auto_del > 0:
        await asyncio.sleep(client.auto_del)
        for msg in messages:
            try:
                await msg.delete()
            except Exception as e:
                client.LOGGER(__name__, client.name).warning(f"Failed to auto-delete message {msg.id}: {e}")
    command_part = enter.split(" ")[1] if len(enter.split(" ")) > 1 else None
    button_url = None
    if command_part:
        try:
            button_url = f"https://t.me/{client.username}?start={command_part}"
        except:
            pass

    final_text = "<b>𝖯𝗋𝖾𝗏𝗂𝗈𝗎𝗌 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖶𝖺𝗌 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 🗑</b>"
    keyboard = None

    if button_url:
        final_text += f'\n<blockquote><b>𝖨𝖿 𝖸𝗈𝗎 𝖶𝖺𝗇𝗍 𝖳𝗈 𝖦𝖾𝗍 𝖳𝗁𝖾 𝖥𝗂𝗅𝖾𝗌 𝖠𝗀𝖺𝗂𝗇, 𝖳𝗁𝖾𝗇 𝖢𝗅𝗂𝖼𝗄:[<a href="{button_url}">⭕️ 𝖢𝗅𝗂𝖼𝗄 𝖧𝖾𝗋𝖾</a>] 𝖡𝗎𝗍𝗍𝗈𝗇 𝖡𝖾𝗅𝗈𝗐 𝖤𝗅𝗌𝖾 𝖢𝗅𝗈𝗌𝖾 𝖳𝗁𝗂𝗌 𝖬𝖾𝗌𝗌𝖺𝗀𝖾.</blockquote></b>'
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✦ 𝖢𝗅𝗂𝖼𝗄 𝖧𝖾𝗋𝖾", url=button_url), InlineKeyboardButton("✦ 𝖢𝗅𝗈𝗌𝖾 ✖️", callback_data="close")]]
        )

    try:
        if k.photo:
            await k.edit_caption(
                caption=final_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        else:
            await k.edit_text(
                final_text,
                reply_markup=keyboard,
                disable_web_page_preview=True,
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error editing auto-delete warning: {e}")

def weilai_style(text):
    if not text:
        return ""
    mapping = {
        'A': '𝖠', 'B': '𝖡', 'C': '𝖢', 'D': '𝖣', 'E': '𝖤', 'F': '𝖥', 'G': '𝖦', 'H': '𝖧', 'I': '𝖨', 'J': '𝖩', 'K': '𝖪', 'L': '𝖫', 'M': '𝖬', 'N': '𝖭', 'O': '𝖮', 'P': '𝖯', 'Q': '𝖰', 'R': '𝖱', 'S': '𝖲', 'T': '𝖳', 'U': '𝖴', 'V': '𝖵', 'W': '𝖶', 'X': '𝖷', 'Y': '𝖸', 'Z': '𝖹',
        'a': '𝖺', 'b': '𝖻', 'c': '𝖼', 'd': '𝖽', 'e': '𝖾', 'f': '𝖿', 'g': '𝖌', 'h': '𝗁', 'i': '𝗂', 'j': '𝗃', 'k': '𝗄', 'l': '𝗅', 'm': '𝗆', 'n': '𝗇', 'o': '𝗈', 'p': '𝗉', 'q': '𝗊', 'r': '𝗋', 's': '𝗌', 't': '𝗍', 'u': '𝗎', 'v': '𝗏', 'w': '𝗐', 'x': '𝗑', 'y': '𝗒', 'z': '𝗓',
        '0': '𝟢', '1': '𝟣', '2': '𝟤', '3': '𝟥', '4': '𝟦', '5': '𝟧', '6': '𝟨', '7': '𝟩', '8': '𝟪', '9': '𝟫'
    }
    def style_char(c):
        return mapping.get(c, c)
    def style_word(word):
        if not word:
            return ""
        if len(word) >= 2 and word.isupper():
            return "".join(style_char(c) for c in word)
        return "".join(style_char(c) for c in word.title())
    parts = re.split(r'(<[^>]+>)', str(text))
    styled_parts = []
    for part in parts:
        if part.startswith('<') and part.endswith('>'):
            styled_parts.append(part)
        else:
            words = re.split(r'(\s+)', part)
            styled_words = []
            for word in words:
                if not word.strip():
                    styled_words.append(word)
                else:
                    m = re.match(r'^([\w]+)([^\w]*)$', word)
                    if m:
                        base, suffix = m.groups()
                        styled_words.append(style_word(base) + "".join(style_char(c) for c in suffix))
                    else:
                        styled_words.append("".join(style_char(c) for c in word))
            styled_parts.append("".join(styled_words))
    return "".join(styled_parts)

def ftext(text):
    return weilai_style(text)

def flbl(text):
    if not text:
        return "✧ "
    clean_text = re.sub(r'^[^\w\s]+', '', str(text)).strip()
    return "✧ " + weilai_style(clean_text)
