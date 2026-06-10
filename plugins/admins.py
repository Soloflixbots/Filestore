from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from config import OWNER_ID
import time
import os
import sys
import psutil
import shutil

async def admins(client, query):
    if not (query.from_user.id==client.owner):
        return await query.answer('𝖳𝗁𝗂𝗌 𝖼𝖺𝗇 𝗈𝗇𝗅𝗒 𝖻𝖾 𝗎𝗌𝖾𝖽 𝖻𝗒 𝗈𝗐𝗇𝖾𝗋.')
    msg = f"""<blockquote>**𝖠𝖽𝗆𝗂𝗇 𝖲𝖾𝗍𝗍𝗂𝗇𝗀𝗌:**</blockquote>
**𝖠𝖽𝗆𝗂𝗇 𝖴𝗌𝖾𝗋 𝖨𝖽𝗌:** {", ".join(f"`{a}`" for a in client.admins)}

__𝖴𝗌𝖾 𝗍𝗁𝖾 𝖺𝗉𝗉𝗋𝗈𝗉𝗋𝗂𝖺𝗍𝖾 𝖻𝗎𝗍𝗍𝗈𝗇 𝖻𝖾𝗅𝗈𝗶 𝗍𝗈 𝖺𝖽𝖽 𝗈𝗋 𝗋𝖾𝗆𝗈𝗏𝖾 𝖺𝗇 𝖺𝖽𝗆𝗂𝗇 𝖻𝖺𝗌𝖾𝖽 𝗈𝗇 𝗒𝗈𝗎𝗋 𝗇𝖾𝖾𝖽𝗌!__
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton('✦ 𝖠𝖽𝖽 𝖠𝖽𝗆𝗂𝗇', 'add_admin'), InlineKeyboardButton('✦ 𝖱𝖾𝗆𝗈𝗏𝖾 𝖠𝖽𝗆𝗂𝗇', 'rm_admin')],
        [InlineKeyboardButton('✦ 𝖡𝖺𝖼𝗄', 'settings_pg1')]
    ])
    await query.message.edit_text(msg, reply_markup=reply_markup)
    return

@Client.on_message(filters.command("usage"))
async def usage_cmd(client: Client, message: Message):
    if message.from_user.id not in client.admins:
        return await message.reply(client.reply_text)
    reply = await message.reply("`𝖾𝗑𝗍𝗋𝖺𝖼𝗍𝗂𝗇𝗀 𝖺𝗅𝗅 𝖴𝗌𝖺𝗀𝖾!!`")

    total, used, free = shutil.disk_usage("/")
    total_gb, used_gb, free_gb = total / (1024**3), used / (1024**3), free / (1024**3)

    ram = psutil.virtual_memory()
    total_ram, used_ram, free_ram = ram.total / (1024**3), ram.used / (1024**3), ram.available / (1024**3)

    swap = psutil.swap_memory()
    total_swap, used_swap, free_swap = swap.total / (1024**3), swap.used / (1024**3), swap.free / (1024**3)

    try:
        net_io = psutil.net_io_counters()
        bytes_sent, bytes_recv = net_io.bytes_sent / (1024**2), net_io.bytes_recv / (1024**2)
        net_msg = f"**📡 Network:** `↑ {bytes_sent:.2f} MB` | `↓ {bytes_recv:.2f} MB`\n"
    except (PermissionError, AttributeError):
        net_msg = ""

    process = psutil.Process()
    bot_cpu, bot_mem = process.cpu_percent(interval=1), process.memory_info().rss / (1024**2)

    msg = (
        f"<blockquote>**📊 𝖲𝗒𝗌𝗍𝖾𝗆 𝖴𝗌𝖺𝗀𝖾 𝖲𝗍𝖺𝗍𝗌:**</blockquote>\n"
        f"**💾 𝖣𝗂𝗌𝗄:** `{used_gb:.2f} 𝖦𝖡 / {total_gb:.2f} 𝖦𝖡`\n"
        f"**🖥 𝖱𝖺𝗆:** `{used_ram:.2f} 𝖦𝖡 / {total_ram:.2f} 𝖦𝖡` ({ram.percent}%)\n"
        f"**🔄 𝖲𝗐𝖺𝗉:** `{used_swap:.2f} 𝖦𝖡 / {total_swap:.2f} 𝖦𝖡` ({swap.percent}%)\n"
        f"**⚡ 𝖢𝖯𝖴:** `{psutil.cpu_percent(interval=1):.2f}%`\n"
        f"{net_msg}"
        f"**🤖 𝖡𝗈𝗍:** `𝖢𝖯𝖴 {bot_cpu:.2f}%` | `𝖬𝖾𝗆 {bot_mem:.2f} 𝖬𝖡`"
    )

    await reply.edit_text(msg)

@Client.on_callback_query(filters.regex("^add_admin$"))
async def add_new_admins(client: Client, query: CallbackQuery):
    await query.answer()
    if not query.from_user.id in client.admins:
        return await client.send_message(query.from_user.id, client.reply_text)
    try:
        ids_msg = await client.ask(query.from_user.id, "𝖲𝖾𝗇𝖽 𝗎𝗌𝖾𝗋 𝗂𝖽𝗌 𝗌𝖾𝗉𝖾𝗋𝖺𝗍𝖾𝖽 𝖻𝗒 𝖺 𝗌𝗉𝖺𝖼𝖾 𝗂𝗇 𝗍𝗁𝖾 𝗇𝖾𝗑𝗍 𝟨𝟢 𝗌𝖾𝖼𝗈𝗇𝖽𝗌!\n𝖤𝗀: `𝟪𝟥𝟪𝟤𝟩𝟪𝟨𝟪𝟤 𝟪𝟥𝟨𝟤𝟤𝟫𝟤𝟪 𝟪𝟤𝟩𝟪𝟫𝟫𝟤𝟪`", filters=filters.text, timeout=60)
        ids = ids_msg.text.split()
        for identifier in ids:
            if int(identifier) not in client.admins:
                client.admins.append(int(identifier))
        await client.mongodb.save_settings(client.name, client.get_current_settings())
        await admins(client, query)
        await ids_msg.reply(f"__{len(ids)} 𝖺𝖽𝗆𝗂𝗇 {'𝗂𝖽' if len(ids)==1 else '𝗂𝖽𝗌'} 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝗉𝗋𝗈𝗆𝗈𝗍𝖾𝖽!!__")
    except Exception as e:
        await ids_msg.reply(f"Error: {e}")
@Client.on_callback_query(filters.regex("^rm_admin$"))
async def remove_admins(client: Client, query: CallbackQuery):
    await query.answer()
    if not query.from_user.id in client.admins:
        return await client.send_message(query.from_user.id, client.reply_text)
    try:
        ids_msg = await client.ask(query.from_user.id, "𝖲𝖾𝗇𝖽 𝗎𝗌𝖾𝗋 𝗂𝖽𝗌 𝗌𝖾𝗉𝖾𝗋𝖺𝗍𝖾𝖽 𝖻𝗒 𝖺 𝗌𝗉𝖺𝖼𝖾 𝗂𝗇 𝗍𝗁𝖾 𝗇𝖾𝗑𝗍 𝟨𝟢 𝗌𝖾𝖼𝗈𝗇𝖽𝗌!\n𝖤𝗀: `𝟪𝟥𝟪𝟤𝟩𝟪𝟨𝟪𝟤 𝟪𝟥𝟨𝟤𝟤𝟫𝟤𝟪 𝟪𝟤𝟩𝟪𝟫𝟫𝟤𝟪`", filters=filters.text, timeout=60)
        ids = ids_msg.text.split()
        for identifier in ids:
            if int(identifier) == client.owner:
                await client.send_message(query.from_user.id, "𝖸𝗈𝗎 𝖼𝖺𝗇𝗇𝗈𝗍 𝗋𝖾𝗆𝗈𝗏𝖾 𝗍𝗁𝖾 𝗈𝗐𝗇𝖾𝗋 𝖿𝗋𝗈𝗆 𝗍𝗁𝖾 𝖺𝖽𝗆𝗂𝗇 𝗅𝗂𝗌𝗍!")
                continue
            if int(identifier) in client.admins:
                client.admins.remove(int(identifier))
        await client.mongodb.save_settings(client.name, client.get_current_settings())
        await admins(client, query)
        await ids_msg.reply(f"__{len(ids)} 𝖺𝖽𝗆𝗂𝗇 {'𝗂𝖽' if len(ids)==1 else '𝗂𝖽𝗌'} 𝗁𝖺𝗏𝖾 𝖻𝖾𝖾𝗇 𝗋𝖾𝗆𝗈𝗏𝖾𝖽!!__")
    except Exception as e:
        await ids_msg.reply(f"Error: {e}")