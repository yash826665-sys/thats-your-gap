"""
Synthetic test data. None of this describes a real person — it exists
purely to exercise the pipeline end to end without touching private data.
"""

SYNTHETIC_LINKEDIN_TEXT = """Alex Rivera
Aspiring Data Analyst | SQL, Power BI, Python, Machine Learning
Austin, Texas Area

Summary
Recent graduate passionate about turning data into decisions. Comfortable with SQL
and Power BI from coursework and a summer internship.

Experience
Data Analyst Intern
Northwind Retail
Jun 2023 - Aug 2023
Wrote SQL queries to pull weekly sales data for the merchandising team.
Built two Power BI dashboards used in the weekly ops meeting.

Teaching Assistant
State University
Jan 2022 - May 2023
Held office hours for an intro statistics course.

Education
State University
B.S. in Statistics, 2019 - 2023

Top Skills
SQL, Power BI, Python, Machine Learning, Excel, Tableau

Licenses & Certifications
Google Data Analytics Certificate
Google

Honors & Awards
Dean's List, 2021
"""

SYNTHETIC_RESUME_TEXT = """ALEX RIVERA
Austin, TX | alex.rivera@example.com

SUMMARY
Detail-oriented recent graduate seeking a Data Analyst role.

EXPERIENCE
Data Analyst Intern — Northwind Retail
June 2023 - August 2023
- Queried sales data using SQL to support the merchandising team
- Built Power BI dashboards adopted in weekly ops meetings, reducing manual
  reporting time by roughly 3 hours per week

Teaching Assistant — State University
January 2022 - May 2023
- Supported an introductory statistics course for 40 students

PROJECTS
Retail Sales Forecasting
Built a forecasting model in Python to predict weekly store sales using
historical data. Presented findings to a class of 30.

EDUCATION
B.S. in Statistics, State University, 2019 - 2023

SKILLS
SQL, Python, Power BI, Excel, Statistics

CERTIFICATIONS
Google Data Analytics Certificate, Google
"""

# A well-formed, schema-valid mock LLM response used to test the
# validation and API layers without making a real network call.
SYNTHETIC_LLM_RESPONSE = {
    "career_signal": 74,
    "dimensions": {
        "positioning": 78,
        "evidence": 66,
        "clarity": 85,
        "impact": 60,
        "role_alignment": 80,
    },
    "strongest_signal": {
        "insight": "Your strongest signal is hands-on SQL and Power BI experience from a real internship, corroborated across both documents.",
        "evidence": [
            "LinkedIn experience: 'Wrote SQL queries... Built two Power BI dashboards'",
            "Resume experience: 'Queried sales data using SQL... Built Power BI dashboards adopted in weekly ops meetings'",
        ],
    },
    "biggest_blind_spot": {
        "insight": "Machine Learning is listed as a skill but only one project provides limited supporting evidence.",
        "evidence": ["Skills list includes 'Machine Learning'", "Only one project (forecasting) touches on it, described briefly"],
    },
    "positioning_diagnosis": {
        "insight": "Your headline claims breadth across SQL, Power BI, Python, and Machine Learning, but demonstrated evidence is concentrated in SQL and BI reporting.",
        "evidence": ["Headline: 'SQL, Power BI, Python, Machine Learning'", "Experience entries focus on SQL/Power BI reporting tasks"],
    },
    "evidence_gaps": [
        {
            "claim": "Machine Learning (skill)",
            "gap": "No project or experience entry demonstrates applied machine learning work beyond a single forecasting project.",
            "evidence": ["Skills section lists Machine Learning", "Projects section shows one forecasting project without ML-specific detail"],
        }
    ],
    "impact_analysis": {
        "insight": "One resume bullet quantifies impact (reduced reporting time by ~3 hours/week); most other bullets describe tasks without measurable outcomes.",
        "evidence": ["Resume bullet: 'reducing manual reporting time by roughly 3 hours per week'", "Other bullets describe activities without numbers"],
    },
    "consistency_checks": [
        {
            "topic": "Internship dates",
            "linkedin_version": "Jun 2023 - Aug 2023",
            "resume_version": "June 2023 - August 2023",
            "note": "Dates appear consistent across both documents.",
        }
    ],
    "target_role_match": None,
    "next_three_moves": [
        {
            "recommendation": "Add a measurable outcome to the Power BI dashboard bullet on LinkedIn, mirroring the resume's time-saved detail.",
            "reason": "The resume already quantifies this achievement; LinkedIn currently doesn't, so LinkedIn under-sells your best evidence of impact.",
        },
        {
            "recommendation": "Expand the forecasting project description with the specific technique used and a measurable result.",
            "reason": "This is your only evidence for the Machine Learning skill you list, so it currently carries more weight than its detail supports.",
        },
        {
            "recommendation": "Add one more concrete metric to the Teaching Assistant entry, such as sections led or average grade improvement.",
            "reason": "This entry is currently description-only with no measurable outcome, unlike your internship bullets.",
        },
    ],
}
