
import re

from database.db import get_connection


# ==========================================
# 1. CREATE SCREENING RESULTS TABLE
# ==========================================

def init_screening_table():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS screening_results (

            screening_id INTEGER PRIMARY KEY AUTOINCREMENT,

            application_id INTEGER NOT NULL UNIQUE,

            candidate_id INTEGER NOT NULL,

            job_id INTEGER NOT NULL,

            skill_score REAL,

            experience_score REAL,

            matching_score REAL,

            matched_skills TEXT,

            missing_skills TEXT,

            category TEXT,

            recommendation TEXT,

            screened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

    """)

    connection.commit()

    connection.close()


# ==========================================
# 2. CONVERT SKILLS INTO A LIST
# ==========================================

def extract_skills(skills_text):

    if not skills_text:

        return []

    skills = re.split(
        r"[,;\n]+",
        str(skills_text)
    )

    return [

        skill.strip()

        for skill in skills

        if skill.strip()

    ]


# ==========================================
# 3. CHECK WHETHER A SKILL MATCHES
# ==========================================

def skill_exists(skill, candidate_skills):

    pattern = (
        r"(?<!\w)"
        + re.escape(skill.lower())
        + r"(?!\w)"
    )

    return re.search(
        pattern,
        candidate_skills.lower()
    ) is not None


# ==========================================
# 4. CALCULATE SKILL MATCHING SCORE
# ==========================================

def calculate_skill_score(
    required_skills,
    candidate_skills
):

    matched_skills = []

    missing_skills = []

    for skill in required_skills:

        if skill_exists(skill, candidate_skills):

            matched_skills.append(skill)

        else:

            missing_skills.append(skill)

    if not required_skills:

        return 0, [], []

    score = (
        len(matched_skills)
        / len(required_skills)
    ) * 100

    return score, matched_skills, missing_skills


# ==========================================
# 5. CALCULATE EXPERIENCE SCORE
# ==========================================

def calculate_experience_score(
    candidate_experience,
    required_experience
):

    candidate_experience = float(
        candidate_experience or 0
    )

    required_experience = float(
        required_experience or 0
    )

    if candidate_experience < 0 or required_experience < 0:

        raise ValueError(
            "Experience cannot be negative."
        )

    if required_experience == 0:

        return 100.0

    score = (
        candidate_experience
        / required_experience
    ) * 100

    return min(score, 100.0)


# ==========================================
# 6. CALCULATE FINAL MATCHING SCORE
# ==========================================

def calculate_matching_score(
    skill_score,
    experience_score
):

    final_score = (

        (skill_score * 0.70)

        +

        (experience_score * 0.30)

    )

    return round(final_score, 2)


# ==========================================
# 7. CATEGORISE CANDIDATE
# ==========================================

def categorise_candidate(matching_score):

    if matching_score >= 70:

        return "Relevant"

    elif matching_score >= 40:

        return "Partially Relevant"

    else:

        return "Not Relevant"


# ==========================================
# 8. GENERATE RECOMMENDATION
# ==========================================

def generate_recommendation(
    matching_score,
    category
):

    if category == "Insufficient Job Criteria":

        return "Add job requirements"

    if matching_score >= 80:

        return "Strong Potential Match"

    elif matching_score >= 60:

        return "Manual Review Recommended"

    else:

        return "Low Match - Review Manually"


# ==========================================
# 9. SCREEN ALL APPLICATIONS
# ==========================================

def screen_all_applications():

    connection = get_connection()

    cursor = connection.cursor()

    screened_count = 0

    try:

        # Retrieve candidate and job information

        cursor.execute("""

            SELECT

                applications.application_id,

                applicants.candidate_id,

                jobs.job_id,

                applicants.candidate_name,

                applicants.skills,

                applicants.experience_years,

                jobs.job_title,

                jobs.required_skills,

                jobs.min_experience

            FROM applications

            JOIN applicants

                ON applications.candidate_id =
                   applicants.candidate_id

            JOIN jobs

                ON applications.job_id =
                   jobs.job_id

            ORDER BY applications.application_id

        """)

        applications = cursor.fetchall()

        # Process each application

        for application in applications:

            application_id = application[0]

            candidate_id = application[1]

            job_id = application[2]

            candidate_skills = application[4] or ""

            candidate_experience = application[5] or 0

            required_skills_text = application[7] or ""

            required_experience = application[8] or 0

            # Extract required skills

            required_skills = extract_skills(
                required_skills_text
            )

            # Check whether job requirements exist

            if not required_skills:

                skill_score = 0

                experience_score = 0

                matching_score = 0

                matched_skills = []

                missing_skills = []

                category = "Insufficient Job Criteria"

            else:

                # Calculate skill score

                (
                    skill_score,
                    matched_skills,
                    missing_skills

                ) = calculate_skill_score(

                    required_skills,
                    candidate_skills

                )

                # Calculate experience score

                experience_score = calculate_experience_score(

                    candidate_experience,
                    required_experience

                )

                # Calculate final score

                matching_score = calculate_matching_score(

                    skill_score,
                    experience_score

                )

                # Assign candidate category

                category = categorise_candidate(
                    matching_score
                )

            # Generate recommendation

            recommendation = generate_recommendation(

                matching_score,
                category

            )

            # Save screening result

            cursor.execute("""

                INSERT INTO screening_results (

                    application_id,

                    candidate_id,

                    job_id,

                    skill_score,

                    experience_score,

                    matching_score,

                    matched_skills,

                    missing_skills,

                    category,

                    recommendation

                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(application_id)

                DO UPDATE SET

                    candidate_id = excluded.candidate_id,

                    job_id = excluded.job_id,

                    skill_score = excluded.skill_score,

                    experience_score = excluded.experience_score,

                    matching_score = excluded.matching_score,

                    matched_skills = excluded.matched_skills,

                    missing_skills = excluded.missing_skills,

                    category = excluded.category,

                    recommendation = excluded.recommendation,

                    screened_at = CURRENT_TIMESTAMP

            """, (

                application_id,

                candidate_id,

                job_id,

                round(skill_score, 2),

                round(experience_score, 2),

                matching_score,

                ", ".join(matched_skills),

                ", ".join(missing_skills),

                category,

                recommendation

            ))

            screened_count += 1

        connection.commit()

        return screened_count

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


# ==========================================
# 10. RETRIEVE SCREENING RESULTS
# ==========================================

def get_screening_results():

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute("""

            SELECT

                screening_results.screening_id,

                applicants.candidate_name,

                jobs.job_title,

                screening_results.skill_score,

                screening_results.experience_score,

                screening_results.matching_score,

                screening_results.matched_skills,

                screening_results.missing_skills,

                screening_results.category,

                screening_results.recommendation,

                screening_results.screened_at

            FROM screening_results

            JOIN applicants

                ON screening_results.candidate_id =
                   applicants.candidate_id

            JOIN jobs

                ON screening_results.job_id =
                   jobs.job_id

            ORDER BY screening_results.matching_score DESC

        """)

        results = cursor.fetchall()

        return results

    finally:

        connection.close()
