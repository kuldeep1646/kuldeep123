
import sqlite3
from pathlib import Path

# Find the location of this file
BASE_DIR = Path(__file__).resolve().parent

# Define where our database will be stored
DATABASE_PATH = BASE_DIR / "recruitment.db"


def get_connection():

    connection = sqlite3.connect(DATABASE_PATH)

    # Enable foreign key checking
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db():

    connection = get_connection()
    cursor = connection.cursor()

    # Create all database tables
    cursor.executescript("""

        CREATE TABLE IF NOT EXISTS jobs (

            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company_name TEXT,
            description TEXT,
            required_skills TEXT,
            min_experience REAL DEFAULT 0,
            location TEXT,
            employment_type TEXT,
            salary_range TEXT,
            indeed_url TEXT,
            posting_date TEXT,
            posting_status TEXT DEFAULT 'Draft',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP

        );


        CREATE TABLE IF NOT EXISTS applicants (

            candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            location TEXT,
            experience_years REAL DEFAULT 0,
            skills TEXT,
            education TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP

        );


        CREATE TABLE IF NOT EXISTS applications (

            application_id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            application_date TEXT,
            category TEXT DEFAULT 'Unreviewed',
            status TEXT DEFAULT 'Pending',
            source TEXT DEFAULT 'Indeed',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (candidate_id)
                REFERENCES applicants(candidate_id),

            FOREIGN KEY (job_id)
                REFERENCES jobs(job_id),

            UNIQUE(candidate_id, job_id)

        );


        CREATE TABLE IF NOT EXISTS screening (

            screening_id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL UNIQUE,
            screening_score REAL,
            screening_remarks TEXT,
            decision TEXT,
            reviewed_by TEXT,
            screened_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (application_id)
                REFERENCES applications(application_id)

        );


        CREATE TABLE IF NOT EXISTS call_logs (

            call_id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            phone_number TEXT,
            twilio_call_sid TEXT UNIQUE,
            call_status TEXT DEFAULT 'Initiated',
            call_outcome TEXT,
            duration INTEGER DEFAULT 0,
            consent_status TEXT,
            follow_up_date TEXT,
            call_time TEXT DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,

            FOREIGN KEY (application_id)
                REFERENCES applications(application_id)

        );


        CREATE TABLE IF NOT EXISTS interviews (

            interview_id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            interview_date TEXT,
            interview_time TEXT,
            interview_mode TEXT,
            venue_or_link TEXT,
            interviewer_name TEXT,
            confirmation_status TEXT DEFAULT 'Confirmation Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (application_id)
                REFERENCES applications(application_id)

        );

    """)

    connection.commit()
    connection.close()


def migrate_call_logs():

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("PRAGMA table_info(call_logs)")

        existing_columns = [
            column[1] for column in cursor.fetchall()
        ]

        new_columns = {
            "twilio_call_sid": "TEXT",
            "call_status": "TEXT DEFAULT 'Initiated'",
            "duration": "INTEGER DEFAULT 0",
            "follow_up_date": "TEXT"
        }

        for column_name, column_type in new_columns.items():

            if column_name not in existing_columns:

                cursor.execute(
                    f"ALTER TABLE call_logs ADD COLUMN {column_name} {column_type}"
                )

        connection.commit()

        print("Call logs database updated successfully!")

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


if __name__ == "__main__":

    init_db()
    migrate_call_logs()

    print("Database created successfully!")
    print("Database location:")
    print(DATABASE_PATH)
