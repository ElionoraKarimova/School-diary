from django.db import connection
def student_average_via_plpgsql(student_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT student_average(%s);", [student_id])
        row = cursor.fetchone()
    return float(row[0]) if row and row[0] is not None else None