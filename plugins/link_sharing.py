
import asyncio
import base64
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import FloodWait, UserNotParticipant, ChatAdminRequired, RPCError
from pyrogram.errors.pyromod import ListenerTimeout
from helper.helper_func import encode, decode, ftext, flbl, get_redirect_link
from datetime import datetime, timedelta, timezone

PAGE_SIZE = 6

@Client.on_callback_query(filters.regex("^add_ch$"))
async def add_channel_callback(client: Client, query: CallbackQuery):
    if not client.is_support:
        return
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    
    await query.answer()

    prompt = await client.send_message(
        query.from_user.id,
        ftext("<b>Please send the channel ID you want to add.</b>\n\n"
        "<b>Example:</b> <code>-1001234567890</code>\n\n"
        "Type `cancel` to abort."),
        parse_mode=ParseMode.HTML
    )
    
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=60)
    except (ListenerTimeout, asyncio.TimeoutError):
        await prompt.edit(ftext("<b>⏰ Timeout! No action taken.</b>"))
        from plugins.channel_settings import channel_settings_panel
        return await channel_settings_panel(client, query)

    if res.text.lower() == "cancel":
        await res.reply(ftext("<b>🚫 Action cancelled.</b>"), parse_mode=ParseMode.HTML)
        from plugins.channel_settings import channel_settings_panel
        return await channel_settings_panel(client, query)

    try:
        channel_id = int(res.text)
    except ValueError:
        await res.reply(ftext("<b>❌ Invalid channel ID. Please provide a valid integer.</b>"), parse_mode=ParseMode.HTML)
        from plugins.channel_settings import channel_settings_panel
        return await channel_settings_panel(client, query)
    
    try:
        chat = await client.get_chat(channel_id)
        bot_member = await client.get_chat_member(channel_id, "me")

        if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            return await res.reply(
                ftext(f"<b>❌ I am not an admin in {chat.title}.</b>\n\n"
                "Please make me an admin to continue."),
                parse_mode=ParseMode.HTML,
            )

        if bot_member.status == ChatMemberStatus.ADMINISTRATOR:
            if not bot_member.privileges or not bot_member.privileges.can_invite_users:
                return await res.reply(
                    ftext(f"<b>❌ I am an admin in {chat.title}, but I'm missing the 'Invite Users via Link' permission.</b>\n\nPlease grant this permission."),
                    parse_mode=ParseMode.HTML,
                )
        
        await client.mongodb.save_link_channel(channel_id)
        
        normal_link = await get_redirect_link(client, await encode(f"lnk_{channel_id}"))
        request_link = await get_redirect_link(client, await encode(f"req_{channel_id}"))
        
        reply_text = ftext(f"<b>✅ Channel Added Successfully!</b>\n\n"
            f"<b>Channel:</b> {chat.title}\n"
            f"<b>ID:</b> <code>{channel_id}</code>\n\n"
            f"<b>🔗 Normal Link:</b>\n") + f"<code>{normal_link}</code>\n\n"

        reply_text += ftext(f"<b>🔗 Request Link:</b>\n") + f"<code>{request_link}</code>"

        await res.reply(reply_text, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        await res.reply(
            ftext(f"<b>❌ Error:</b> <code>{str(e)}</code>"),
            parse_mode=ParseMode.HTML
        )

    from plugins.channel_settings import channel_settings_panel
    await channel_settings_panel(client, query)

@Client.on_callback_query(filters.regex("^del_ch$"))
async def delete_channel_callback(client: Client, query: CallbackQuery):
    if not client.is_support:
        return
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    
    await query.answer()

    prompt = await client.send_message(
        query.from_user.id,
        ftext("<b>Please send the channel ID you want to remove.</b>\n\n"
        "<b>Example:</b> <code>-1001234567890</code>\n\n"
        "Type `cancel` to abort."),
        parse_mode=ParseMode.HTML
    )
    
    try:
        res = await client.listen(chat_id=query.from_user.id, filters=filters.text, timeout=60)
        if res.text.lower() == "cancel":
            await res.reply(ftext("<b>🚫 Action cancelled.</b>"), parse_mode=ParseMode.HTML)
            from plugins.channel_settings import channel_settings_panel
            return await channel_settings_panel(client, query)

        try:
            channel_id = int(res.text)
            chat = await client.get_chat(channel_id)

            success = await client.mongodb.remove_link_channel(channel_id)

            if success:
                await res.reply(
                    ftext(f"<b>✅ Channel Removed Successfully!</b>\n\n"
                    f"<b>Channel:</b> {chat.title}\n"
                    f"<b>ID:</b> <code>{channel_id}</code>"),
                    parse_mode=ParseMode.HTML
                )
            else:
                await res.reply(
                    ftext("<b>❌ Channel not found in link sharing system!</b>"),
                    parse_mode=ParseMode.HTML
                )
        except ValueError:
            await res.reply(ftext("<b>❌ Invalid channel ID. Please provide a valid integer.</b>"), parse_mode=ParseMode.HTML)
        except Exception as e:
            await res.reply(
                ftext(f"<b>❌ Error:</b> <code>{str(e)}</code>"),
                parse_mode=ParseMode.HTML
            )
    except (ListenerTimeout, asyncio.TimeoutError):
        await prompt.edit(ftext("<b>⏰ Timeout! No action taken.</b>"))

    from plugins.channel_settings import channel_settings_panel
    await channel_settings_panel(client, query)

@Client.on_callback_query(filters.regex("^show_chs$"))
async def show_channels_callback(client: Client, query: CallbackQuery):
    if not client.is_support:
        return
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    
    await query.answer()
    channels = await client.mongodb.get_link_channels()
    
    if not channels:
        return await client.send_message(
            query.from_user.id,
            ftext("<b>📋 No link sharing channels configured.</b>"),
            parse_mode=ParseMode.HTML
        )
    
    await send_channels_page(client, query.message, channels, page=0, edit=True)

async def send_channels_page(client, message, channels, page, edit=False):
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    
    text = ftext("<b>📋 Link Sharing Channels:</b>\n\n")
    
    for idx, channel_id in enumerate(channels[start_idx:end_idx], start=start_idx + 1):
        try:
            chat = await client.get_chat(channel_id)
            button_link = await get_redirect_link(client, await encode(f"lnk_{channel_id}"))
            
            text += ftext(f"<b>{idx}. {chat.title}</b>\n")
            text += ftext(f"   <b>ID:</b> ") + f"<code>{channel_id}</code>\n"
            text += ftext(f"   <b>Link:</b> ") + f"<code>{button_link}</code>\n"
            text += "\n"
        except Exception as e:
            text += ftext(f"<b>{idx}. Channel {channel_id}</b>\n")
            text += ftext(f"   <b>Status:</b> Error fetching info\n\n")
    
    text += ftext(f"<b>📄 Page {page + 1} of {total_pages}</b>\n")
    text += ftext(f"<b>Total Channels:</b> {len(channels)}")
    
    buttons = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(flbl("Previous Page"), callback_data=f"chpage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(flbl("Next Page"), callback_data=f"chpage_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton(flbl("Back"), callback_data="channel_settings"), InlineKeyboardButton(flbl("Close"), callback_data="close")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    if edit:
        await message.edit_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"chpage_(\d+)"))
async def paginate_channels(client, callback_query):
    page = int(callback_query.data.split("_")[1])
    channels = await client.mongodb.get_link_channels()
    await send_channels_page(client, callback_query.message, channels, page, edit=True)

@Client.on_callback_query(filters.regex("^show_lnks$"))
async def show_all_links_callback(client: Client, query: CallbackQuery):
    if not client.is_support:
        return
    if query.from_user.id not in client.admins:
        return await query.answer("𝖠𝖽𝗆𝗂𝗇 𝗈𝗇𝗅𝗒!", show_alert=True)
    
    await query.answer()
    channels = await client.mongodb.get_link_channels()
    
    if not channels:
        return await client.send_message(
            query.from_user.id,
            ftext("<b>📋 No link sharing channels configured.</b>"),
            parse_mode=ParseMode.HTML
        )
    
    await send_links_page(client, query.message, channels, page=0, edit=True)

async def send_links_page(client, message, channels, page, edit=False):
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    
    text = ftext("<b>➤ All Channel Links:</b>\n\n")
    
    for idx, channel_id in enumerate(channels[start_idx:end_idx], start=start_idx + 1):
        try:
            chat = await client.get_chat(channel_id)
            
            normal_link = await get_redirect_link(client, await encode(f"lnk_{channel_id}"))
            request_link = await get_redirect_link(client, await encode(f"req_{channel_id}"))
            
            text += ftext(f"<b>{idx}. {chat.title}</b>\n")
            text += ftext("<b>➥ Normal:</b> ") + f"<code>{normal_link}</code>\n"
            text += ftext("<b>➤ Request:</b> ") + f"<code>{request_link}</code>\n"
            text += "\n"
        except Exception as e:
            text += ftext(f"<b>{idx}. Channel {channel_id}</b> (Error)\n\n")
    
    text += ftext(f"<b>📄 Page {page + 1} of {total_pages}</b>")
    
    buttons = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(flbl("Previous Page"), callback_data=f"lnkpage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(flbl("Next Page"), callback_data=f"lnkpage_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton(flbl("Back"), callback_data="channel_settings"), InlineKeyboardButton(flbl("Close"), callback_data="close")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    if edit:
        await message.edit_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

@Client.on_callback_query(filters.regex(r"lnkpage_(\d+)"))
async def paginate_links(client, callback_query):
    page = int(callback_query.data.split("_")[1])
    channels = await client.mongodb.get_link_channels()
    await send_links_page(client, callback_query.message, channels, page, edit=True)

@Client.on_message(filters.command('reqlink') & filters.private)
async def show_request_links(client: Client, message: Message):
    if not client.is_support:
        return
    if message.from_user.id not in client.admins:
        return await message.reply(ftext(client.reply_text))
    
    channels = await client.mongodb.get_link_channels()
    
    if not channels:
        return await message.reply(
            ftext("<b>📋 No link sharing channels configured.</b>\n\n"
            "Use <code>/addch {channel_id}</code> to add one."),
            parse_mode=ParseMode.HTML
        )
    
    await send_request_page(client, message, channels, page=0)

async def send_request_page(client, message, channels, page, edit=False):
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    buttons = []
    
    row = []
    for channel_id in channels[start_idx:end_idx]:
        try:
            button_link = await get_redirect_link(client, await encode(f"req_{channel_id}"))
            chat = await client.get_chat(channel_id)
            
            row.append(InlineKeyboardButton(flbl(chat.title), url=button_link))
            
            if len(row) == 2:
                buttons.append(row)
                row = []
        except Exception as e:
            client.LOGGER(__name__, client.name).error(f"Error for channel {channel_id}: {e}")
    
    if row:
        buttons.append(row)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(flbl("Previous Page"), callback_data=f"reqpage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(flbl("Next Page"), callback_data=f"reqpage_{page+1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    if not client.is_support:
        buttons.append([InlineKeyboardButton(flbl("Close"), callback_data="close")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    if edit:
        await message.edit_text(
            ftext("<b>Select a channel to request access:</b>"),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    else:
        await message.reply_text(
            ftext("<b>Select a channel to request access:</b>"),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )

@Client.on_callback_query(filters.regex(r"reqpage_(\d+)"))
async def paginate_requests(client, callback_query):
    page = int(callback_query.data.split("_")[1])
    channels = await client.mongodb.get_link_channels()
    await send_request_page(client, callback_query.message, channels, page, edit=True)

@Client.on_message(filters.command('bulklink') & filters.private)
async def bulk_link_generation(client: Client, message: Message):
    if not client.is_support:
        return
    if message.from_user.id not in client.admins:
        return await message.reply(ftext(client.reply_text))
    
    if len(message.command) < 2:
        return await message.reply(
            ftext("<b>Usage:</b> <code>/bulklink {id1} {id2} {id3} ...</code>\n\n"
            "<b>Example:</b> <code>/bulklink -1001234567890 -1009876543210</code>"),
            parse_mode=ParseMode.HTML
        )
    
    ids = message.command[1:]
    reply_text = ftext("<b>➤ Bulk Link Generation & Addition:</b>\n\n")
    
    for idx, id_str in enumerate(ids, start=1):
        try:
            channel_id = int(id_str)
            chat = await client.get_chat(channel_id)
            bot_member = await client.get_chat_member(channel_id, "me")

            if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                reply_text += ftext(f"<b>{idx}. {chat.title}</b>\n") + ftext("<b>Status:</b> ❌ Not Admin\n\n")
                continue

            if bot_member.status == ChatMemberStatus.ADMINISTRATOR:
                if not bot_member.privileges or not bot_member.privileges.can_invite_users:
                    reply_text += ftext(f"<b>{idx}. {chat.title}</b>\n") + ftext("<b>Status:</b> ❌ Missing 'Invite Users' perm\n\n")
                    continue

            await client.mongodb.save_link_channel(channel_id)
            
            normal_link = await get_redirect_link(client, await encode(f"lnk_{channel_id}"))
            request_link = await get_redirect_link(client, await encode(f"req_{channel_id}"))
            
            reply_text += ftext(f"<b>{idx}. {chat.title}</b>\n")
            reply_text += ftext("<b>ID:</b> ") + f"<code>{channel_id}</code>\n"
            reply_text += ftext("<b>➥ Normal:</b> ") + f"<code>{normal_link}</code>\n"
            reply_text += ftext("<b>➤ Request:</b> ") + f"<code>{request_link}</code>\n"
            reply_text += "\n"
        except Exception as e:
            reply_text += ftext(f"<b>{idx}. Channel {id_str}</b> (Error: {e})\n\n")
    
    await message.reply(reply_text, parse_mode=ParseMode.HTML)

async def handle_link_sharing(client: Client, user_id: int, decoded_param: str):
    try:
        is_request = decoded_param.startswith("req_")
        channel_id_str = decoded_param.replace("lnk_", "").replace("req_", "")
        
        try:
            channel_id = int(channel_id_str)
        except (ValueError, TypeError):
            client.LOGGER(__name__, client.name).error(f"Invalid channel ID in link: {channel_id_str}")
            return await client.send_message(user_id, ftext("<b>❌ Invalid channel link format.</b>"), parse_mode=ParseMode.HTML)
            
        if not await client.mongodb.is_link_channel(channel_id):
            return await client.send_message(user_id, ftext("<b>❌ This channel link is invalid or has been disabled.</b>"), parse_mode=ParseMode.HTML)
        
        link_info = await client.mongodb.get_current_invite_link(channel_id, is_request)
        expiry_mins = getattr(client, 'channel_link_expiry', 0)

        invite_link = None
        if link_info:
            invite_link = link_info.get("invite_link")
            expires_at = link_info.get("expires_at")

            if expires_at:
                if datetime.now(timezone.utc) > expires_at.replace(tzinfo=timezone.utc):
                    invite_link = None
            elif expiry_mins > 0:
                # Link is permanent but global setting requires expiry
                invite_link = None

        if not invite_link:
            expiry_mins = getattr(client, 'channel_link_expiry', 0)
            expire_date = datetime.now(timezone.utc) + timedelta(minutes=expiry_mins) if expiry_mins > 0 else None

            invite = await client.create_chat_invite_link(
                chat_id=channel_id,
                creates_join_request=is_request,
                expire_date=expire_date
            )
            invite_link = invite.invite_link
            await client.mongodb.save_invite_link(channel_id, invite_link, is_request, expires_at=expire_date)
        
        button_text = "Request To Join" if is_request else "Join Channel"
        button = InlineKeyboardMarkup([[InlineKeyboardButton(flbl(button_text), url=invite_link)]])
        
        wait_msg = await client.send_message(user_id, ftext("<b>Please wait...</b>"), parse_mode=ParseMode.HTML)
        await asyncio.sleep(0.5)
        await wait_msg.delete()
        
        await client.send_message(
            user_id,
            ftext("<b>Here is your link! Click below to proceed</b>"),
            reply_markup=button,
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Link sharing error: {e}")
        await client.send_message(user_id, ftext("<b>❌ An unexpected error occurred while generating your link.</b>"), parse_mode=ParseMode.HTML)
