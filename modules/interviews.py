
from database.db import get_connection

from modules.email_notifications import send_interview_email


def get_interview_email_details(cursor, application_id):
    cursor.execute("""
        SELECT
            applicants.candidate_name,
            applicants.email,
            jobs.job_title
        FROM applications
        JOIN applicants
            ON applications.candidate_id = applicants.candidate_id
        JOIN jobs
            ON applications.job_id = jobs.job_id
        WHERE applications.application_id = ?
    """, (application_id,))

    return cursor.fetchone()


def schedule_interview(
    application_id,
    interview_date,
    interview_time,
    interview_mode,
    venue_or_link,
    interviewer_name,
    confirmation_status="Confirmation Pending"
):
    allowed_modes = ["Online", "Offline", "Phone"]

    allowed_statuses = [
        "Confirmation Pending",
        "Confirmed",
        "Rescheduled",
        "Cancelled"
    ]

    if interview_mode not in allowed_modes:
        raise ValueError("Invalid interview mode.")

    if confirmation_status not in allowed_statuses:
        raise ValueError("Invalid confirmation status.")

    if not interviewer_name.strip():
        raise ValueError("Interviewer name is required.")

    if interview_mode in ["Online", "Offline"] and not venue_or_link.strip():
        raise ValueError("Meeting link or venue is required.")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        candidate = get_interview_email_details(
            cursor, application_id
        )

        if candidate is None:
            raise ValueError("Application not found.")

        cursor.execute("""
            INSERT INTO interviews (
                application_id,
                interview_date,
                interview_time,
                interview_mode,
                venue_or_link,
                interviewer_name,
                confirmation_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            application_id,
            interview_date,
            interview_time,
            interview_mode,
            venue_or_link,
            interviewer_name,
            confirmation_status
        ))

        interview_id = cursor.lastrowid
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    if confirmation_status != "Cancelled":
        try:
            send_interview_email(
                recipient_email=candidate[1],
                candidate_name=candidate[0],
                job_title=candidate[2],
                interview_date=interview_date,
                interview_time=interview_time,
                interview_mode=interview_mode,
                venue_or_link=venue_or_link,
                interviewer_name=interviewer_name,
                email_type="confirmation"
            )
            print("Interview confirmation email sent.")

        except Exception as error:
            raise RuntimeError(
                f"Interview ID {interview_id} was saved, "
                f"but the confirmation email failed: {error}"
            )

    return interview_id


def get_all_interviews():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                interviews.interview_id,
                applicants.candidate_name,
                jobs.job_title,
                interviews.application_id,
                interviews.interview_date,
                interviews.interview_time,
                interviews.interview_mode,
                interviews.venue_or_link,
                interviews.interviewer_name,
                interviews.confirmation_status
            FROM interviews
            JOIN applications
                ON interviews.application_id = applications.application_id
            JOIN applicants
                ON applications.candidate_id = applicants.candidate_id
            JOIN jobs
                ON applications.job_id = jobs.job_id
            ORDER BY
                interviews.interview_date ASC,
                interviews.interview_time ASC
        """)

        return cursor.fetchall()

    finally:
        connection.close()


def update_interview(
    interview_id,
    interview_date,
    interview_time,
    interview_mode,
    venue_or_link,
    interviewer_name,
    confirmation_status
):
    allowed_modes = ["Online", "Offline", "Phone"]

    allowed_statuses = [
        "Confirmation Pending",
        "Confirmed",
        "Rescheduled",
        "Cancelled"
    ]

    if interview_mode not in allowed_modes:
        raise ValueError("Invalid interview mode.")

    if confirmation_status not in allowed_statuses:
        raise ValueError("Invalid confirmation status.")

    if not interviewer_name.strip():
        raise ValueError("Interviewer name is required.")

    if interview_mode in ["Online", "Offline"] and not venue_or_link.strip():
        raise ValueError("Meeting link or venue is required.")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                application_id,
                interview_date,
                interview_time,
                interview_mode,
                venue_or_link,
                interviewer_name,
                confirmation_status
            FROM interviews
            WHERE interview_id = ?
        """, (interview_id,))

        old_record = cursor.fetchone()

        if old_record is None:
            raise ValueError("Interview not found.")

        application_id = old_record[0]

        candidate = get_interview_email_details(
            cursor, application_id
        )

        cursor.execute("""
            UPDATE interviews
            SET
                interview_date = ?,
                interview_time = ?,
                interview_mode = ?,
                venue_or_link = ?,
                interviewer_name = ?,
                confirmation_status = ?
            WHERE interview_id = ?
        """, (
            interview_date,
            interview_time,
            interview_mode,
            venue_or_link,
            interviewer_name,
            confirmation_status,
            interview_id
        ))

        updated_rows = cursor.rowcount
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    if updated_rows == 0:
        return 0

    old_status = old_record[6]

    if confirmation_status == "Cancelled" and old_status != "Cancelled":
        email_type = "cancellation"
        email_date = old_record[1]
        email_time = old_record[2]
        email_mode = old_record[3]
        email_venue = old_record[4]
        email_interviewer = old_record[5]

    elif confirmation_status != "Cancelled" and (
        confirmation_status == "Rescheduled"
        or interview_date != old_record[1]
        or interview_time != old_record[2]
        or interview_mode != old_record[3]
        or venue_or_link != old_record[4]
    ):
        email_type = "reschedule"
        email_date = interview_date
        email_time = interview_time
        email_mode = interview_mode
        email_venue = venue_or_link
        email_interviewer = interviewer_name

    else:
        return updated_rows

    try:
        send_interview_email(
            recipient_email=candidate[1],
            candidate_name=candidate[0],
            job_title=candidate[2],
            interview_date=email_date,
            interview_time=email_time,
            interview_mode=email_mode,
            venue_or_link=email_venue,
            interviewer_name=email_interviewer,
            email_type=email_type
        )

        print(f"Interview {email_type} email sent.")

    except Exception as error:
        raise RuntimeError(
            f"Interview changes were saved, "
            f"but the {email_type} email failed: {error}"
        )

    return updated_rows
