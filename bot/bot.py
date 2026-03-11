import asyncio
from aiogram import Bot, Dispatcher
from core.config import load_config
from core.retriever import Retriever
from bot.handler import router, init_agent
from bot.scheduler import setup_scheduler

async def main():
    cfg = load_config()
    bot = Bot(token=cfg["telegram"]["bot_token"])
    dp = Dispatcher()
    init_agent(cfg)
    dp.include_router(router)
    
    retriever = Retriever(cfg)
    await setup_scheduler(bot, cfg, retriever)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())