from apscheduler.schedulers.asyncio import AsyncIOScheduler
async def send_reminders(bot, retriever, my_id, reminder_days):
    stale = retriever.get_stale_notes(reminder_days)
    if "свежие" not in stale: 
        await bot.send_message(my_id, stale)
async def setup_scheduler(bot, cfg, retriever):
    scheduler = AsyncIOScheduler()
    hour, minute = cfg["telegram"]["reminder_time"].split(":")
    scheduler.add_job(
        send_reminders,
        'cron',
        hour=int(hour),
        minute=int(minute),
        args=[bot, retriever, cfg["telegram"]["my_id"], cfg["telegram"]["reminder_days"]]
    )
    scheduler.start()
    return scheduler

