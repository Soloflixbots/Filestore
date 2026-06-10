

import asyncio
from bot import Bot
from pyrogram import compose, idle
from config import BOTS, PORT
from aiohttp import web

async def handle_health_check(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Web server started on port {PORT}")

async def main():
    await start_web_server()
    app = []

    for config in BOTS:
        bot = Bot(config)
        app.append(bot)

    if app:
        master_bot = app[0]
        try:
            clones = await master_bot.mongodb.get_clones()
            for clone_config in clones:
                app.append(Bot(clone_config))
        except Exception as e:
            print(f"Failed to load clones: {e}")

    if not app:
        print("No valid bot configurations found in config.py. Exiting.")
        return

    await compose(app)
    await idle()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped manually.")
    except Exception as e:
        print(f"An unexpected error occurred during startup: {e}")