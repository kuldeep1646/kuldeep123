
import sqlite3

from database.db import get_connection


# =====================================
# 1. ADD A NEW JOB
# =====================================

def add_job(
    job_title,
    company_name,
    description,
    required_skills,
    min_experience,
    location,
    employment_type,
    salary_range,
    indeed_url,
    posting_date,
    posting_status
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""

        INSERT INTO jobs (

            job_title,
            company_name,
            description,
            required_skills,
            min_experience,
            location,
            employment_type,
            salary_range,
            indeed_url,
            posting_date,
            posting_status

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        job_title,
        company_name,
        description,
        required_skills,
        min_experience,
        location,
        employment_type,
        salary_range,
        indeed_url,
        posting_date,
        posting_status

    ))

    job_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return job_id


# =====================================
# 2. RETRIEVE ALL JOBS
# =====================================

def get_all_jobs():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""

        SELECT *
        FROM jobs
        ORDER BY job_id DESC

    """)

    jobs = cursor.fetchall()

    connection.close()

    return jobs


# =====================================
# 3. RETRIEVE ONE JOB
# =====================================

def get_job_by_id(job_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""

        SELECT *
        FROM jobs
        WHERE job_id = ?

    """, (job_id,))

    job = cursor.fetchone()

    connection.close()

    return job


# =====================================
# 4. UPDATE JOB DETAILS
# =====================================

def update_job(

    job_id,
    job_title,
    company_name,
    description,
    required_skills,
    min_experience,
    location,
    employment_type,
    salary_range,
    indeed_url,
    posting_date,
    posting_status

):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""

        UPDATE jobs

        SET

            job_title = ?,
            company_name = ?,
            description = ?,
            required_skills = ?,
            min_experience = ?,
            location = ?,
            employment_type = ?,
            salary_range = ?,
            indeed_url = ?,
            posting_date = ?,
            posting_status = ?

        WHERE job_id = ?

    """, (

        job_title,
        company_name,
        description,
        required_skills,
        min_experience,
        location,
        employment_type,
        salary_range,
        indeed_url,
        posting_date,
        posting_status,
        job_id

    ))

    connection.commit()

    updated_rows = cursor.rowcount

    connection.close()

    return updated_rows


# =====================================
# 5. DELETE A JOB
# =====================================

def delete_job(job_id):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute("""

            DELETE FROM jobs
            WHERE job_id = ?

        """, (job_id,))

        connection.commit()

        deleted_rows = cursor.rowcount

        return deleted_rows

    except sqlite3.IntegrityError:

        connection.rollback()

        raise ValueError(
            "This job has applications linked to it. "
            "Close the vacancy instead of deleting it."
        )

    finally:

        connection.close()
