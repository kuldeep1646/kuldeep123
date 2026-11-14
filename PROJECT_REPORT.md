# Project Report: Recruitment Workflow Automation System

## 1. Introduction

Recruitment involves multiple connected activities, including managing job openings, collecting applications, reviewing candidate suitability, contacting applicants, and arranging interviews. Handling these activities manually across separate tools can make the process difficult to track. This project demonstrates a centralized application for managing a basic recruitment workflow.

## 2. Problem Statement

Recruitment teams need a structured way to maintain job and applicant information and coordinate screening, candidate contact, and interview scheduling. A fragmented process can lead to repeated data entry, inconsistent records, and missed communication. The project addresses this by bringing these activities into one Streamlit application backed by a relational SQLite database.

## 3. Objectives

- Build a centralized interface for basic recruitment activities.
- Maintain job, applicant, application, screening, call, and interview records.
- Provide rule-based screening using skills and experience.
- Demonstrate outbound calling through Twilio with an explicit consent check.
- Automate interview confirmation, rescheduling, and cancellation emails.
- Deploy the application as a portfolio demonstration.

## 4. Scope

The system covers job management, applicant import and management, candidate screening, calling management, interview scheduling, and interview email notifications. The deployed version is intended for demonstration with fictional data. It is not configured as a production recruitment platform.

## 5. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application and business logic |
| Streamlit | Web user interface |
| SQLite | Relational data storage for the demo |
| pandas | CSV and tabular data handling |
| Twilio Python SDK | Outbound phone calls |
| Gmail SMTP | Interview email notifications |
| python-dotenv | Local environment configuration |
| GitHub | Source-code hosting and version control |
| Streamlit Community Cloud | Application hosting |

## 6. System Architecture

The system uses a layered, modular architecture. The Streamlit interface in `app.py` receives user input and calls functions in the relevant module. The modules implement recruitment operations and use the database connection functions in `database/db.py` to read or update SQLite records. External communication is handled by the Twilio SDK for calls and Python's SMTP/email libraries for interview notifications. Configuration values are read from a local `.env` file during local development or Streamlit Cloud Secrets after deployment.

```text
User
  |
  v
Streamlit interface (app.py)
  |
  +--> Job Management module --------+
  +--> Applicant Management module ---+
  +--> Screening module --------------+--> SQLite database
  +--> Calling module -----------------+       |
  +--> Interview module ---------------+       +--> Jobs
  +--> Email notification module ------+       +--> Applicants / Applications
          |                                     +--> Screening / Call logs
          +--> Gmail SMTP                      +--> Interviews
          +--> Twilio API
```

## 7. Module Description

### 7.1 Job Management
Supports adding, viewing, updating, and deleting job postings. Job information includes role details, required skills, experience, location, employment type, and posting information.

### 7.2 Applicant Management
Supports importing applicant information from CSV, maintaining candidate and application records, avoiding duplicate candidate/job applications, and updating application status.

### 7.3 Candidate Screening
Applies a rule-based matching approach using required skills and experience. The existing implementation uses a weighted score, with 70% assigned to skills and 30% to experience.

### 7.4 Calling Management
Uses the Twilio Python SDK to initiate an outbound call after an explicit consent confirmation. Call details and outcomes are stored in the database. Actual call availability depends on Twilio account configuration and trial restrictions.

### 7.5 Interview Scheduling
Allows interviews to be scheduled and existing interview details or confirmation status to be updated.

### 7.6 Email Notifications
Uses Gmail SMTP to send interview confirmation, rescheduling, and cancellation messages. The email content includes relevant candidate and interview information.

## 8. Database Design

The SQLite database is created by the application at runtime. Core tables include `jobs`, `applicants`, `applications`, `screening`, `call_logs`, and `interviews`. The screening module also creates its screening-results table. Foreign-key relationships connect applications to candidates and jobs, and connect screening, call, and interview records to applications.

## 9. Workflow

1. The recruiter creates a job record.
2. Applicant details are imported from a CSV file.
3. Candidate applications are associated with job records.
4. Screening evaluates skills and experience and provides a matching recommendation.
5. A shortlisted candidate may be contacted through Twilio after consent is confirmed.
6. The recruiter schedules an interview.
7. The system sends a confirmation email. If the interview is updated, it sends a rescheduling email; if cancelled, it sends a cancellation email.
8. The recruiter can review interview and call records in the application.

## 10. Testing Summary

During development, the individual modules were exercised through the Streamlit interface and focused tests. The user confirmed successful standalone Gmail SMTP delivery and successful interview confirmation email delivery with correct details. Rescheduling and cancellation were included in the final workflow testing. Before public release, the deployed instance must be tested again because cloud secrets, hosting behavior, and the cloud database are separate from the local environment.

## 11. Deployment

The project is prepared for deployment through GitHub and Streamlit Community Cloud. Dependencies are listed in `requirements.txt`. Secret credentials are excluded from source control and are configured through Streamlit Cloud Secrets. A fresh SQLite database is created at runtime rather than publishing the local development database.

## 12. Limitations

- SQLite files in the Streamlit app container are not guaranteed to persist across restarts or redeployments.
- The current project is not designed for concurrent multi-user production workloads.
- Authentication and role-based access control are not included.
- Email delivery logging and retry management are not implemented.
- Twilio calls depend on account permissions, verified numbers, and candidate consent.
- The screening process is rule-based and should not be treated as a complete hiring decision system.

## 13. Future Scope

- Use managed PostgreSQL for durable data storage.
- Add authentication and recruiter/admin roles.
- Add audit trails and configurable data retention.
- Add email delivery logs and retry mechanisms.
- Integrate Twilio status callbacks.
- Improve screening with configurable criteria and explainable scoring.
- Add automated unit and integration testing.

## 14. Conclusion

The Recruitment Workflow Automation System demonstrates how common recruitment activities can be organized in one modular web application. It combines job and applicant management, rule-based screening, candidate calling, interview scheduling, and email notifications. The deployment-ready version is intended as a portfolio demonstration using fictional data, with clear limitations documented for any future production expansion.
