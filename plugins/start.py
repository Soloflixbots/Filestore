
from helper.helper_func import *
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
import humanize
import asyncio
from datetime import datetime, timedelta
from plugins.others import send_start_message
import random

async def get_messages_with_fallback(client: Client, channel_id: int, msg_ids: list):
    final_messages = {}
    ids_to_fetch = list(msg_ids)
    client.LOGGER(__name__, client.name).info(f"📥 Fetching {len(ids_to_fetch)} messages from channel {channel_id}")
    try:
        all_raw_msgs = []
        for i in range(0, len(ids_to_fetch), 200):
            batch_ids = ids_to_fetch[i:i+200]
            try:
                msgs = await client.get_messages(chat_id=channel_id, message_ids=batch_ids)
                if isinstance(msgs, list): all_raw_msgs.extend(msgs)
                else: all_raw_msgs.append(msgs)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                msgs = await client.get_messages(chat_id=channel_id, message_ids=batch_ids)
                if isinstance(msgs, list): all_raw_msgs.extend(msgs)
                else: all_raw_msgs.append(msgs)
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"❌ Major error fetching from original channel {channel_id}: {e}")
    successful_ids = {msg.id for msg in all_raw_msgs if msg and not msg.empty}
    for msg in all_raw_msgs:
        if msg and not msg.empty:
            final_messages[msg.id] = msg

    failed_ids = set(ids_to_fetch) - successful_ids
    if failed_ids:
        client.LOGGER(__name__, client.name).info(f"🔄 {len(failed_ids)} messages not found. Checking backup...")
        backup_db_id = client.databases.get('backup')
        if backup_db_id:
            backup_map = {await client.mongodb.get_backup_msg_id(channel_id, og_id): og_id for og_id in failed_ids}
            backup_map = {k: v for k, v in backup_map.items() if k is not None}

            if backup_map:
                backup_msg_ids = list(backup_map.keys())
                for i in range(0, len(backup_msg_ids), 200):
                    batch_backup_ids = backup_msg_ids[i:i+200]
                    try:
                        backup_msgs = await client.get_messages(backup_db_id, batch_backup_ids)
                        if not isinstance(backup_msgs, list): backup_msgs = [backup_msgs]
                        for b_msg in backup_msgs:
                            if b_msg and not b_msg.empty:
                                original_id = backup_map.get(b_msg.id)
                                if original_id:
                                    final_messages[original_id] = b_msg
                    except Exception as e:
                        client.LOGGER(__name__, client.name).error(f"❌ Error fetching from backup: {e}")
    return [final_messages.get(og_id) for og_id in msg_ids if final_messages.get(og_id)]

async def backup_files(client: Client, original_channel_id: int, message_ids: list):
    backup_db_id = client.databases.get('backup')
    if not backup_db_id or not message_ids:
        return

    for msg_id in message_ids:
        try:
            if await client.mongodb.is_backed_up(original_channel_id, msg_id):
                continue
            original_msg = await client.get_messages(original_channel_id, msg_id)
            if not original_msg or original_msg.empty:
                continue
            backup_msg = await original_msg.copy(backup_db_id)
            await client.mongodb.add_backup_mapping(original_channel_id, msg_id, backup_msg.id)
            await asyncio.sleep(1)
        except Exception as e:
            client.LOGGER(__name__, client.name).error(f"BACKGROUND BACKUP: Failed for message {msg_id}: {e}")

async def resolve_payload(client: Client, payload: str):
    current_payload = payload
    visited_payloads = set()
    for _ in range(10):
        if not current_payload or current_payload in visited_payloads: break
        visited_payloads.add(current_payload)

        if current_payload.startswith("dl_"):
            current_payload = current_payload[3:]
            continue

        if current_payload.startswith("exp_"):
            temp_id = current_payload[4:]
            temp_data = await client.mongodb.get_temp_link(temp_id)
            if temp_data:
                current_payload = temp_data.get("payload")
                continue
            else:
                return None

        verification_data = await client.mongodb.get_verification(current_payload)
        if verification_data:
            current_payload = verification_data.get("payload")
            continue

        short_data = await client.mongodb.get_short_link(current_payload)
        if short_data:
            current_payload = short_data.get("payload")
            continue

        alias_payload = await client.mongodb.get_alias(current_payload)
        if alias_payload:
            current_payload = alias_payload
            continue

        try:
            decoded = await client.mongodb.decode_link_param(current_payload)
            if decoded:
                current_payload = decoded
                continue
        except Exception:
            pass

        break

    return current_payload

@Client.on_message(filters.command('start') & filters.private)
@force_sub
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await client.mongodb.present_user(user_id, client.me.id):
        await client.mongodb.add_user(user_id, client.me.id)
    if await client.mongodb.is_banned(user_id):
        return await message.reply("**𝖸𝗈𝗎 𝖧𝖺𝗏𝖾 𝖡𝖾𝖾𝗇 𝖡𝖺𝗇𝗇𝖾𝖽!**")

    text = message.text
    if len(text) <= 7:
        return await send_start_message(client, message)

    try:
        param = text.split(" ", 1)[1]
    except IndexError:
        return await send_start_message(client, message)

    decoded_string = await resolve_payload(client, param)

    if not decoded_string:
        return await message.reply("❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗈𝗋 𝖾𝗑𝗉𝗂𝗋𝖾𝖽 𝗅𝗂𝗇𝗄.")

    is_admin = user_id in client.admins
    clean_payload = await encode(decoded_string)

    if getattr(client, 'robot_check', False) and not is_admin:
        temp_id = await client.mongodb.save_verification(clean_payload, client.username)
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 𝖨 𝖠𝗆 𝖭𝗈𝗍 𝖠 𝖱𝗈𝖻𝗈𝗍", callback_data=f"robot_check_{temp_id}")]
        ])
        return await message.reply(
            "<b>𝖯𝗅𝖾𝖺𝗌𝖾 𝗏𝖾𝗋𝗂𝖿𝗒 𝗍𝗁𝖺𝗍 𝗒𝗈𝗎 𝖺𝗋𝖾 𝗁𝗎𝗆𝖺𝗇 𝖻𝗒 𝖼𝗅𝗂𝖼𝗄𝗂𝗇𝗀 𝗍𝗁𝖾 𝖻𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗐.</b>",
            reply_markup=buttons,
            parse_mode=ParseMode.HTML
        )

    await process_start_payload(client, user_id, decoded_string, text)

async def process_start_payload(client: Client, user_id: int, decoded_string: str, original_text: str):
    try:
        parts = decoded_string.split("_")
        command = parts[0]
        if command in ["lnk", "req"] and len(parts) > 1:
            from plugins.link_sharing import handle_link_sharing
            return await handle_link_sharing(client, user_id, decoded_string)

        if command == "single" and len(parts) > 2:
            channel_id, msg_ids = int(parts[1]), [int(parts[2])]
        elif command == "batch" and len(parts) > 1:
            if len(parts) >= 4:
                channel_id, start_id, end_id = int(parts[1]), int(parts[2]), int(parts[3])
                msg_ids = list(range(start_id, end_id + 1))
            else:
                channel_id, msg_ids = await client.mongodb.get_batch(parts[1])
                if not (channel_id and msg_ids):
                    return await client.send_message(user_id, "❌ This link has expired.")
        else:
            raise ValueError("Unsupported link format")
    except (IndexError, ValueError):
        return await client.send_message(user_id, "❌ Invalid or malformed file link.")

    temp_msg = await client.send_message(user_id, "<b>𝖯𝗅𝖾𝖺𝗌𝖾 𝖶𝖺𝗂𝗍...</b>", parse_mode=ParseMode.HTML)
    messages_to_send = await get_messages_with_fallback(client, channel_id, msg_ids)
    if not messages_to_send:
        return await temp_msg.edit("❌ <b>𝖢𝗈𝗇𝗍𝖾𝗇𝗍 𝖭𝗈𝗍 𝖥𝗈𝗎𝗇𝖽.</b> 𝖨𝗍 𝗆𝖺𝗒 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝖽𝖾𝗅𝖾𝗍𝖾𝖽.")
    if client.databases.get('backup'):
        asyncio.create_task(backup_files(client, channel_id, msg_ids))
    await temp_msg.delete()

    sent_messages, failed_count = [], 0
    for msg in messages_to_send:
        is_web_page = hasattr(msg, 'web_page') and msg.web_page is not None

        if msg.media and not is_web_page:
            final_caption = "" if client.hide_caption else (msg.caption.html if msg.caption else "")
            buttons = []
            if client.channel_button_enabled and client.button_name and client.button_url:
                buttons.append([InlineKeyboardButton(f"✦ {client.button_name}", url=client.button_url)])

            final_markup = InlineKeyboardMarkup(buttons) if buttons else None
            try:
                sent_msg = await msg.copy(
                    chat_id=user_id,
                    caption=final_caption,
                    reply_markup=final_markup,
                    protect_content=client.protect
                )
                sent_messages.append(sent_msg)

            except FloodWait as e:
                await asyncio.sleep(e.x + 1)
                try:
                    sent_msg = await msg.copy(user_id, caption=final_caption, reply_markup=final_markup, protect_content=client.protect)
                    sent_messages.append(sent_msg)
                except Exception: failed_count += 1
            except Exception:
                failed_count += 1
        elif msg.text:
            try:
                sent_text = await client.send_message(
                    chat_id=user_id,
                    text=msg.text.html,
                    reply_markup=msg.reply_markup,
                    disable_web_page_preview=True,
                    protect_content=client.protect
                )
                sent_messages.append(sent_text)
            except Exception:
                failed_count += 1
    if not sent_messages and not failed_count:
        await client.send_message(user_id, "No valid content found in the requested link(s).")
        return

    if failed_count > 0:
        await client.send_message(user_id, f"⚠️ <b>Note:</b> {failed_count} item(s) could not be sent.")
    if sent_messages and client.auto_del > 0:
        del_text = client.messages.get('AUTO_DEL_TEXT', "<b>⚠️ 𝖸𝗈𝗎𝗋 𝖥𝗂𝗅𝖾𝗌 𝖶𝗂𝗅𝗅 𝖡𝖾 𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖶𝗂𝗍𝗁𝗂𝗇 {time}.</b>").replace("{time}", humanize.naturaldelta(timedelta(seconds=client.auto_del)))
        del_photo = client.messages.get('AUTO_DEL_PHOTO')
        if del_photo:
            k = await client.send_photo(chat_id=user_id, photo=del_photo, caption=del_text)
        else:
            k = await client.send_message(chat_id=user_id, text=del_text)
        asyncio.create_task(delete_files(sent_messages, client, k, original_text))

@Client.on_callback_query(filters.regex("^robot_check_"))
async def robot_check_cb(client: Client, query: CallbackQuery):
    temp_id = query.data.replace("robot_check_", "")
    user_id = query.from_user.id
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    ans = a + b
    verification_data = await client.mongodb.get_verification(temp_id)
    if not verification_data:
        return await query.answer("❌ 𝖫𝗂𝗇𝗄 𝖾𝗑𝗉𝗂𝗋𝖾𝖽.", show_alert=True)
    await client.mongodb.verifications.update_one({"_id": temp_id}, {"$set": {"captcha": ans}})
    options = [ans, ans + random.randint(1, 5), ans - random.randint(1, 5), random.randint(1, 20)]
    options = list(set(options))
    random.shuffle(options)
    buttons = []
    for opt in options:
        buttons.append(InlineKeyboardButton(str(opt), callback_data=f"vr_{temp_id}_{user_id}_{opt}"))
    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    await query.message.edit_text(
        f"<b>𝖲𝗈𝗅𝗏𝖾 𝗍𝗁𝗂𝗌 𝗍𝗈 𝗉𝗋𝗈𝗏𝖾 𝗒𝗈𝗎 𝖺𝗋𝖾 𝗁𝗎𝗆𝖺𝗇:</b>\n\n<blockquote><code>{a} + {b} = ?</code></blockquote>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.HTML
    )

@Client.on_callback_query(filters.regex("^vr_"))
async def verify_robot_cb(client: Client, query: CallbackQuery):
    data = query.data.split("_")
    temp_id = data[1]
    target_user_id = int(data[2])
    selected_opt = int(data[3])

    if query.from_user.id != target_user_id:
        return await query.answer("𝖳𝗁𝗂𝗌 𝗂𝗌 𝗇𝗈𝗍 𝖿𝗈𝗋 𝗒𝗈𝗎!", show_alert=True)

    verification_data = await client.mongodb.get_verification(temp_id)
    if not verification_data:
        return await query.answer("❌ 𝖫𝗂𝗇𝗄 𝖾𝗑𝗉𝗂𝗋𝖾𝖽.", show_alert=True)

    correct_ans = verification_data.get("captcha")
    if selected_opt != correct_ans:
        return await query.answer("❌ 𝖶𝗋𝗈𝗇𝗀 𝖺𝗇𝗌𝗐𝖾𝗋. 𝖳𝗋𝗒 𝖺𝗀𝖺𝗂𝗇!", show_alert=True)

    await query.answer("✅ 𝖵𝖾𝗋𝗂𝖿𝗂𝖾𝖽!", show_alert=True)
    await query.message.delete()
    payload = verification_data.get("payload")
    decoded_string = await resolve_payload(client, payload)
    if not decoded_string:
        return await client.send_message(query.from_user.id, "❌ 𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝗅𝗂𝗇𝗄.")
    await process_start_payload(client, query.from_user.id, decoded_string, f"/start {payload}")
