from service.db_connection import db_executed


def store_appointments(data):
    values = (
        data["thread_id"],
        data["user_id"],
        data["doctor_id"],
        data["appointment_date"],
        data["day_of_week"],
        data["appointment_time"]
    )

    sql = """
        INSERT INTO appointments (thread_id, user_id, doctor_id, appointment_date, day_of_week, appointment_time)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    db_executed("insert", sql, values)