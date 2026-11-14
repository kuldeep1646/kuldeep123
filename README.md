# Recruitment Workflow Automation System

A Streamlit-based recruitment workflow application that demonstrates job management, applicant management, rule-based candidate screening, candidate calling through Twilio, interview scheduling, and interview email notifications through Gmail SMTP.

## Features

- **Job Management:** Create, view, edit, and delete job postings.
- **Applicant Management:** Import applicants from CSV, view applicants, and update application statuses.
- **Candidate Screening:** Score applicants using skill and experience matching rules.
- **Calling Management:** Initiate consent-based candidate calls through Twilio and maintain call records.
- **Interview Scheduling:** Schedule and manage candidate interviews.
- **Email Notifications:** Send interview confirmation, rescheduling, and cancellation emails through Gmail SMTP.
- **Dashboard:** View the recruitment workspace.

## Technology stack

| Area | Technology |
|---|---|
| User interface | Streamlit |
| Programming language | Python |
| Data processing | pandas |
| Database | SQLite |
| Email | Gmail SMTP (`smtplib`, `email.message`) |
| Outbound calling | Twilio Python SDK |
| Local configuration | `python-dotenv` |
| Hosting | Streamlit Community Cloud |
| Source control | Git and GitHub |

## Project structure

```text
recruitment_workflow_automation/
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── database/
│   ├── __init__.py
│   └── db.py
├── modules/
│   ├── __init__.py
│   ├── applicants.py
│   ├── calling.py
│   ├── config.py
│   ├── email_notifications.py
│   ├── interviews.py
│   ├── jobs.py
│   └── screening.py
├── .gitignore
├── app.py
├── README.md
└── requirements.txt
```

## Run locally

1. Install Python 3.10 or newer.
2. Clone or download this repository.
3. Open a terminal in the project directory.
4. Create and activate a virtual environment:

   **Windows PowerShell**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

5. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

6. Create a `.env` file in the project root if you want to enable email and calling features:
   ```env
   EMAIL_ADDRESS=your_gmail_address@gmail.com
   EMAIL_APP_PASSWORD=your_gmail_app_password
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   ```

   Use a Gmail App Password, not your normal Gmail password. Keep `.env` private.

7. Start the app:
   ```powershell
   streamlit run app.py
   ```

The application creates a new SQLite database at `database/recruitment.db` on first run. This repository intentionally does not include a database file or real candidate records.

## Deploy to Streamlit Community Cloud

1. Push this project to a GitHub repository. Do not commit `.env`, `database/recruitment.db`, or `.streamlit/secrets.toml`.
2. Sign in to Streamlit Community Cloud using your GitHub account.
3. Create an app and select this repository, branch, and `app.py` as the main file.
4. In the app's settings, open **Secrets** and add the credential values in TOML format. Use `.streamlit/secrets.toml.example` as a key-name reference, replacing every placeholder with your own values.
5. Deploy and test the public app.

**Demo database note:** The app uses SQLite in the deployed app's local filesystem. Streamlit Community Cloud does not provide a durable database service for files written into the app container. Data may be lost when the app is restarted, redeployed, or moved to a new container. This is acceptable for a temporary portfolio demonstration, but use a managed database for persistent real-world use.

**Calling note:** Twilio trial accounts can have restrictions, including calling only verified destination numbers. Do not place calls to real candidates as part of a public portfolio demonstration. Use your own verified test number and obtain consent before any test call.

**Privacy note:** Use fictional candidate data in the portfolio demo. Do not upload personal candidate records, secrets, or credentials to GitHub.

## Architecture

The application follows a simple modular structure:

- `app.py` is the Streamlit presentation layer. It displays the dashboard, navigation, forms, tables, and user actions.
- `modules/` contains the recruitment business logic. Each module handles a specific capability such as jobs, applicants, screening, calling, interviews, or email notifications.
- `database/db.py` creates the SQLite database, defines the core tables, and provides database connections.
- `modules/config.py` reads local environment variables from `.env` and falls back to Streamlit Cloud Secrets for deployment.

## Main workflow

1. Add a job posting.
2. Import applicants from a CSV file.
3. Review applicants and their application records.
4. Run candidate screening based on required skills and experience.
5. Contact shortlisted candidates by phone when consent is confirmed.
6. Schedule an interview for a shortlisted candidate.
7. Automatically send confirmation, rescheduling, or cancellation emails when the corresponding interview action occurs.
8. Review recruitment and interview records in the application.

## Limitations and future improvements

- Replace SQLite with a managed PostgreSQL database for persistent multi-user deployment.
- Add user authentication and role-based access control before any real organizational use.
- Add email delivery logs, retry handling, and notification status tracking.
- Add a Twilio status callback/webhook to update call outcomes automatically.
- Add automated tests and CI checks.
- Add privacy controls, audit logs, and data-retention policies before processing real candidate data.

## Disclaimer

This project is a portfolio/demo application. It is not intended to store or process real candidate data in its current deployment configuration.
