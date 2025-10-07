from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    BotFrameworkAdapter,
    ConversationState,
    MemoryStorage,
    TurnContext,
)
from botbuilder.schema import Activity
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot import StandupBot
import os

APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)
memory = MemoryStorage()
conversation_state = ConversationState(memory)
bot = StandupBot(conversation_state)

async def messages(req):
    body = await req.json()
    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")
    response = await adapter.process_activity(activity, auth_header, bot.on_turn)
    return web.Response(status=201)

app = web.Application()
app.router.add_post("/api/messages", messages)

async def send_daily_standup():
    if not bot.conversation_references:
        print("No users to send scheduled standup to yet.")
    for conv_ref in bot.conversation_references.values():
        await adapter.continue_conversation(
            conv_ref,
            lambda turn_context: turn_context.send_activity("👋 Good morning! It's time for your daily standup. Please reply to start."),
            APP_ID
        )
        print("Sent scheduled standup message.")

if __name__ == "__main__":
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_daily_standup, "cron", hour=9, minute=1)  # or "interval", minutes=1 for testing

    async def on_startup(app):
        scheduler.start()
        print("Scheduler started.")

    app.on_startup.append(on_startup)

    print("Bot is running.")
    web.run_app(app, host="localhost", port=3978)

