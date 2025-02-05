from __future__ import unicode_literals
from urllib.parse import urlparse
import youtube_dl
import aiohttp
import aiofiles
import os
from random import randint
from pyrogram import filters
from wbb import app, SUDOERS, arq, MAIN_CHATS
from wbb.core.decorators.errors import capture_err
from wbb.utils.pastebin import paste

__MODULE__ = "Music"
__HELP__ = """/ytmusic [link] To Download Music From Various Websites Including Youtube.
/saavn [query] To Download Music From Saavn.
/deezer [query] To Download Music From Deezer.
/lyrics [query] To Get Lyrics Of A Song."""

ydl_opts = {
    'format': 'bestaudio/best',
    'writethumbnail': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }]
}


# Ytmusic

@app.on_message(filters.command("ytmusic") & ~filters.edited & filters.user(SUDOERS))
@capture_err
async def music(_, message):
    if len(message.command) != 2:
        await message.reply_text("/ytmusic needs a link as argument")
        return
    link = message.text.split(None, 1)[1]
    m = await message.reply_text(f"Downloading {link}",
                                 disable_web_page_preview=True)
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
            # .webm -> .weba
            basename = audio_file.rsplit(".", 1)[-2]
            thumbnail_url = info_dict['thumbnail']
            thumbnail_file = basename + "." + \
                get_file_extension_from_url(thumbnail_url)
            audio_file = basename + ".mp3"
    except Exception as e:
        await m.edit(str(e))
        return
        # info
    title = info_dict['title']
    performer = info_dict['uploader']
    duration = int(float(info_dict['duration']))
    await m.delete()
    await message.reply_chat_action("upload_document")
    await message.reply_audio(audio_file, duration=duration, performer=performer,
                              title=title, thumb=thumbnail_file)
    os.remove(audio_file)
    os.remove(thumbnail_file)


def get_file_extension_from_url(url):
    url_path = urlparse(url).path
    basename = os.path.basename(url_path)
    return basename.split(".")[-1]


# Funtion To Download Song
async def download_song(url):
    song_name = f"{randint(6969, 6999)}.mp3"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(song_name, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return song_name

is_downloading = False
# Jiosaavn Music


@app.on_message(filters.command("saavn") & ~filters.edited)
@capture_err
async def jssong(_, message):
    global is_downloading
    if len(message.command) < 2:
        await message.reply_text("/saavn requires an argument.")
        return
    if is_downloading:
        await message.reply_text("Another download is in progress, try again after sometime.")
        return
    is_downloading = True
    text = message.text.split(None, 1)[1]
    query = text.replace(" ", "%20")
    m = await message.reply_text("Searching...")
    try:
        songs = await arq.saavn(query)
        sname = songs[0].song
        slink = songs[0].media_url
        ssingers = songs[0].singers
        await m.edit("Downloading")
        song = await download_song(slink)
        await m.edit("Uploading")
        await message.reply_audio(audio=song, title=sname,
                                  performer=ssingers)
        os.remove(song)
        await m.delete()
    except Exception as e:
        is_downloading = False
        await m.edit(str(e))
        return
    is_downloading = False

# Deezer Music


@app.on_message(filters.command("deezer") & ~filters.edited)
@capture_err
async def deezsong(_, message):
    global is_downloading
    if len(message.command) < 2:
        await message.reply_text("/deezer requires an argument.")
        return
    if is_downloading:
        await message.reply_text("Another download is in progress, try again after sometime.")
        return
    is_downloading = True
    text = message.text.split(None, 1)[1]
    query = text.replace(" ", "%20")
    m = await message.reply_text("Searching...")
    try:
        songs = await arq.deezer(query, 1)
        title = songs[0].title
        url = songs[0].url
        artist = songs[0].artist
        await m.edit("Downloading")
        song = await download_song(url)
        await m.edit("Uploading")
        await message.reply_audio(audio=song, title=title,
                                  performer=artist)
        os.remove(song)
        await m.delete()
    except Exception as e:
        is_downloading = False
        await m.edit(str(e))
        return
    is_downloading = False

# Lyrics


@app.on_message(filters.command("lyrics"))
async def lyrics_func(_, message):
    if len(message.command) < 2:
        await message.reply_text("**Usage:**\n/lyrics [QUERY]")
        return
    m = await message.reply_text("**Searching**")
    query = message.text.strip().split(None, 1)[1]
    song = await arq.lyrics(query)
    lyrics = song.lyrics
    if len(lyrics) < 4095:
        await m.edit(f"__{lyrics}__")
        return
    lyrics = await paste(lyrics)
    await m.edit(f"**LYRICS_TOO_LONG:** [URL]({lyrics})")
