from wbb import app, arq, BOT_ID
from wbb.core.decorators.errors import capture_err
from wbb.utils.filter_groups import chatbot_group
from pyrogram import filters


__MODULE__ = "ChatBot"
__HELP__ = "/chatbot [ON|OFF] To Enable Or Disable ChatBot In Your Chat."

active_chats = []

# Enabled | Disable Chatbot


@app.on_message(filters.command("chatbot") & ~filters.edited)
@capture_err
async def chatbot_status(_, message):
    global active_chats
    if len(message.command) != 2:
        await message.reply_text("/chatbot [ON|OFF]")
        return
    status = message.text.split(None, 1)[1]
    chat_id = message.chat.id

    if status == "ON" or status == "on" or status == "On":
        if chat_id not in active_chats:
            active_chats.append(chat_id)
            text = "Chatbot Enabled Reply To Any Message" \
                   + "Of Mine To Get A Reply"
            await message.reply_text(text)
            return
        await message.reply_text("ChatBot Is Already Enabled.")
        return

    elif status == "OFF" or status == "off" or status == "Off":
        if chat_id in active_chats:
            active_chats.remove(chat_id)
            await message.reply_text("Chatbot Disabled!")
            return
        await message.reply_text("ChatBot Is Already Disabled.")
        return

    else:
        await message.reply_text("/chatbot [ON|OFF]")


@app.on_message(filters.text & filters.reply & ~filters.bot &
                ~filters.via_bot & ~filters.forwarded, group=chatbot_group)
@capture_err
async def chatbot_talk(_, message):
    if message.chat.id not in active_chats:
        return
    if not message.reply_to_message:
        return
    if message.reply_to_message.from_user.id != BOT_ID:
        return
    query = message.text
    luna = await arq.luna(query)
    response = luna.response
    await message.reply_text(response)
