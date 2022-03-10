from wbb import app, SUDOERS, BOT_ID, BOT_NAME
from wbb.utils.filter_groups import global_stats_group
from wbb.core.decorators.errors import capture_err
from wbb.utils.fetch import fetch
from wbb.modules import ALL_MODULES
from wbb.utils.dbfunctions import (
    is_served_chat,
    get_served_chats,
    add_served_chat,
    remove_served_chat,
    get_notes_count,
    get_filters_count,
    get_warns_count,
    get_karmas_count,
    get_gbans_count
)
from pyrogram import filters

import asyncio


@app.on_message(filters.text, group=global_stats_group)
@capture_err
async def chat_watcher(_, message):
    chat_id = message.chat.id
    served_chat = await is_served_chat(chat_id)
    if served_chat:
        return
    await add_served_chat(chat_id)


@app.on_message(
    filters.command("gstats") & filters.user(SUDOERS)
    & ~filters.edited
)
@capture_err
async def global_stats(_, message):
    m = await app.send_message(
        message.chat.id,
        text="__**Analysing Stats**__",
        disable_web_page_preview=True
    )

    total_users = 0
    chats = await get_served_chats()
    served_chats = [int(chat["chat_id"]) for chat in chats]
    await m.edit(
            f"__**Analysing Stats Might Take {len(served_chats)*6}+ Seconds.**__",
            disable_web_page_preview=True
            )
    for served_chat in served_chats:
        try:
            await app.get_chat_members(served_chat, BOT_ID)
            await asyncio.sleep(3)
        except Exception:
            await remove_served_chat(served_chat)
            served_chats.remove(served_chat)
    for i in served_chats:
        try:
            mc = (await app.get_chat(i)).members_count
            total_users += int(mc)
        except Exception:
            await remove_served_chat(served_chat)
        await asyncio.sleep(3)

    # Gbans count
    gbans = await get_gbans_count()
    # Notes count across chats
    _notes = await get_notes_count()
    notes_count = _notes["notes_count"]
    notes_chats_count = _notes["chats_count"]

    # Filters count across chats
    _filters = await get_filters_count()
    filters_count = _filters["filters_count"]
    filters_chats_count = _filters["chats_count"]

    # Warns count across chats
    _warns = await get_warns_count()
    warns_count = _warns["warns_count"]
    warns_chats_count = _warns["chats_count"]

    # Karmas count across chats
    _karmas = await get_karmas_count()
    karmas_count = _karmas["karmas_count"]
    karmas_chats_count = _karmas["chats_count"]

    # Contributors/Developers count and commits on github
    url = "https://api.github.com/repos/thehamkercat/williambutcherbot/contributors"
    rurl = "https://github.com/thehamkercat/williambutcherbot"
    developers = await fetch(url)
    commits = sum(developer['contributions'] for developer in developers)
    developers = len(developers)

    # Modules info
    modules_count = len(ALL_MODULES)

    msg = f"""
**Global Stats of {BOT_NAME}**:
**{modules_count}** Modules Loaded
**{gbans}** Globally banned users.
**{filters_count}** Filters, Across **{filters_chats_count}** chats.
**{notes_count}** Notes, Across **{notes_chats_count}** chats.
**{warns_count}** Warns, Across **{warns_chats_count}** chats.
**{karmas_count}** Karma, Across **{karmas_chats_count}** chats.
**{total_users}** Users, Across **{len(served_chats)}** chats.
**{developers}** Developers And **{commits}** Commits On **[Github]({rurl})**."""

    await m.edit(msg, disable_web_page_preview=True)
