from datetime import date, timedelta

def get_next_date_from_day(day_name):
    today = date.today()
    days_ahead = (["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
                  .index(day_name) - today.weekday()) % 7
    return today + timedelta(days=days_ahead)