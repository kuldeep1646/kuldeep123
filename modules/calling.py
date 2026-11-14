from twilio.rest import Client

from database.db import get_connection
from modules.config import get_setting


def make_candidate_call(application_id, consent_confirmed=False):
    """
    Start an outbound call to an applicant and save the call record.

    Only call candidates who have explicitly agreed to be contacted.
    """

    if consent_confirmed is not True:
        raise ValueError(
            "Candidate consent is required before making a call."
        )

    account_sid = get_setting("TWILIO_ACCOUNT_SID")
    auth_token = get_setting("TWILIO_AUTH_TOKEN")
    twilio_number = get_setting("TWILIO_PHONE_NUMBER")

    if not account_sid or not auth_token or not twilio_number:
        raise ValueError(
            "Twilio credentials are missing. Configure TWILIO_ACCOUNT_SID, "
            "TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER in your local .env "
            "file or Streamlit Cloud Secrets."
        )

    # Find the candidate and their phone number for this application.
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                applicants.candidate_name,
                applicants.phone
            FROM applications
            JOIN applicants
                ON applications.candidate_id = applicants.candidate_id
            WHERE applications.application_id = ?
            """,
            (application_id,)
        )
        applicant = cursor.fetchone()
    finally:
        connection.close()

    if applicant is None:
        raise ValueError("Application not found.")

    candidate_name, phone_number = applicant

    if not phone_number:
        raise ValueError("Candidate phone number is missing.")

    phone_number = str(phone_number).strip()

    if not phone_number.startswith("+"):
        raise ValueError(
            "Candidate phone number must use international format, "
            "for example +919876543210."
        )

    # Connect to Twilio and initiate the call.
    client = Client(account_sid, auth_token)

    call = client.calls.create(
        to=phone_number,
        from_=twilio_number,
        twiml=(
            "<Response>"
            "<Say>Hello. This is a recruitment team calling "
            "regarding your job application.</Say>"
            "</Response>"
        )
    )

    # Save the Twilio call details in the local database.
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO call_logs (
                application_id,
                phone_number,
                twilio_call_sid,
                call_status,
                consent_status,
                call_outcome
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                application_id,
                phone_number,
                call.sid,
                call.status,
                "Consented",
                "Pending"
            )
        )

        connection.commit()
        call_id = cursor.lastrowid

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    return {
        "call_id": call_id,
        "candidate_name": candidate_name,
        "phone_number": phone_number,
        "twilio_call_sid": call.sid,
        "call_status": call.status
    }


def get_call_history():
    """Return call records with the related candidate and job details."""

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                call_logs.call_id,
                applicants.candidate_name,
                jobs.job_title,
                call_logs.phone_number,
                call_logs.call_status,
                call_logs.call_outcome,
                call_logs.duration,
                call_logs.call_time,
                call_logs.follow_up_date,
                call_logs.notes
            FROM call_logs
            JOIN applications
                ON call_logs.application_id = applications.application_id
            JOIN applicants
                ON applications.candidate_id = applicants.candidate_id
            JOIN jobs
                ON applications.job_id = jobs.job_id
            ORDER BY call_logs.call_id DESC
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()


def update_call_outcome(
    call_id,
    call_outcome,
    notes="",
    follow_up_date=None
):
    """Update the recruiter's outcome, notes and optional follow-up date."""

    allowed_outcomes = [
        "Connected",
        "No Answer",
        "Busy",
        "Call Back Required",
        "Rejected"
    ]

    if call_outcome not in allowed_outcomes:
        raise ValueError("Invalid call outcome.")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE call_logs
            SET
                call_outcome = ?,
                notes = ?,
                follow_up_date = ?
            WHERE call_id = ?
            """,
            (
                call_outcome,
                notes,
                follow_up_date,
                call_id
            )
        )

        updated_rows = cursor.rowcount
        connection.commit()

        return updated_rows

    finally:
        connection.close()
