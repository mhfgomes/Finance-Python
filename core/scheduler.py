import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


def start_scheduler():
    from core.services.rate_updater import fetch_and_update_rates

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        fetch_and_update_rates,
        trigger=IntervalTrigger(hours=24),
        id='update_exchange_rates',
        replace_existing=True,
        max_instances=1,
        next_run_time=datetime.now(),  # run immediately on startup
    )
    scheduler.start()
    logger.info('Exchange rate scheduler started (runs every 24 h).')
