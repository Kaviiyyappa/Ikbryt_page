import os
import time
import pyromod.listen
from datetime import datetime, timedelta
from pytz import timezone
from pyrogram import Client, __version__, enums
from pyrogram.raw.all import layer
from config import Config
from aiohttp import web
from route import web_server
import pyrogram.utils
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# IMPORTANT: Leapcell cannot write outside /tmp
SESSION_PATH = "/tmp/rexbots"

pyrogram.utils.MIN_CHANNEL_ID = -1002964099736
PORT = Config.PORT


class Bot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION_PATH,       # <-- FIXED for Leapcell
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
            parse_mode=enums.ParseMode.HTML
        )
        self.start_time = time.time()

    async def start(self):
        await super().start()
        me = await self.get_me()

        self.mention = me.mention
        self.username = me.username
        self.uptime = Config.BOT_UPTIME

        # Webhook mode
        if Config.WEBHOOK:
            runner = web.AppRunner(await web_server())
            await runner.setup()
            await web.TCPSite(runner, "0.0.0.0", PORT).start()

        print(f"{me.first_name} Started Successfully ✨")

        uptime_seconds = int(time.time() - self.start_time)
        uptime_string = str(timedelta(seconds=uptime_seconds))

        # Send restart alerts to log channels
        for chat_id in [Config.LOG_CHANNEL, Config.SUPPORT_CHAT]:
            if not chat_id:
                continue

            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                await self.send_photo(
                    chat_id=chat_id,
                    photo=Config.START_PIC,
                    caption=(
                        "**I restarted again!**\n\n"
                        f"Uptime before restart: `{uptime_string}`"
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Updates", url="https://t.me/RexBots_Official")]
                    ])
                )
            except Exception as e:
                print(f"Failed to send message in {chat_id}: {e}")


Bot().run()
