import os
import time
import pyromod.listen
from datetime import datetime, timedelta
from pytz import timezone
from aiohttp import web
from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from route import web_server
import pyrogram.utils

# -------------------------------
# IMPORTANT: Leapcell writable path
# -------------------------------
SESSION_PATH = "/data/rexbots"
os.makedirs(SESSION_PATH, exist_ok=True)

pyrogram.utils.MIN_CHANNEL_ID = -1002964099736
PORT = Config.PORT


class Bot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION_PATH,                  # session saved in /tmp
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

        print(f"{me.first_name} Started Successfully ✨")

        self.mention = me.mention
        self.username = me.username

        # -----------------------------------------
        # LEAPCELL HEALTH CHECK ENDPOINT (required)
        # -----------------------------------------
        async def health_check(request):
            return web.Response(text="OK")

        health_app = web.Application()
        health_app.router.add_get("/kaithheathcheck", health_check)

        # Webhook mode
        if Config.WEBHOOK:
            webhook_app = await web_server()
            health_app.add_subapp("/webhook", webhook_app)

        runner = web.AppRunner(health_app)
        await runner.setup()
        await web.TCPSite(runner, "0.0.0.0", PORT).start()

        print(f"Healthcheck running on port {PORT}")

        # -----------------------------------------
        # SEND START MESSAGE
        # -----------------------------------------
        uptime_sec = int(time.time() - self.start_time)
        uptime_str = str(timedelta(seconds=uptime_sec))

        for chat_id in [Config.LOG_CHANNEL, Config.SUPPORT_CHAT]:
            if not chat_id:
                continue

            try:
                await self.send_photo(
                    chat_id=chat_id,
                    photo=Config.START_PIC,
                    caption=(
                        "**I restarted again!**\n\n"
                        f"Uptime before restart: `{uptime_str}`"
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("Updates", url="https://t.me/RexBots_Official")]
                    ])
                )
            except Exception as e:
                print(f"Failed sending message to {chat_id}: {e}")


Bot().run()
