# coding: utf-8

import asyncio
import os
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler


def test_apscheduler():
    def tick():
        print('Tick! The time is: %s' % datetime.now())

    async def leave():
        asyncio.get_event_loop().stop()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(tick, 'interval', seconds=1)
    scheduler.add_job(leave, 'interval', seconds=3)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
