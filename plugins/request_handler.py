from pyrogram import Client
from pyrogram.types import ChatMemberUpdated, ChatJoinRequest
from pyrogram.enums import ChatMemberStatus, ParseMode

@Client.on_chat_member_updated()
async def member_update_handler(client: Client, update: ChatMemberUpdated):
    """Synchronizes user membership status with the database."""
    if not update.new_chat_member:
        return

    user_id = update.from_user.id
    channel_id = update.chat.id
    status = update.new_chat_member.status

    try:
        if status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await client.mongodb.add_channel_user(channel_id, user_id)
            await client.mongodb.add_user(user_id, client.me.id)
        elif status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
            await client.mongodb.remove_channel_user(channel_id, user_id)

    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error in member_update_handler: {e}")

@Client.on_chat_join_request()
async def join_request_handler(client: Client, request: ChatJoinRequest):
    """Handles join requests by adding users to the database without auto-approving."""
    user_id = request.from_user.id
    try:
        await client.mongodb.add_user(user_id, client.me.id)
        await client.send_message(
            chat_id=user_id,
            text="<b>𝖸𝗈𝗎𝗋 𝗃𝗈𝗂𝗇 𝗋𝖾𝗊𝗎𝖾𝗌𝗍 𝗁𝖺𝗌 𝖻𝖾𝖾𝗇 𝗌𝖾𝗇𝗍. 𝖯𝗅𝖾𝖺𝗌𝖾 𝗐𝖺𝗂𝗍 𝖿𝗈𝗋 𝖺𝖽𝗆𝗂𝗇 𝖺𝗉𝗉𝗋𝗈𝗏𝖺𝗅.</b>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        client.LOGGER(__name__, client.name).error(f"Error in join_request_handler: {e}")
