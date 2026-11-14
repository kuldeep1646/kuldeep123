
from database.db import get_connection


# =====================================
# 1. CLEAN TEXT DATA
# =====================================

def clean_text(value):

    if value is None:
        return ""

    return str(value).strip()


# =====================================
# 2. FIND AN EXISTING CANDIDATE
# =====================================

def find_existing_candidate(cursor, email, phone):

    candidate = None

    # First search using email
    if email:

        cursor.execute("""

            SELECT candidate_id

            FROM applicants

            WHERE LOWER(email) = LOWER(?)

            LIMIT 1

        """, (email,))

        candidate = cursor.fetchone()

    # If not found, search using phone
    if candidate is None and phone:

        cursor.execute("""

            SELECT candidate_id

            FROM applicants

            WHERE phone = ?

            LIMIT 1

        """, (phone,))

        candidate = cursor.fetchone()

    if candidate:

        return candidate[0]

    return None


# =====================================
# 3. IMPORT APPLICANTS
# =====================================

def import_applicants(records, job_id):

    connection = get_connection()

    cursor = connection.cursor()

    inserted_candidates = 0

    existing_candidates = 0

    new_applications = 0

    duplicate_applications = 0

    invalid_records = 0

    try:

        # Process each applicant
        for record in records:

            # ---------------------------------
            # READ CANDIDATE INFORMATION
            # ---------------------------------

            name = clean_text(
                record.get("candidate_name")
            )

            email = clean_text(
                record.get("email")
            ).lower()

            phone = clean_text(
                record.get("phone")
            )

            location = clean_text(
                record.get("location")
            )

            skills = clean_text(
                record.get("skills")
            )

            education = clean_text(
                record.get("education")
            )

            # ---------------------------------
            # VALIDATE MANDATORY INFORMATION
            # ---------------------------------

            if not name or not (email or phone):

                invalid_records += 1

                continue

            # ---------------------------------
            # VALIDATE EXPERIENCE
            # ---------------------------------

            raw_experience = record.get(
                "experience_years"
            )

            try:

                if raw_experience is None or raw_experience == "":

                    experience = 0

                else:

                    experience = float(raw_experience)

                if experience < 0:

                    invalid_records += 1

                    continue

            except (ValueError, TypeError):

                invalid_records += 1

                continue

            # ---------------------------------
            # READ APPLICATION DATE
            # ---------------------------------

            application_date = clean_text(
                record.get("application_date")
            )

            # ---------------------------------
            # CHECK EXISTING CANDIDATE
            # ---------------------------------

            candidate_id = find_existing_candidate(
                cursor,
                email,
                phone
            )

            if candidate_id is None:

                # Insert a new candidate

                cursor.execute("""

                    INSERT INTO applicants (

                        candidate_name,
                        email,
                        phone,
                        location,
                        experience_years,
                        skills,
                        education

                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?)

                """, (

                    name,
                    email,
                    phone,
                    location,
                    experience,
                    skills,
                    education

                ))

                candidate_id = cursor.lastrowid

                inserted_candidates += 1

            else:

                existing_candidates += 1

            # ---------------------------------
            # CHECK DUPLICATE APPLICATION
            # ---------------------------------

            cursor.execute("""

                SELECT application_id

                FROM applications

                WHERE candidate_id = ?

                AND job_id = ?

            """, (

                candidate_id,
                job_id

            ))

            existing_application = cursor.fetchone()

            if existing_application:

                duplicate_applications += 1

                continue

            # ---------------------------------
            # INSERT NEW APPLICATION
            # ---------------------------------

            cursor.execute("""

                INSERT INTO applications (

                    candidate_id,
                    job_id,
                    application_date,
                    category,
                    status,
                    source

                )

                VALUES (?, ?, ?, ?, ?, ?)

            """, (

                candidate_id,
                job_id,
                application_date,
                "Unreviewed",
                "Pending",
                "Approved CSV Import"

            ))

            new_applications += 1

        # Save all database changes

        connection.commit()

    except Exception:

        # Undo database changes if an error occurs

        connection.rollback()

        raise

    finally:

        # Always close the database connection

        connection.close()

    # ---------------------------------
    # RETURN IMPORT SUMMARY
    # ---------------------------------

    return {

        "inserted_candidates": inserted_candidates,

        "existing_candidates": existing_candidates,

        "new_applications": new_applications,

        "duplicate_applications": duplicate_applications,

        "invalid_records": invalid_records

    }


# =====================================
# 4. GET ALL APPLICANTS
# =====================================

def get_all_applicants():

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute("""

            SELECT

                applicants.candidate_id,

                applicants.candidate_name,

                applicants.email,

                applicants.phone,

                applicants.location,

                applicants.experience_years,

                applicants.skills,

                applicants.education,

                jobs.job_title,

                applications.application_id,

                applications.application_date,

                applications.category,

                applications.status

            FROM applications

            JOIN applicants

                ON applications.candidate_id =
                   applicants.candidate_id

            JOIN jobs

                ON applications.job_id =
                   jobs.job_id

            ORDER BY applications.application_id DESC

        """)

        applicants = cursor.fetchall()

        return applicants

    finally:

        connection.close()


# =====================================
# 5. UPDATE APPLICATION STATUS
# =====================================

def update_application_status(application_id, status):

    allowed_statuses = [

        "Pending",

        "Shortlisted",

        "On Hold",

        "Not Shortlisted"

    ]

    # Validate application status

    if status not in allowed_statuses:

        raise ValueError(
            "Invalid application status."
        )

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute("""

            UPDATE applications

            SET status = ?

            WHERE application_id = ?

        """, (

            status,
            application_id

        ))

        updated_rows = cursor.rowcount

        connection.commit()

        return updated_rows

    finally:

        connection.close()
