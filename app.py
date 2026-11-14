
import streamlit as st
import pandas as pd

from datetime import date, time

from database.db import init_db, migrate_call_logs

from modules.applicants import (
    import_applicants,
    get_all_applicants,
    update_application_status
)

from modules.screening import (
    init_screening_table,
    screen_all_applications,
    get_screening_results
)

from modules.jobs import (
    add_job,
    get_all_jobs,
    get_job_by_id,
    update_job,
    delete_job
)

from modules.calling import (
    make_candidate_call,
    get_call_history,
    update_call_outcome
)

from modules.interviews import (
    schedule_interview,
    get_all_interviews,
    update_interview
)


# =====================================
# 1. INITIAL CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Recruitment Management System",
    page_icon="👥",
    layout="wide"
)

# Make sure database tables exist

init_db()

migrate_call_logs()

# Make sure screening table exists

init_screening_table()


# =====================================
# 2. APPLICATION HEADER
# =====================================

st.title("Recruitment Workflow Automation System")

st.write(
    "Manage job postings, applicants, screening, "
    "calling and interview scheduling."
)


# =====================================
# 3. SIDEBAR NAVIGATION
# =====================================

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select a Module",
    [
        "Dashboard",
        "Job Management",
        "Applicant Management",
        "Candidate Screening",
        "Calling Management",
        "Interview Scheduling"
    ]
)


# =====================================
# 4. DASHBOARD
# =====================================

if page == "Dashboard":

    st.header("Recruitment Dashboard")

    jobs = get_all_jobs()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Jobs", len(jobs))

    col2.metric("Total Applicants", 0)

    col3.metric("Shortlisted", 0)

    col4.metric("Interviews Scheduled", 0)

    st.divider()

    st.info(
        "Welcome! Start by adding your job postings."
    )


# =====================================
# 5. JOB MANAGEMENT
# =====================================

elif page == "Job Management":

    st.header("Job Management")

    st.write(
        "Add, view, update and manage Indeed job postings."
    )

    # Create two tabs
    add_tab, manage_tab = st.tabs(
        ["Add New Job", "View / Edit Jobs"]
    )


    # ---------------------------------
    # TAB 1: ADD NEW JOB
    # ---------------------------------

    with add_tab:

        st.subheader("Add a New Vacancy")

        with st.form("add_job_form"):

            job_title = st.text_input(
                "Job Title *"
            )

            company_name = st.text_input(
                "Company Name"
            )

            description = st.text_area(
                "Job Description"
            )

            required_skills = st.text_input(
                "Required Skills",
                placeholder="Python, SQL, Django"
            )

            col1, col2 = st.columns(2)

            with col1:

                min_experience = st.number_input(
                    "Minimum Experience (Years)",
                    min_value=0.0,
                    max_value=50.0,
                    value=0.0,
                    step=0.5
                )

                location = st.text_input(
                    "Job Location"
                )

            with col2:

                employment_type = st.selectbox(
                    "Employment Type",
                    [
                        "Full-time",
                        "Part-time",
                        "Internship",
                        "Contract"
                    ]
                )

                salary_range = st.text_input(
                    "Salary Range",
                    placeholder="₹4-6 LPA"
                )

            indeed_url = st.text_input(
                "Indeed Job URL (Optional)"
            )

            posting_date = st.date_input(
                "Posting Date",
                value=date.today()
            )

            posting_status = st.selectbox(
                "Posting Status",
                [
                    "Draft",
                    "Published",
                    "Paused",
                    "Closed"
                ]
            )

            submitted = st.form_submit_button(
                "Save Job",
                use_container_width=True
            )


        if submitted:

            if not job_title.strip():

                st.error("Job title is required.")

            elif indeed_url.strip() and not (
                indeed_url.strip().startswith("https://")
                or indeed_url.strip().startswith("http://")
            ):

                st.error("Please enter a valid HTTP or HTTPS URL.")

            else:

                try:

                    new_job_id = add_job(
                        job_title.strip(),
                        company_name.strip(),
                        description.strip(),
                        required_skills.strip(),
                        min_experience,
                        location.strip(),
                        employment_type,
                        salary_range.strip(),
                        indeed_url.strip(),
                        posting_date.isoformat(),
                        posting_status
                    )

                    st.success(
                        f"Job saved successfully! Job ID: {new_job_id}"
                    )

                except Exception as error:

                    st.error(f"Unable to save job: {error}")


    # ---------------------------------
    # TAB 2: VIEW AND EDIT JOBS
    # ---------------------------------

    with manage_tab:

        st.subheader("Saved Job Vacancies")

        jobs = get_all_jobs()

        if not jobs:

            st.info(
                "No jobs found. Add your first vacancy."
            )

        else:

            # Convert database records into a DataFrame

            job_data = []

            for job in jobs:

                job_data.append({

                    "Job ID": job[0],
                    "Job Title": job[1],
                    "Company": job[2],
                    "Experience": job[5],
                    "Location": job[6],
                    "Employment Type": job[7],
                    "Salary": job[8],
                    "Indeed URL": job[9],
                    "Posting Date": job[10],
                    "Status": job[11]

                })

            df = pd.DataFrame(job_data)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )


            # ---------------------------------
            # SELECT JOB TO EDIT
            # ---------------------------------

            st.divider()

            st.subheader("Edit Existing Job")

            job_options = {
                f"{job[0]} - {job[1]}": job[0]
                for job in jobs
            }

            selected_job = st.selectbox(
                "Select a Job",
                list(job_options.keys())
            )

            selected_job_id = job_options[selected_job]

            selected_record = get_job_by_id(
                selected_job_id
            )


            if selected_record:

                job = selected_record

                with st.form("edit_job_form"):

                    edit_title = st.text_input(
                        "Job Title",
                        value=job[1] or ""
                    )

                    edit_company = st.text_input(
                        "Company Name",
                        value=job[2] or ""
                    )

                    edit_description = st.text_area(
                        "Job Description",
                        value=job[3] or ""
                    )

                    edit_skills = st.text_input(
                        "Required Skills",
                        value=job[4] or ""
                    )

                    edit_experience = st.number_input(
                        "Minimum Experience",
                        min_value=0.0,
                        max_value=50.0,
                        value=float(job[5] or 0),
                        step=0.5
                    )

                    edit_location = st.text_input(
                        "Location",
                        value=job[6] or ""
                    )

                    employment_options = [
                        "Full-time",
                        "Part-time",
                        "Internship",
                        "Contract"
                    ]

                    current_employment = (
                        job[7]
                        if job[7] in employment_options
                        else "Full-time"
                    )

                    edit_employment = st.selectbox(
                        "Employment Type",
                        employment_options,
                        index=employment_options.index(
                            current_employment
                        )
                    )

                    edit_salary = st.text_input(
                        "Salary Range",
                        value=job[8] or ""
                    )

                    edit_url = st.text_input(
                        "Indeed URL",
                        value=job[9] or ""
                    )

                    try:

                        current_date = (
                            date.fromisoformat(job[10])
                            if job[10]
                            else date.today()
                        )

                    except ValueError:

                        current_date = date.today()

                    edit_date = st.date_input(
                        "Posting Date",
                        value=current_date
                    )

                    status_options = [
                        "Draft",
                        "Published",
                        "Paused",
                        "Closed"
                    ]

                    current_status = (
                        job[11]
                        if job[11] in status_options
                        else "Draft"
                    )

                    edit_status = st.selectbox(
                        "Posting Status",
                        status_options,
                        index=status_options.index(
                            current_status
                        )
                    )

                    update_submitted = st.form_submit_button(
                        "Update Job",
                        use_container_width=True
                    )


                if update_submitted:

                    if not edit_title.strip():

                        st.error("Job title is required.")

                    elif edit_url.strip() and not (
                        edit_url.strip().startswith("https://")
                        or edit_url.strip().startswith("http://")
                    ):

                        st.error("Please enter a valid URL.")

                    else:

                        try:

                            update_job(
                                selected_job_id,
                                edit_title.strip(),
                                edit_company.strip(),
                                edit_description.strip(),
                                edit_skills.strip(),
                                edit_experience,
                                edit_location.strip(),
                                edit_employment,
                                edit_salary.strip(),
                                edit_url.strip(),
                                edit_date.isoformat(),
                                edit_status
                            )

                            st.success("Job updated successfully!")

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Unable to update job: {error}"
                            )


                # ---------------------------------
                # DELETE JOB
                # ---------------------------------

                st.divider()

                st.subheader("Delete Job")

                st.warning(
                    "Deleting a job is permanent. "
                    "Jobs with existing applications cannot be deleted."
                )

                confirm_delete = st.checkbox(
                    "I confirm that I want to delete this job.",
                    key=f"confirm_delete_{selected_job_id}"
                )

                if st.button(
                    "Delete Selected Job",
                    disabled=not confirm_delete
                ):

                    try:

                        delete_job(selected_job_id)

                        st.success("Job deleted successfully!")

                        st.rerun()

                    except ValueError as error:

                        st.error(str(error))



# =====================================
# 6. APPLICANT MANAGEMENT
# =====================================

elif page == "Applicant Management":

    st.header("Applicant Management")

    st.write(
        "Import, view and manage candidate applications."
    )

    # Create two tabs
    import_tab, view_tab = st.tabs(
        ["Import Applicants", "View Applicants"]
    )


    # ---------------------------------
    # TAB 1: IMPORT APPLICANTS
    # ---------------------------------

    with import_tab:

        st.subheader("Import Candidate Information")

        jobs = get_all_jobs()

        if not jobs:

            st.warning(
                "Please add at least one job before importing applicants."
            )

        else:

            job_options = {

                f"{job[0]} - {job[1]}": job[0]

                for job in jobs

            }

            selected_job = st.selectbox(
                "Select the Job",
                list(job_options.keys())
            )

            selected_job_id = job_options[selected_job]

            st.divider()

            uploaded_file = st.file_uploader(
                "Upload Applicant CSV File",
                type=["csv"]
            )

            if uploaded_file is not None:

                try:

                    # Read phone numbers as text
                    df = pd.read_csv(
                        uploaded_file,
                        dtype={"phone": "string"}
                    )

                    # Required column
                    required_columns = [
                        "candidate_name"
                    ]

                    missing_columns = [

                        column

                        for column in required_columns

                        if column not in df.columns

                    ]

                    if missing_columns:

                        st.error(
                            f"Missing required columns: {missing_columns}"
                        )

                    else:

                        # Add optional columns if missing
                        optional_columns = [

                            "email",
                            "phone",
                            "location",
                            "experience_years",
                            "skills",
                            "education",
                            "application_date"

                        ]

                        for column in optional_columns:

                            if column not in df.columns:

                                df[column] = None

                        # Replace empty cells with None
                        df = df.astype(object).where(
                            pd.notna(df),
                            None
                        )

                        # Default blank experience to zero
                        df["experience_years"] = (
                            df["experience_years"].fillna(0)
                        )

                        st.subheader("Applicant Preview")

                        st.dataframe(
                            df,
                            width="stretch",
                            hide_index=True
                        )

                        st.write(
                            f"Total records found: {len(df)}"
                        )

                        if st.button(
                            "Import Applicants",
                            width="stretch"
                        ):

                            try:

                                records = df.to_dict(
                                    orient="records"
                                )

                                result = import_applicants(
                                    records,
                                    selected_job_id
                                )

                                st.success(
                                    "Applicant import completed!"
                                )

                                # Display import summary

                                col1, col2 = st.columns(2)

                                col1.metric(
                                    "New Candidates",
                                    result["inserted_candidates"]
                                )

                                col2.metric(
                                    "Existing Candidates",
                                    result["existing_candidates"]
                                )

                                col3, col4 = st.columns(2)

                                col3.metric(
                                    "New Applications",
                                    result["new_applications"]
                                )

                                col4.metric(
                                    "Duplicate Applications",
                                    result["duplicate_applications"]
                                )

                                st.metric(
                                    "Invalid Records",
                                    result["invalid_records"]
                                )

                                st.info(
                                    "Refresh the View Applicants tab "
                                    "to see the imported records."
                                )

                            except Exception as error:

                                st.error(
                                    f"Import failed: {error}"
                                )

                except Exception as error:

                    st.error(
                        f"Unable to read CSV file: {error}"
                    )


    # ---------------------------------
    # TAB 2: VIEW APPLICANTS
    # ---------------------------------

    with view_tab:

        st.subheader("Applicant Database")

        applicants = get_all_applicants()

        if not applicants:

            st.info(
                "No applicant records found. "
                "Import your first CSV file."
            )

        else:

            applicant_data = []

            for applicant in applicants:

                applicant_data.append({

                    "Candidate ID": applicant[0],

                    "Candidate Name": applicant[1],

                    "Email": applicant[2],

                    "Phone": applicant[3],

                    "Location": applicant[4],

                    "Experience": applicant[5],

                    "Skills": applicant[6],

                    "Education": applicant[7],

                    "Applied For": applicant[8],

                    "Application ID": applicant[9],

                    "Application Date": applicant[10],

                    "Category": applicant[11],

                    "Status": applicant[12]

                })

            applicant_df = pd.DataFrame(
                applicant_data
            )

            # Summary metrics

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Applications",
                len(applicant_df)
            )

            col2.metric(
                "Unique Candidates",
                applicant_df["Candidate ID"].nunique()
            )

            col3.metric(
                "Shortlisted",
                (
                    applicant_df["Status"] == "Shortlisted"
                ).sum()
            )

            st.divider()

            # Display applicant records

            st.dataframe(
                applicant_df,
                width="stretch",
                hide_index=True
            )

            # ---------------------------------
            # UPDATE APPLICATION STATUS
            # ---------------------------------

            st.divider()

            st.subheader("Update Application Status")

            application_options = {

                f"{row['Application ID']} - "
                f"{row['Candidate Name']} - "
                f"{row['Applied For']}": row["Application ID"]

                for _, row in applicant_df.iterrows()

            }

            selected_application = st.selectbox(
                "Select Application",
                list(application_options.keys())
            )

            selected_application_id = (
                application_options[selected_application]
            )

            new_status = st.selectbox(

                "Select New Status",

                [
                    "Pending",
                    "Shortlisted",
                    "On Hold",
                    "Not Shortlisted"
                ]

            )

            if st.button("Update Application Status"):

                try:

                    update_application_status(
                        selected_application_id,
                        new_status
                    )

                    st.success(
                        "Application status updated successfully!"
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Unable to update status: {error}"
                    )




# =====================================
# 7. CANDIDATE SCREENING
# =====================================

elif page == "Candidate Screening":

    st.header("Candidate Screening")

    st.write(
        "Evaluate candidates based on their skills "
        "and professional experience."
    )

    st.divider()

    # ---------------------------------
    # RUN SCREENING
    # ---------------------------------

    st.subheader("Screen Applicants")

    st.info(
        "The screening engine compares candidate skills "
        "and experience against job requirements."
    )

    if st.button(
        "Run Candidate Screening",
        width="stretch"
    ):

        try:

            screened_count = screen_all_applications()

            st.success(
                f"Screening completed! "
                f"{screened_count} applications evaluated."
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Screening failed: {error}"
            )


    st.divider()

    # ---------------------------------
    # DISPLAY SCREENING RESULTS
    # ---------------------------------

    st.subheader("Screening Results")

    results = get_screening_results()

    if not results:

        st.warning(
            "No screening results available. "
            "Please import applicants and run screening."
        )

    else:

        # Convert database results into a DataFrame

        screening_data = []

        for result in results:

            screening_data.append({

                "Screening ID": result[0],

                "Candidate Name": result[1],

                "Job Title": result[2],

                "Skill Score (%)": result[3],

                "Experience Score (%)": result[4],

                "Matching Score (%)": result[5],

                "Matched Skills": result[6],

                "Missing Skills": result[7],

                "Category": result[8],

                "Recommendation": result[9],

                "Screened At": result[10]

            })

        screening_df = pd.DataFrame(
            screening_data
        )

        # ---------------------------------
        # SUMMARY METRICS
        # ---------------------------------

        total_screened = len(screening_df)

        relevant_count = (

            screening_df["Category"] == "Relevant"

        ).sum()

        partial_count = (

            screening_df["Category"] == "Partially Relevant"

        ).sum()

        not_relevant_count = (

            screening_df["Category"] == "Not Relevant"

        ).sum()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Screened",
            total_screened
        )

        col2.metric(
            "Relevant",
            relevant_count
        )

        col3.metric(
            "Partially Relevant",
            partial_count
        )

        col4.metric(
            "Not Relevant",
            not_relevant_count
        )

        st.divider()

        # ---------------------------------
        # FILTER SCREENING RESULTS
        # ---------------------------------

        st.subheader("Filter Candidates")

        selected_category = st.selectbox(

            "Select Candidate Category",

            [
                "All",
                "Relevant",
                "Partially Relevant",
                "Not Relevant",
                "Insufficient Job Criteria"
            ]

        )

        if selected_category != "All":

            filtered_df = screening_df[

                screening_df["Category"] == selected_category

            ]

        else:

            filtered_df = screening_df

        # ---------------------------------
        # DISPLAY RESULTS TABLE
        # ---------------------------------

        st.dataframe(

            filtered_df,

            width="stretch",

            hide_index=True

        )

        # ---------------------------------
        # DOWNLOAD SCREENING REPORT
        # ---------------------------------

        csv_data = filtered_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(

            label="Download Screening Report",

            data=csv_data,

            file_name="candidate_screening_report.csv",

            mime="text/csv"

        )



# =====================================
# 8. CALLING MANAGEMENT
# =====================================

elif page == "Calling Management":

    st.header("Calling Management")
    st.write(
        "Contact applicants, record call outcomes and manage follow-ups."
    )

    make_call_tab, history_tab = st.tabs(
        ["Make a Call", "Call History"]
    )

    # ---------------------------------
    # TAB 1: MAKE A CALL
    # ---------------------------------

    with make_call_tab:

        st.subheader("Call an Applicant")

        applicants = get_all_applicants()

        if not applicants:
            st.warning(
                "No applications found. Import applicants first."
            )
        else:
            application_options = {
                (
                    f"Application {row[9]} - "
                    f"{row[1]} - {row[8]} - {row[3]}"
                ): row[9]
                for row in applicants
            }

            selected_application = st.selectbox(
                "Select Applicant",
                list(application_options.keys()),
                key="calling_selected_application"
            )

            selected_application_id = application_options[
                selected_application
            ]

            consent_confirmed = st.checkbox(
                "I confirm that this candidate has consented "
                "to receive a recruitment call.",
                key="calling_consent_confirmed"
            )

            st.warning(
                "Clicking the button below initiates a real phone call."
            )

            if st.button(
                "Initiate Twilio Call",
                disabled=not consent_confirmed,
                use_container_width=True,
                key="initiate_twilio_call"
            ):
                try:
                    result = make_candidate_call(
                        selected_application_id,
                        consent_confirmed=True
                    )

                    st.success("Call initiated successfully!")
                    st.write("Candidate:", result["candidate_name"])
                    st.write("Phone:", result["phone_number"])
                    st.write("Twilio Call SID:", result["twilio_call_sid"])
                    st.write("Call Status:", result["call_status"])

                except Exception as error:
                    st.error(f"Unable to initiate call: {error}")

    # ---------------------------------
    # TAB 2: CALL HISTORY
    # ---------------------------------

    with history_tab:

        st.subheader("Previous Calls")

        history = get_call_history()

        if not history:
            st.info("No call records found.")
        else:
            call_columns = [
                "Call ID",
                "Candidate",
                "Job Title",
                "Phone",
                "Call Status",
                "Call Outcome",
                "Duration (Seconds)",
                "Call Time",
                "Follow-up Date",
                "Notes"
            ]

            history_df = pd.DataFrame(
                history,
                columns=call_columns
            )

            st.dataframe(
                history_df,
                use_container_width=True,
                hide_index=True
            )

            st.divider()
            st.subheader("Update Call Outcome")

            call_options = {
                f"Call {row[0]} - {row[1]} - {row[2]}": row[0]
                for row in history
            }

            selected_call = st.selectbox(
                "Select a Call",
                list(call_options.keys()),
                key="calling_selected_call"
            )

            selected_call_id = call_options[selected_call]

            with st.form("update_call_form"):

                call_outcome = st.selectbox(
                    "Call Outcome",
                    [
                        "Connected",
                        "No Answer",
                        "Busy",
                        "Call Back Required",
                        "Rejected"
                    ]
                )

                notes = st.text_area(
                    "Recruiter Notes",
                    placeholder="Enter details about the conversation..."
                )

                schedule_follow_up = st.checkbox(
                    "Schedule a follow-up"
                )

                follow_up_date = None

                if schedule_follow_up:
                    follow_up_date = st.date_input(
                        "Follow-up Date",
                        min_value=date.today()
                    )

                update_submitted = st.form_submit_button(
                    "Save Call Outcome",
                    use_container_width=True
                )

            if update_submitted:
                try:
                    result = update_call_outcome(
                        selected_call_id,
                        call_outcome,
                        notes,
                        (
                            follow_up_date.isoformat()
                            if follow_up_date
                            else None
                        )
                    )

                    if result:
                        st.success("Call outcome updated successfully!")
                        st.rerun()
                    else:
                        st.warning("No matching call record found.")

                except Exception as error:
                    st.error(f"Unable to update call outcome: {error}")


# =====================================
# 9. INTERVIEW SCHEDULING
# =====================================


elif page == "Interview Scheduling":

    st.header("Interview Scheduling")

    st.write(
        "Schedule interviews for shortlisted candidates "
        "and manage interview details."
    )

    schedule_tab, manage_tab = st.tabs(
        ["Schedule an Interview", "View / Manage Interviews"]
    )

    # SCHEDULE INTERVIEW

    with schedule_tab:

        st.subheader("Create Interview Schedule")

        applicants = get_all_applicants()

        shortlisted = [
            row for row in applicants
            if str(row[12]).strip().lower() == "shortlisted"
        ]

        if not shortlisted:

            st.warning(
                "No shortlisted applicants found. "
                "Shortlist an applicant first."
            )

        else:

            application_options = {
                f"{row[1]} - {row[8]} - Application {row[9]}": row[9]
                for row in shortlisted
            }

            with st.form("schedule_interview_form"):

                selected = st.selectbox(
                    "Select Shortlisted Candidate",
                    list(application_options.keys())
                )

                interview_date = st.date_input(
                    "Interview Date",
                    min_value=date.today()
                )

                interview_time = st.time_input(
                    "Interview Time",
                    value=time(10, 0)
                )

                interview_mode = st.selectbox(
                    "Interview Mode",
                    ["Online", "Offline", "Phone"]
                )

                venue_or_link = st.text_input(
                    "Meeting Link / Venue / Phone Details"
                )

                interviewer_name = st.text_input(
                    "Interviewer Name"
                )

                confirmation_status = st.selectbox(
                    "Confirmation Status",
                    [
                        "Confirmation Pending",
                        "Confirmed",
                        "Rescheduled",
                        "Cancelled"
                    ]
                )

                submitted = st.form_submit_button(
                    "Schedule Interview"
                )

            if submitted:

                try:

                    interview_id = schedule_interview(
                        application_options[selected],
                        interview_date.isoformat(),
                        interview_time.strftime("%H:%M"),
                        interview_mode,
                        venue_or_link.strip(),
                        interviewer_name.strip(),
                        confirmation_status
                    )

                    st.success(
                        f"Interview scheduled! ID: {interview_id}"
                    )

                except Exception as error:

                    st.error(str(error))

    # VIEW AND MANAGE INTERVIEWS

    with manage_tab:

        st.subheader("Scheduled Interviews")

        interviews = get_all_interviews()

        if not interviews:

            st.info("No interviews scheduled yet.")

        else:

            columns = [
                "Interview ID",
                "Candidate",
                "Job Title",
                "Application ID",
                "Interview Date",
                "Interview Time",
                "Mode",
                "Venue / Link",
                "Interviewer",
                "Confirmation Status"
            ]

            interview_df = pd.DataFrame(
                interviews,
                columns=columns
            )

            st.dataframe(
                interview_df,
                use_container_width=True,
                hide_index=True
            )

            st.divider()

            st.subheader("Update Interview")

            interview_options = {
                f"Interview {row[0]} - {row[1]} - {row[4]}": row[0]
                for row in interviews
            }

            selected_interview = st.selectbox(
                "Select Interview",
                list(interview_options.keys())
            )

            selected_id = interview_options[selected_interview]

            record = next(
                row for row in interviews
                if row[0] == selected_id
            )

            with st.form("update_interview_form"):

                new_date = st.date_input(
                    "Interview Date",
                    value=date.fromisoformat(record[4])
                )

                try:
                    current_time = time.fromisoformat(record[5])
                except (ValueError, TypeError):
                    current_time = time(10, 0)

                new_time = st.time_input(
                    "Interview Time",
                    value=current_time
                )

                new_mode = st.selectbox(
                    "Interview Mode",
                    ["Online", "Offline", "Phone"],
                    index=["Online", "Offline", "Phone"].index(record[6])
                    if record[6] in ["Online", "Offline", "Phone"]
                    else 0
                )

                new_venue = st.text_input(
                    "Meeting Link / Venue / Phone Details",
                    value=record[7] or ""
                )

                new_interviewer = st.text_input(
                    "Interviewer Name",
                    value=record[8] or ""
                )

                statuses = [
                    "Confirmation Pending",
                    "Confirmed",
                    "Rescheduled",
                    "Cancelled"
                ]

                new_status = st.selectbox(
                    "Confirmation Status",
                    statuses,
                    index=statuses.index(record[9])
                    if record[9] in statuses
                    else 0
                )

                update_submitted = st.form_submit_button(
                    "Save Interview Changes"
                )

            if update_submitted:

                try:

                    update_interview(
                        selected_id,
                        new_date.isoformat(),
                        new_time.strftime("%H:%M"),
                        new_mode,
                        new_venue.strip(),
                        new_interviewer.strip(),
                        new_status
                    )

                    st.success("Interview updated successfully!")
                    st.rerun()

                except Exception as error:

                    st.error(str(error))

