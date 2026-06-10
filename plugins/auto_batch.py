import re
import traceback
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
from pyrogram.errors.pyromod import ListenerTimeout
from helper.helper_func import encode, get_message_id, get_messages, get_redirect_link, weilai_style

QUALITY_PATTERNS = {
    "4k": re.compile(r'2160p|4k', re.IGNORECASE),
    "1080p": re.compile(r'1080p', re.IGNORECASE),
    "720p": re.compile(r'720p', re.IGNORECASE),
    "540p": re.compile(r'540p', re.IGNORECASE),
    "480p": re.compile(r'480p', re.IGNORECASE),
    "hdrip": re.compile(r'HDRip|HD-Rip|HD\sRip', re.IGNORECASE),
    "bluray": re.compile(r'BluRay', re.IGNORECASE),
    "webdl": re.compile(r'WEB-DL|WEBRip', re.IGNORECASE),
    "hevc": re.compile(r'HEVC|X265', re.IGNORECASE),
}

QUALITY_DISPLAY_NAMES = {
    "4k": "2160p | 4K", "1080p": "1080p", "720p": "720p", "540p": "540p", "480p": "480p",
    "hdrip": "HDRip", "bluray": "BluRay", "webdl": "WEB-DL", "hevc": "HEVC X265", "other": "Other"
}

def get_file_quality(filename: str):
    if not isinstance(filename, str): return "other"
    for quality, pattern in QUALITY_PATTERNS.items():
        if pattern.search(filename): return quality
    return "other"
async def ask_for_message(client, user_id, prompt_text):
    prompt_message = await client.send_message(user_id, prompt_text, parse_mode=ParseMode.HTML)
    try:
        response = await client.listen(chat_id=user_id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=120)
        await prompt_message.delete()
        return response
    except ListenerTimeout:
        await prompt_message.edit("<b>⏰ 𝖳𝗂𝗆𝖾𝗈𝗎!</b> 𝖯𝗅𝖾𝖺𝗌𝖾 𝗍𝗋𝗒 𝗍𝗁𝖾 𝖼𝗈𝗆𝗆𝖺𝗇𝖽 𝖺𝗀𝖺𝗂𝗇.")
        return None

@Client.on_message(filters.private & filters.command('autobatch'))
async def auto_batch_range_command(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    logger = client.LOGGER(__name__, "autobatch")

    args = message.text.split(None, 1)
    custom_data = None
    if len(args) > 1:
        parts = args[1].split("|")
        if len(parts) == 2:
            title = parts[0].strip()
            audio = parts[1].strip()
            custom_data = {"title": title, "audio": audio}

    while True:
        first_message = await ask_for_message(client, message.from_user.id, "<b>📨 𝖥𝗈𝗋𝗐𝖺𝗋𝖽 𝗍𝗁𝖾 <u>𝖥𝗂𝗋𝗌𝗍 𝖬𝖾𝗌𝗌𝖺𝗀𝖾</u> 𝖿𝗋𝗈𝗆 𝖣𝖻 𝖢𝗁𝖺𝗇𝗇𝖾𝗅</b>")
        if not first_message: return
        f_channel_id, f_msg_id = await get_message_id(client, first_message)
        if f_msg_id: break
        else: await first_message.reply("❌ <b>𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖬𝖾𝗌𝗌𝖺𝗀𝖾</b>: 𝖭𝗈𝗍 𝖿𝗋𝗈𝗆 𝖺 𝖼𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾𝖽 𝖣𝖻 𝖼𝗁𝖺𝗇𝗇𝖾𝗅.", quote=True)
    while True:
        second_message = await ask_for_message(client, message.from_user.id, "<b>📨 𝖥𝗈𝗋𝗐𝖺𝗋𝖽 𝗍𝗁𝖾 <u>𝖫𝖺𝗌𝗍 𝖬𝖾𝗌𝗌𝖺𝗀𝖾</u> 𝖿𝗋𝗈𝗆 𝖣𝖻 𝖢𝗁𝖺𝗇𝗇𝖾𝗅</b>")
        if not second_message: return
        s_channel_id, s_msg_id = await get_message_id(client, second_message)
        if s_msg_id: break
        else: await second_message.reply("❌ <b>𝖨𝗇𝗏𝖺𝗅𝗂𝖽 𝖬𝖾𝗌𝗌𝖺𝗀𝖾</b>: 𝖭𝗈𝗍 𝖿𝗋𝗈𝗆 𝖺 𝖼𝗈𝗇𝖿𝗂𝗀𝗎𝗋𝖾𝖽 𝖣𝖻 𝖼𝗁𝖺𝗇𝗇𝖾𝗅.", quote=True)
    if f_channel_id != s_channel_id:
        return await second_message.reply("❌ 𝖡𝗈𝗍𝗁 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝗆𝗎𝗌𝗍 𝖻𝖾 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝗌𝖺𝗆𝖾 𝖣𝖻 𝖼𝗁𝖺𝗇𝗇𝖾𝗅.")
    if f_msg_id >= s_msg_id:
        return await second_message.reply("❌ 𝖳𝗁𝖾 𝖿𝗂𝗋𝗌𝗍 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝖨𝖽 𝗆𝗎𝗌𝗍 𝖻𝖾 𝗌𝗆𝖺𝗅𝗅𝖾𝗋 𝗍𝗁𝖺𝗇 𝗍𝗁𝖾 𝗅𝖺𝗌𝗍 𝗈𝗇𝖾.")
    msg_ids_range = list(range(f_msg_id, s_msg_id + 1))
    prompt = await second_message.reply_text(f"⏳ <b>𝖥𝖾𝗍𝖼𝗁𝗂𝗇𝗀 {len(msg_ids_range)} 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌...</b>")
    try:
        messages_to_process = await get_messages(client, f_channel_id, msg_ids_range)
        if not messages_to_process:
            return await prompt.edit_text("❌ 𝖢𝗈𝗎𝗅𝖽 𝗇𝗈𝗍 𝖿𝖾𝗍𝖼𝗁 𝖺𝗇𝗒 𝗆𝖾𝗌𝗌𝖺𝗀𝖾𝗌 𝖿𝗈𝗋 𝗍𝗁𝖾 𝗀𝗂𝗏𝖾𝗇 𝗋𝖺𝗇𝗀𝖾.")

        await prompt.edit_text(f"⚙️ <b>𝖯𝗋𝗈𝖼𝖾𝗌𝗌𝗂𝗇𝗀 {len(messages_to_process)} 𝖿𝗂𝗅𝖾𝗌...</b>")
        grouped_files = {}
        total_files = 0
        detected_seasons = set()
        detected_episodes = set()
        season_episode_pairs = set()

        for msg in messages_to_process:
            file = msg.document or msg.video or msg.audio or msg.animation or msg.voice or msg.video_note or msg.sticker or msg.photo
            if not file: continue
            total_files += 1
            filename = str(getattr(file, "file_name", None) or msg.caption or "Unknown")

            s_match = re.search(r'[Ss](?:eason)?[\s.]?(\d+)', filename)
            e_match = re.search(r'[Ee](?:p(?:isode)?)?[\s.]?(\d+)', filename)

            s_no = int(s_match.group(1)) if s_match else None
            e_no = int(e_match.group(1)) if e_match else None

            if s_no is not None:
                detected_seasons.add(s_no)
            if e_no is not None:
                detected_episodes.add(e_no)
            if s_no is not None and e_no is not None:
                season_episode_pairs.add((s_no, e_no))

            quality = get_file_quality(filename)
            if quality not in grouped_files:
                grouped_files[quality] = []
            grouped_files[quality].append(msg.id)

        if not grouped_files:
            return await prompt.edit_text("❌ 𝖭𝗈 𝗏𝖺𝗅𝗂𝖽 𝖿𝗂𝗅𝖾𝗌 𝖼𝗈𝗎𝗅𝖽 𝖻𝖾 𝗀𝗋𝗈𝗎𝗉𝖾𝖽.")

        if detected_seasons:
            sorted_seasons = sorted(list(detected_seasons))
            if len(sorted_seasons) == 1:
                season_str = f"{sorted_seasons[0]:02d}"
            elif len(sorted_seasons) > 1:
                is_continuous = all(sorted_seasons[i] + 1 == sorted_seasons[i+1] for i in range(len(sorted_seasons)-1))
                if is_continuous:
                    season_str = f"{sorted_seasons[0]:02d}-{sorted_seasons[-1]:02d}"
                else:
                    season_str = ", ".join(f"{s:02d}" for s in sorted_seasons)
        else:
            season_str = "01"

        if season_episode_pairs:
            ep_count = len(season_episode_pairs)
        elif detected_episodes:
            ep_count = len(detected_episodes)
        else:
            ep_count = total_files

        all_grouped_ids = []
        for ids in grouped_files.values():
            all_grouped_ids.extend(ids)

        batch_key = await client.mongodb.save_batch(f_channel_id, all_grouped_ids)
        base64_sharing_payload = await encode(f"batch_{batch_key}")
        sharing_link = await get_redirect_link(client, base64_sharing_payload, use_redirector=True)

        generated_links = {}
        for quality, msg_ids in grouped_files.items():
            if not msg_ids: continue
            batch_key = await client.mongodb.save_batch(f_channel_id, msg_ids)
            base64_string = await encode(f"batch_{batch_key}")
            generated_links[quality] = {
                "direct": await get_redirect_link(client, base64_string, use_redirector=False),
                "count": len(msg_ids)
            }

        final_text = ""
        reply_markup = None

        if custom_data:
            display_map = {"480p": "𝟦𝟪𝟢𝗉", "540p": "𝟧𝟦𝟢𝗉", "720p": "𝟩𝟤𝟢𝗉", "1080p": "𝟣𝟢𝟪𝟢𝗉", "4k": "𝟦𝖪", "hdrip": "𝖧𝖽𝗋𝗂𝗉", "bluray": "𝖡𝗅𝗎𝖱𝖺𝗒", "webdl": "𝖶𝖤𝖡-𝖣𝖫", "hevc": "𝖧𝖤𝖵𝖢"}
            quality_order = ["480p", "540p", "720p", "1080p", "4k", "hdrip", "bluray", "webdl", "hevc"]

            title = weilai_style(custom_data['title'])
            audio = weilai_style(custom_data['audio'])

            season = weilai_style(season_str)
            total_ep = weilai_style(f"{ep_count:02d}")

            season_label = "𝖲𝖾𝖺𝗌𝗈𝗇𝗌" if len(detected_seasons) > 1 else "𝖲𝖾𝖺𝗌𝗈𝗇"

            final_text = f"<b>{title}</b>\n\n"
            final_text += f"✪ 𝖠𝗎𝖽𝗂𝗈 : {audio}\n\n"
            final_text += f"➤ {season_label} {season} [{total_ep} 𝖤𝖯]\n\n"

            for q in quality_order:
                if q in generated_links:
                    label = display_map.get(q, q)
                    final_text += f"➠ {label} - <a href='{generated_links[q]['direct']}'>{weilai_style('Link')}</a>\n\n"

            final_text += f"➤ {weilai_style('Powered by')} @Team_Weilai"

            buttons = []
            for q in quality_order:
                if q in generated_links:
                    button_text = f"✦ {QUALITY_DISPLAY_NAMES.get(q).split(' | ')[-1]}"
                    buttons.append(InlineKeyboardButton(text=button_text, url=generated_links[q]['direct']))
            reply_markup = InlineKeyboardMarkup([buttons[i:i + 2] for i in range(0, len(buttons), 2)]) if buttons else None

        else:
            from plugins.autobatch_settings import DEFAULT_AUTOBATCH_TEMPLATE
            use_custom_template = client.autobatch_template != DEFAULT_AUTOBATCH_TEMPLATE and client.autobatch_template != ""

            if use_custom_template:
                placeholders = {
                    "{totalfilecount}": str(len(messages_to_process)),
                    "{season}": season_str,
                    "{totalepisodes}": f"{ep_count:02d}",
                    "{sharinglink}": sharing_link
                }
                for key in QUALITY_DISPLAY_NAMES.keys():
                    link_data = generated_links.get(key)
                    if link_data:
                        placeholders[f"{{{key}}}"] = QUALITY_DISPLAY_NAMES.get(key)
                        placeholders[f"{{{key}link}}"] = link_data["direct"]
                        placeholders[f"{{{key}directlink}}"] = link_data["direct"]
                        placeholders[f"{{{key}filecount}}"] = str(link_data["count"])
                    else:
                        placeholders.update({f"{{{key}}}": "", f"{{{key}link}}": "", f"{{{key}directlink}}": "", f"{{{key}filecount}}": ""})
                final_text = client.autobatch_template
                for key, value in placeholders.items():
                    final_text = final_text.replace(key, value)
                final_text = "\n".join(line for line in final_text.split('\n') if line.strip() and '{' not in line)
            else:
                display_map = {"480p": "𝟦𝟪𝟢𝗉", "540p": "𝟧𝟦𝟢𝗉", "720p": "𝟩𝟤𝟢𝗉", "1080p": "𝟣𝟢𝟪𝟢𝗉", "4k": "𝟦𝖪", "hdrip": "𝖧𝖽𝗋𝗂𝗉", "bluray": "𝖡𝗅𝗎𝖱𝖺𝗒", "webdl": "𝖶𝖤𝖡-𝖣𝖫", "hevc": "𝖧𝖤𝖵𝖢", "other": "𝖮𝗍𝗁𝖾𝗋"}
                quality_order = ["480p", "540p", "720p", "1080p", "4k", "hdrip", "bluray", "webdl", "hevc", "other"]
                sorted_qualities = [q for q in quality_order if q in generated_links]
                response_text = "<b>⬇️ 𝖡𝖾𝗅𝗈𝗐 𝖨𝗌 𝖳𝗁𝖾 𝖡𝖺𝗍𝖼𝗁 𝖫𝗂𝗇𝗄:</b>\n\n<b>𝖣𝗂𝗋𝖾𝖼𝗍 𝖫𝗂𝗇𝗄𝗌:</b>\n<blockquote>"
                for qk in sorted_qualities:
                    label = display_map.get(qk, QUALITY_DISPLAY_NAMES.get(qk))
                    response_text += f"<b>{label}:</b> <a href='{generated_links[qk]['direct']}'>{weilai_style('Link')}</a>\n"
                response_text += "</blockquote>"
                final_text = response_text
            buttons = []
            button_order = ["480p", "540p", "720p", "1080p", "4k", "hdrip", "bluray", "webdl", "hevc", "other"]
            for quality_key in button_order:
                if quality_key in generated_links:
                    button_text = f"✦ {QUALITY_DISPLAY_NAMES.get(quality_key).split(' | ')[-1]}"
                    buttons.append(InlineKeyboardButton(text=button_text, url=generated_links[quality_key]['direct']))
            reply_markup = InlineKeyboardMarkup([buttons[i:i + 2] for i in range(0, len(buttons), 2)]) if buttons else None

        if client.db:
            try:
                db_msg = await client.send_message(
                    chat_id=client.db,
                    text=final_text,
                    reply_markup=None,
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.HTML
                )
                payload = await encode(f"single_{client.db}_{db_msg.id}")
                sharing_link = await get_redirect_link(client, payload, use_redirector=True)
                await prompt.edit_text(
                    f"<b>✅ 𝖠𝗎𝗍𝗈𝖻𝖺𝗍𝖼𝗁 𝖥𝗈𝗋𝗆𝖺𝗍 𝖲𝖺𝗏𝖾𝖽 𝖳𝗈 𝖣𝖻!</b>\n\n<b>🔗 𝖲𝗁𝖺𝗋𝗂𝗇𝗀 𝖫𝗂𝗇𝗄:</b>\n<code>{sharing_link}</code>",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✦ 𝖮𝗉𝖾𝗇 𝖫𝗂𝗇𝗄", url=sharing_link)]]),
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.HTML
                )

                if getattr(client, 'redirector_log', None):
                    try:
                        await client.send_message(
                            chat_id=client.redirector_log,
                            text=f"<b>📥 𝖭𝖾𝗐 𝖠𝗎𝗍𝗈𝖻𝖺𝗍𝖼𝗁 𝖢𝗈𝗅𝗅𝖾𝖼𝗍𝖾𝖽!</b>\n\n{final_text}\n\n<b>🔗 𝖲𝗁𝖺𝗋𝗂𝗇𝗀 𝖫𝗂𝗇𝗄:</b> {sharing_link}",
                            disable_web_page_preview=True,
                            parse_mode=ParseMode.HTML
                        )
                    except Exception as e:
                        logger.error(f"Failed to collect autobatch: {e}")

            except Exception as e:
                logger.error(f"Failed to send to DB: {e}")
                await prompt.edit_text(
                    final_text,
                    reply_markup=None,
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.HTML
                )
        else:
            await prompt.edit_text(
                final_text,
                reply_markup=None,
                disable_web_page_preview=True,
                parse_mode=ParseMode.HTML
            )
    except Exception:
        logger.error(traceback.format_exc())
        await message.reply_text(f"<b>❌ 𝖠𝗇 𝖾𝗋𝗋𝗈𝗋 𝗈𝖼𝖼𝗎𝗋𝗋𝖾𝖽! 𝖯𝗅𝖾𝖺𝗌𝖾 𝖼𝗁𝖾𝖼𝗄 𝗒𝗈𝗎𝗋 𝗍𝖾𝗆𝗉𝗅𝖺𝗍𝖾 𝖿𝗈𝗋 𝖿𝗈𝗋𝗆𝖺𝗍𝗍𝗂𝗇𝗀 𝖾𝗋𝗋𝗈𝗋𝗌.</b>")
