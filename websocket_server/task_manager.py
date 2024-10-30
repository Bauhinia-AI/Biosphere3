import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from loguru import logger


class OrphanedTaskManager:
    def __init__(self):
        # character_id -> (task_list, expiration_time)
        self.orphaned_tasks = {}
        self.timeout_duration = 60
        self.lock = asyncio.Lock()
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    async def add_orphaned_tasks(self, character_id, tasks):
        async with self.lock:
            expiration_time = datetime.now() + timedelta(seconds=self.timeout_duration)
            self.orphaned_tasks[character_id] = (tasks, expiration_time)

            self.scheduler.add_job(
                self.cleanup_expired_tasks,
                trigger=DateTrigger(run_date=expiration_time),
                args=[character_id],
                id=f"cleanup_expired_tasks_{character_id}",
                replace_existing=True,
            )

            logger.info(
                f"⏰ Scheduled cleanup of expired tasks for character {character_id} at {expiration_time}"
            )

    async def cleanup_expired_tasks(self, character_id):
        async with self.lock:
            if character_id in self.orphaned_tasks:
                tasks, _ = self.orphaned_tasks[character_id]
                for task in tasks:
                    if not task.done():
                        task.cancel()
                del self.orphaned_tasks[character_id]
                logger.info(f"🗑️ Cleaned up expired tasks for character {character_id}")

    async def get_tasks(self, character_id):
        async with self.lock:
            return self.orphaned_tasks.get(character_id, ([], None))[0]

    async def has_orphaned_tasks(self, character_id):
        async with self.lock:
            return character_id in self.orphaned_tasks

    def get_remaining_time(self, character_id):
        if character_id in self.orphaned_tasks:
            _, expiration_time = self.orphaned_tasks[character_id]
            return (expiration_time - datetime.now()).total_seconds()
        return 0

    async def extend_expiration(self, character_id, additional_time=3600):
        async with self.lock:
            if character_id in self.orphaned_tasks:
                tasks, expiration_time = self.orphaned_tasks[character_id]
                new_expiration_time = expiration_time + timedelta(
                    seconds=additional_time
                )
                self.orphaned_tasks[character_id] = (tasks, new_expiration_time)

                self.scheduler.reschedule_job(
                    id=f"cleanup_expired_tasks_{character_id}",
                    trigger=DateTrigger(run_date=new_expiration_time),
                    replace_existing=True,
                )
                logger.info(
                    f"⏱️ Extended expiration time for character {character_id} by {additional_time} seconds"
                )

    async def get_all_active_tasks_status(self):
        async with self.lock:
            status = {}
            for character_id, (tasks, expiration_time) in self.orphaned_tasks.items():
                active_tasks = [task for task in tasks if not task.done()]
                remaining_time = (expiration_time - datetime.now()).total_seconds()
                status[character_id] = {
                    "active_tasks": len(active_tasks),
                    "remaining_time": remaining_time,
                }
            logger.info(f"🔍 All active tasks status: {status}")
            return status
