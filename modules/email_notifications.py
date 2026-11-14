
import os
import smtplib

from email.message import EmailMessage
from modules.config import get_setting


def send_interview_email(
    recipient_email,
    candidate_name,
    job_title,
    interview_date,
    interview_time,
    interview_mode,
    venue_or_link,
    interviewer_name,
    email_type="confirmation"
):
    sender_email = get_setting("EMAIL_ADDRESS")
    sender_password = get_setting("EMAIL_APP_PASSWORD")

    if not sender_email or not sender_password:
        raise ValueError(
            "Email credentials are missing. "
            "Please configure EMAIL_ADDRESS and EMAIL_APP_PASSWORD in your local .env "
            "file or Streamlit Cloud Secrets."
        )

    if not recipient_email:
        raise ValueError(
            "The candidate does not have an email address."
        )

    if email_type == "confirmation":
        subject = "Interview Confirmation"

        message_text = f"""
Dear {candidate_name},

Your interview has been scheduled successfully.

Interview Details:

Position: {job_title}
Date: {interview_date}
Time: {interview_time}
Mode: {interview_mode}
Venue / Meeting Link: {venue_or_link}
Interviewer: {interviewer_name}

Please be available at the scheduled time.

Regards,
Recruitment Team
"""

    elif email_type == "reschedule":
        subject = "Interview Rescheduled"

        message_text = f"""
Dear {candidate_name},

Your interview has been rescheduled.

Updated Interview Details:

Position: {job_title}
New Date: {interview_date}
New Time: {interview_time}
Mode: {interview_mode}
Venue / Meeting Link: {venue_or_link}
Interviewer: {interviewer_name}

Please take note of the updated schedule.

Regards,
Recruitment Team
"""

    elif email_type == "cancellation":
        subject = "Interview Cancellation"

        message_text = f"""
Dear {candidate_name},

We regret to inform you that your interview has been cancelled.

Position: {job_title}
Previously Scheduled Date: {interview_date}
Previously Scheduled Time: {interview_time}

We apologise for any inconvenience.

Regards,
Recruitment Team
"""

    else:
        raise ValueError("Invalid email notification type.")

    email = EmailMessage()
    email["Subject"] = subject
    email["From"] = sender_email
    email["To"] = recipient_email
    email.set_content(message_text)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(email)

    return True
