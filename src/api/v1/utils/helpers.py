from datetime import datetime, timedelta


def time_to_future(now: datetime, end_date: datetime) -> float:
    """Take  \'now\' and \'end_date\' as input. It returns future time in seconds"""
    future = end_date - now
    seconds = future.total_seconds()

    return float(seconds)
