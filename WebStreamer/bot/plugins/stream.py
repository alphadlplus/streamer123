import asyncio
from datetime import datetime, timedelta
from WebStreamer.bot import StreamBot
from WebStreamer.utils.database import Database
from WebStreamer.utils.human_readable import humanbytes, size_gb
from WebStreamer.vars import Var
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
db = Database()


@StreamBot.on_message(filters.private & (filters.document | filters.video | filters.audio) & ~filters.edited, group=4)
async def private_receive_handler(c: Client, m: Message):
    if await db.check_user(m.from_user.id) == False :
        await c.send_message(
                        chat_id=m.chat.id,
                        text='''سلام\n
شما اشتراک تدارید برای خرید اشتراک به ایدی زیر پیام دهید.\n
<a href='https://t.me/alphadlsup'> AlphaDL Suport</a>''',
                        parse_mode="HTML",
                        disable_web_page_preview=True
        )
    if await db.check_user(m.from_user.id) == True:
        if Var.UPDATES_CHANNEL != "None":
            try:
                user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
                if user.status == "kicked":
                    await c.send_message(
                        chat_id=m.chat.id,
                        text="__شما بن شدید به ادمین پیام دهید__\n\n @alphadlsup",
                        parse_mode="Markdown",
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                await c.send_message(
                    chat_id=m.chat.id,
                    text="""<i>عضو کانال الفا دی ال شوید 🔐!</i>""",
                    reply_markup=InlineKeyboardMarkup(
                        [[ InlineKeyboardButton("🤖 عضویت در کانال", url=f"https://t.me/{Var.UPDATES_CHANNEL}") ]]
                    ),
                    parse_mode="HTML"
                )
                return
            except Exception:
                await c.send_message(
                    chat_id=m.chat.id,
                    text="**مشکلی پیش آمده به ادمین اطلاع دهید** [Alphadl suport](https://t.me/alphadlsup).",
                    parse_mode="Markdown",
                    disable_web_page_preview=True)
                return
        try:
            log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
            stream_link = "https://{}/{}".format(Var.FQDN, log_msg.message_id) if Var.ON_HEROKU or Var.NO_PORT else \
                "http://{}:{}/{}".format(Var.FQDN,
                                        Var.PORT,
                                        log_msg.message_id)
            file_size = None
            if m.video:
                file_size = f"{humanbytes(m.video.file_size)}"
            elif m.document:
                file_size = f"{humanbytes(m.document.file_size)}"
            elif m.audio:
                file_size = f"{humanbytes(m.audio.file_size)}"

            file_name = None
            if m.video:
                file_name = f"{m.video.file_name}"
            elif m.document:
                file_name = f"{m.document.file_name}"
            elif m.audio:
                file_name = f"{m.audio.file_name}"

            msg_text ="""
    <b><u> لینک دانلود آمادست</u></b>\n
    <b>📂 نام فایل :</b> <i>{}</i>\n
    <b>📦 اندازه فایل :</b> <i>{}</i>\n
    <b>📥 لینک دانلود :</b> <i>{}</i>\n
    <b>🚸 نکته : لینک پس از 24 ساعت منقضی می شود</b>\n
    <i>🍃 کانال ما :</i> <b>@alphadl</b>
    """
            if await db.check_status(m.from_user.id) == True:
                if await db.ckeck_dailyusage(m.from_user.id, size_gb(file_size)) == True:
                    await db.set_data(log_msg.message_id, int(datetime.timestamp(datetime.now() + timedelta(hours=24))))
                    await log_msg.reply_text(text=f"**RᴇQᴜᴇꜱᴛᴇᴅ ʙʏ :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**Uꜱᴇʀ ɪᴅ :** `{m.from_user.id}`\n**Dᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ :** {stream_link}", disable_web_page_preview=True, parse_mode="Markdown", quote=True)
                    await m.reply_text(
                        text=msg_text.format(file_name, file_size, stream_link),
                        parse_mode="HTML", 
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("دانلود 📥", url=stream_link)]]),
                        quote=True
                    )
                else:
                    await m.reply_text(
                        text='''**حجم استفاده روزانه شما کافی نیست**\n
حجم باقی مانده: {}'''.format(db.info(m.from_user.id)['dailyUsage']),
                        parse_mode="Markdown",
                        disable_web_page_preview=True

                    )
            else:
                await m.reply_text(
                    text='''شما اشتراک تدارید برای خرید اشتراک به ایدی زیر پیام دهید.\n
<a href='https://t.me/alphadlsup'> AlphaDL Suport</a>''',
                        parse_mode="HTML",
                        disable_web_page_preview=True
                )
        except FloodWait as e:
            print(f"Sleeping for {str(e.x)}s")
            await asyncio.sleep(e.x)
            await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(m.from_user.id)}`", disable_web_page_preview=True, parse_mode="Markdown")


@StreamBot.on_message(filters.channel & (filters.document | filters.video) & ~filters.edited, group=-1)
async def channel_receive_handler(bot, broadcast):
    if int(broadcast.chat.id) in Var.BANNED_CHANNELS:
        await bot.leave_chat(broadcast.chat.id)
        return
    try:
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = "https://{}/{}".format(Var.FQDN, log_msg.message_id) if Var.ON_HEROKU or Var.NO_PORT else \
            "http://{}:{}/{}".format(Var.FQDN,
                                    Var.PORT,
                                    log_msg.message_id)
        await log_msg.reply_text(
            text=f"**Cʜᴀɴɴᴇʟ Nᴀᴍᴇ:** `{broadcast.chat.title}`\n**Cʜᴀɴɴᴇʟ ID:** `{broadcast.chat.id}`\n**Rᴇǫᴜᴇsᴛ ᴜʀʟ:** {stream_link}",
            quote=True,
            parse_mode="Markdown"
        )
        await bot.edit_message_reply_markup(
            chat_id=broadcast.chat.id,
            message_id=broadcast.message_id,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Dᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ 📥", url=stream_link)]])
        )
    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=Var.BIN_CHANNEL,
                             text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(w.x)}s from {broadcast.chat.title}\n\n**Cʜᴀɴɴᴇʟ ID:** `{str(broadcast.chat.id)}`",
                             disable_web_page_preview=True, parse_mode="Markdown")
    except Exception as e:
        await bot.send_message(chat_id=Var.BIN_CHANNEL, text=f"**#ᴇʀʀᴏʀ_ᴛʀᴀᴄᴇʙᴀᴄᴋ:** `{e}`", disable_web_page_preview=True, parse_mode="Markdown")
        print(f"Cᴀɴ'ᴛ Eᴅɪᴛ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ!\nEʀʀᴏʀ: {e}")
