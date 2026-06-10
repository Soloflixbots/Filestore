from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.raw.types import MessageActionPinMessage
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant, Forbidden, PeerIdInvalid, ChatAdminRequired
import asyncio

async def delete_message_after_delay(message, delay):
    """
    A helper coroutine that waits for a specified delay and then deletes the message.
    Runs in the background without blocking.
    """
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        print(f"Could not delete message {message.id} after delay: {e}")
        pass

@Client.on_message(filters.command('users'))
async def user_count(client, message):
    if not message.from_user.id in client.admins:
        return await client.send_message(message.from_user.id, client.reply_text)
    total_users = await client.mongodb.total_users_count()
    bot_users = await client.mongodb.bot_users_count(client.me.id)
    await message.reply(
        f"<b><blockquote>📊 𝖡𝗈𝗍 𝖴𝗌𝖾𝗋 𝖲𝗍𝖺𝗍𝗂𝗌𝗍𝗂𝖼𝗌</blockquote>\n\n"
        f"›› 𝖦𝗅𝗈𝖻𝖺𝗅 𝖴𝗌𝖾𝗋𝗌: <code>{total_users}</code>\n"
        f"›› 𝖳𝗁𝗂𝗌 𝖡𝗈𝗍 𝖴𝗌𝖾𝗋𝗌: <code>{bot_users}</code></b>",
        parse_mode=ParseMode.HTML
    )

@Client.on_message(filters.private & filters.command('broadcast'))
async def send_text(client, message):
    admin_ids = client.admins
    user_id = message.from_user.id
    if user_id in admin_ids:
        if message.reply_to_message:
            query = await client.mongodb.full_userbase()
            broadcast_msg = message.reply_to_message
            total = 0
            successful = 0
            blocked = 0
            deleted = 0
            unsuccessful = 0
            pls_wait = await message.reply("<blockquote><i>𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍𝗂𝗇𝗀 𝖬𝖾𝗌𝗌𝖺𝗀𝖾.. 𝖳𝗁𝗂𝗌 𝗐𝗂𝗅𝗅 𝖳𝖺𝗄𝖾 𝖲𝗈𝗆𝖾 𝖳𝗂𝗆𝖾</i></blockquote>", parse_mode=ParseMode.HTML)
            for chat_id in query:
                try:
                    await broadcast_msg.copy(chat_id)
                    successful += 1
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await broadcast_msg.copy(chat_id)
                    successful += 1
                except UserIsBlocked:
                    await client.mongodb.del_user(chat_id)
                    blocked += 1
                except InputUserDeactivated:
                    await client.mongodb.del_user(chat_id)
                    deleted += 1
                except Exception as e:
                    print(f"Failed to send message to {chat_id}: {e}")
                    unsuccessful += 1
                    pass
                total += 1
            status = f"""<blockquote><b><u>𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝖾𝖽</u></b></blockquote>
    <blockquote expandable><b>𝖳𝗈𝗍𝖺𝗅 𝖴𝗌𝖾𝗋𝗌 :</b> <code>{total}</code>
    <b>𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅 :</b> <code>{successful}</code>
    <b>𝖡𝗅𝗈𝖼𝗄𝖾𝖽 𝖴𝗌𝖾𝗋𝗌 :</b> <code>{blocked}</code>
    <b>𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖠𝖼𝖼𝗈𝗎𝗇𝗍𝗌 :</b> <code>{deleted}</code>
    <b>𝖴𝗇𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅 :</b> <code>{unsuccessful}</code></blockquote>"""
            return await pls_wait.edit(status, parse_mode=ParseMode.HTML)
        else:
            msg = await message.reply(f"𝖴𝗌𝖾 𝖳𝗁𝗂𝗌 𝖢𝗈𝗆𝗆𝖺𝗇𝖽 𝖠𝗌 𝖠 𝖱𝖾𝗉𝗅𝗒 𝖳𝗈 𝖠𝗇𝗒 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗆 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖶𝗂𝗍𝗁𝗈𝗎𝗍 𝖠𝗇𝗒 𝖲𝗉𝖺𝖼𝖾𝗌.")
            await asyncio.sleep(8)
            await msg.delete()

@Client.on_message(filters.private & filters.command('dbroadcast'))
async def deletable_broadcast(client, message):
    """Handles /dbroadcast command with an auto-delete timer."""
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)

    if not message.reply_to_message:
        return await message.reply("<b>𝖯𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗍𝗈 𝖻𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍 𝗂𝗍 𝗐𝗂𝗍𝗁 𝖺 𝗍𝗂𝗆𝖾𝗋.</b>", parse_mode=ParseMode.HTML)

    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            raise ValueError()
        timer_seconds = int(parts[1])
        if timer_seconds <= 0:
            raise ValueError()
    except (ValueError, IndexError):
        return await message.reply(
            "<b>Invalid format. Please provide a positive number of seconds for the timer.</b>\n\n"
            "<b>Usage:</b> <code>/dbroadcast 3600</code> (deletes after 1 hour)",
            parse_mode=ParseMode.HTML
        )

    query = await client.mongodb.full_userbase()
    broadcast_msg = message.reply_to_message
    total = 0
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0
    pls_wait = await message.reply(
        f"<blockquote><i>𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍𝗂𝗇𝗀 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗐𝗂𝗍 𝖺 {timer_seconds}-𝗌𝖾𝖼𝗈𝗇𝖽 𝖺𝗎𝗍𝗈-𝖽𝖾𝗅𝖾𝗍𝖾 𝗍𝗂𝗆𝖾𝗋...</i></blockquote>",
        parse_mode=ParseMode.HTML
    )
    for chat_id in query:
        try:
            sent_msg = await broadcast_msg.copy(chat_id)
            asyncio.create_task(delete_message_after_delay(sent_msg, timer_seconds))
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)
            sent_msg = await broadcast_msg.copy(chat_id)
            asyncio.create_task(delete_message_after_delay(sent_msg, timer_seconds))
            successful += 1
        except UserIsBlocked:
            await client.mongodb.del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await client.mongodb.del_user(chat_id)
            deleted += 1
        except Exception as e:
            print(f"Failed to send deletable broadcast to {chat_id}: {e}")
            unsuccessful += 1
        total += 1
    status = f"""<blockquote><b><u>𝖣𝖾𝗅𝖾𝗍𝖺𝖻𝗅𝖾 𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝖾𝖽</u></b></blockquote>
<blockquote expandable><b>𝖳𝗂𝗆𝖾𝗋 𝖲𝖾𝗍:</b> <code>{timer_seconds} 𝗌𝖾𝖼𝗈𝗇𝖽𝗌</code>
<b>𝖳𝗈𝗍𝖺𝗅 𝖴𝗌𝖾𝗋𝗌:</b> <code>{total}</code>
<b>𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅:</b> <code>{successful}</code>
<b>𝖡𝗅𝗈𝖼𝗄𝖾𝖽 𝖴𝗌𝖾𝗋𝗌:</b> <code>{blocked}</code>
<b>𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖠𝖼𝖼𝗈𝗎𝗇𝗍𝗌:</b> <code>{deleted}</code>
<b>𝖴𝗇𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅:</b> <code>{unsuccessful}</code></blockquote>"""
    await pls_wait.edit(status, parse_mode=ParseMode.HTML)

@Client.on_message(filters.private & filters.command('pbroadcast'))
async def pin_bdcst_text(client, message):
    admin_ids = client.admins
    user_id = message.from_user.id
    if user_id in admin_ids:
        if message.reply_to_message:
            query = await client.mongodb.full_userbase()
            broadcast_msg = message.reply_to_message
            total = 0
            successful = 0
            blocked = 0
            deleted = 0
            unsuccessful = 0
            pls_wait = await message.reply("<blockquote><i>𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍𝗂𝗇𝗀 𝖬𝖾𝗌𝗌𝖺𝗀𝖾.. 𝖳𝗁𝗂𝗌 𝗐𝗂𝗅𝗅 𝖳𝖺𝗄𝖾 𝖲𝗈𝗆𝖾 𝖳𝗂𝗆𝖾</i></blockquote>", parse_mode=ParseMode.HTML)
            for chat_id in query:
                try:
                    sent_msg = await broadcast_msg.copy(chat_id)
                    successful += 1
                    await client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id, both_sides=True)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    sent_msg = await broadcast_msg.copy(chat_id)
                    successful += 1
                    await client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id)
                except UserIsBlocked:
                    await client.mongodb.del_user(chat_id)
                    blocked += 1
                except InputUserDeactivated:
                    await client.mongodb.del_user(chat_id)
                    deleted += 1
                except Exception as e:
                    print(f"Failed to send message to {chat_id}: {e}")
                    unsuccessful += 1
                total += 1
            status = f"""<blockquote><b><u>𝖡𝗋𝗈𝖺𝖽𝖼𝖺𝗌𝗍 𝖢𝗈𝗆𝗉𝗅𝖾𝗍𝖾𝖽</u></b></blockquote>
    <b>𝖳𝗈𝗍𝖺𝗅 𝖴𝗌𝖾𝗋𝗌 :</b> <code>{total}</code>
    <b>𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅 :</b> <code>{successful}</code>
    <b>𝖡𝗅𝗈𝖼𝗄𝖾𝖽 𝖴𝗌𝖾𝗋𝗌 :</b> <code>{blocked}</code>
    <b>𝖣𝖾𝗅𝖾𝗍𝖾𝖽 𝖠𝖼𝖼𝗈𝗎𝗇𝗍𝗌 :</b> <code>{deleted}</code>
    <b>𝖴𝗇𝗌𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅 :</b> <code>{unsuccessful}</code>"""
            return await pls_wait.edit(status, parse_mode=ParseMode.HTML)
        else:
            msg = await message.reply("𝖴𝗌𝖾 𝖳𝗁𝗂𝗌 𝖢𝗈𝗆𝗆𝖺𝗇𝖽 𝖠𝗌 𝖠 𝖱𝖾𝗉𝗅𝗒 𝖳𝗈 𝖠𝗇𝗒 𝖳𝖾𝗅𝖾𝗀𝗋𝖺𝗆 𝖬𝖾𝗌𝗌𝖺𝗀𝖾 𝖶𝗂𝗍𝗁𝗈𝗎𝗍 𝖠𝗇𝗒 𝖲𝗉𝖺𝖼𝖾𝗌.")
            await asyncio.sleep(8)
            await msg.delete()