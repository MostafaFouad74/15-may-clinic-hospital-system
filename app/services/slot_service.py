from datetime import datetime, date, time, timedelta


def generate_time_slots_for_day(target_date: date, start_hour: int = 8, end_hour: int = 12, slot_minutes: int = 15):
    slots = []
    current = datetime.combine(target_date, time(hour=start_hour, minute=0))
    end_time = datetime.combine(target_date, time(hour=end_hour, minute=0))

    while current < end_time:
        slots.append(current)
        current += timedelta(minutes=slot_minutes)

    return slots