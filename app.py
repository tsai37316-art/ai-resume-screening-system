from flask import Flask, request, jsonify
from flask_cors import CORS
from pypdf import PdfReader
from werkzeug.utils import secure_filename
import os
import re
import uuid

app = Flask(__name__)
CORS(app)

# =========================================================
# CONFIGURATION
# =========================================================

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================================================
# SKILLS DATABASE
# =========================================================

SKILLS = [

    # ---------------- FRONTEND ----------------
    "html",
    "css",
    "javascript",
    "react",
    "angular",
    "vue",
    "bootstrap",
    "tailwind",

    # ---------------- BACKEND ----------------
    "python",
    "java",
    "c",
    "c++",
    "c#",
    "flask",
    "django",
    "spring",
    "spring boot",
    "node.js",
    "node",
    "express",
    "rest api",
    "api",

    # ---------------- DATABASE ----------------
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "oracle",

    # ---------------- PROGRAMMING / TOOLS ----------------
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",

    # ---------------- DATA / AI ----------------
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch"
]


# =========================================================
# SKILL CATEGORIES
# =========================================================

FRONTEND_SKILLS = [
    "html",
    "css",
    "javascript",
    "react",
    "angular",
    "vue",
    "bootstrap",
    "tailwind"
]

BACKEND_SKILLS = [
    "python",
    "java",
    "c",
    "c++",
    "c#",
    "flask",
    "django",
    "spring",
    "spring boot",
    "node.js",
    "node",
    "express",
    "rest api",
    "api",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "oracle"
]

OTHER_SKILLS = [
    "git",
    "github",
    "docker",
    "kubernetes",
    "aws",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "data science",
    "pandas",
    "numpy",
    "tensorflow",
    "pytorch"
]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================

def extract_pdf_text(file_path):

    text = ""

    try:

        reader = PdfReader(file_path)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception as e:

        print("PDF extraction error:", e)

    return text


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(text):

    text = text.lower()

    text = re.sub(r"\s+", " ", text)

    return text


# =========================================================
# DETECT SKILLS
# =========================================================

def detect_skills(text):

    text = normalize_text(text)

    detected = []

    for skill in SKILLS:

        if skill == "c++":

            pattern = r"\bc\+\+\b"

        elif skill == "c#":

            pattern = r"\bc#\b"

        elif skill == "c":

            pattern = r"\bc\b"

        elif skill == "node.js":

            pattern = r"\bnode\.js\b"

        elif skill == "spring boot":

            pattern = r"\bspring\s+boot\b"

        elif skill == "rest api":

            pattern = r"\brest\s+api\b"

        else:

            pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):

            detected.append(skill)

    return detected


# =========================================================
# CATEGORIZE SKILLS
# =========================================================

def categorize_skills(resume_skills):

    frontend = []

    backend = []

    other = []

    for skill in resume_skills:

        if skill in FRONTEND_SKILLS:

            frontend.append(skill)

        elif skill in BACKEND_SKILLS:

            backend.append(skill)

        else:

            other.append(skill)

    return frontend, backend, other


# =========================================================
# SCORE CALCULATION
# =========================================================

def calculate_score(resume_skills, job_skills):

    if not job_skills:

        return 0, []

    matched = []

    for skill in job_skills:

        # SQL aliases
        if skill == "sql":

            if (
                "sql" in resume_skills
                or "mysql" in resume_skills
                or "postgresql" in resume_skills
            ):

                matched.append(skill)

        elif skill in resume_skills:

            matched.append(skill)

    score = (
        len(matched) / len(job_skills)
    ) * 100

    return round(score), matched


# =========================================================
# DEFAULT JOB SKILLS
# =========================================================

def get_default_job_skills():

    return [

        "python",
        "java",
        "javascript",
        "html",
        "css",
        "sql",
        "git",
        "flask",
        "django",
        "rest api",
        "machine learning"

    ]


# =========================================================
# MISSING SKILLS
# =========================================================

def get_missing_skills(resume_skills, job_skills):

    missing = []

    for skill in job_skills:

        if skill == "sql":

            if not any(
                sql_skill in resume_skills
                for sql_skill in [
                    "sql",
                    "mysql",
                    "postgresql"
                ]
            ):

                missing.append(skill)

        elif skill not in resume_skills:

            missing.append(skill)

    return missing


# =========================================================
# SCORE BREAKDOWN
# =========================================================

def calculate_sections(text):

    text_lower = text.lower()

    detected_skills = detect_skills(text)

    # ---------------- SKILLS ----------------

    skill_score = min(
        30,
        len(detected_skills) * 3
    )

    # ---------------- EDUCATION ----------------

    education_keywords = [

        "education",
        "bachelor",
        "b.tech",
        "b.e",
        "bca",
        "m.tech",
        "mca",
        "degree",
        "university",
        "college"

    ]

    education_found = any(
        keyword in text_lower
        for keyword in education_keywords
    )

    education_score = (
        15 if education_found else 0
    )

    # ---------------- PROJECTS ----------------

    project_keywords = [

        "project",
        "projects",
        "developed",
        "built",
        "implemented"

    ]

    project_found = any(
        keyword in text_lower
        for keyword in project_keywords
    )

    project_score = (
        20 if project_found else 0
    )

    # ---------------- EXPERIENCE ----------------

    experience_keywords = [

        "experience",
        "internship",
        "intern",
        "developer",
        "worked",
        "employment"

    ]

    experience_found = any(
        keyword in text_lower
        for keyword in experience_keywords
    )

    experience_score = (
        20 if experience_found else 0
    )

    # ---------------- CERTIFICATIONS ----------------

    certification_keywords = [

        "certification",
        "certifications",
        "certificate",
        "certified"

    ]

    certification_found = any(
        keyword in text_lower
        for keyword in certification_keywords
    )

    certification_score = (
        10 if certification_found else 0
    )

    # ---------------- COMPLETENESS ----------------

    completeness_score = (
        5 if len(text.strip()) > 200 else 0
    )

    return {

        "skills": skill_score,

        "education": education_score,

        "projects": project_score,

        "experience": experience_score,

        "certifications": certification_score,

        "completeness": completeness_score

    }


# =========================================================
# RECOMMENDED SKILLS
# =========================================================

def get_recommended_skills(resume_skills):

    recommended = [

        "javascript",
        "react",
        "flask",
        "django",
        "rest api",
        "api",
        "machine learning",
        "git",
        "docker",
        "aws"

    ]

    result = []

    for skill in recommended:

        if skill not in resume_skills:

            result.append(skill)

    return result


# =========================================================
# JOB ROLE RECOMMENDATION
# =========================================================

def get_job_roles(resume_skills):

    roles = []

    # Web Developer

    if any(
        skill in resume_skills
        for skill in [
            "html",
            "css",
            "javascript",
            "react"
        ]
    ):

        roles.append("Web Developer")

    # Data Analyst

    if any(
        skill in resume_skills
        for skill in [
            "python",
            "sql",
            "mysql",
            "pandas",
            "numpy"
        ]
    ):

        roles.append("Data Analyst")

    # Java Developer

    if (
        "java" in resume_skills
        or "spring" in resume_skills
        or "spring boot" in resume_skills
    ):

        roles.append("Java Developer")

    # Python Developer

    if "python" in resume_skills:

        roles.append("Python Developer")

    # Machine Learning Engineer

    if any(
        skill in resume_skills
        for skill in [
            "machine learning",
            "tensorflow",
            "pytorch"
        ]
    ):

        roles.append(
            "Machine Learning Engineer"
        )

    # Backend Developer

    if any(
        skill in resume_skills
        for skill in [
            "python",
            "java",
            "flask",
            "django",
            "spring boot",
            "node.js"
        ]
    ):

        roles.append(
            "Backend Developer"
        )

    # Default roles

    if not roles:

        roles = [

            "Software Developer",

            "Web Developer",

            "Data Analyst"

        ]

    # Remove duplicates

    return list(
        dict.fromkeys(roles)
    )[:5]


# =========================================================
# RESUME SUGGESTIONS
# =========================================================

def get_suggestions(text, resume_skills):

    text_lower = text.lower()

    suggestions = []

    # Certifications

    if not any(
        word in text_lower
        for word in [
            "certification",
            "certificate",
            "certified"
        ]
    ):

        suggestions.append(
            "Add relevant certifications if you have them."
        )

    # Skills

    if len(resume_skills) < 8:

        suggestions.append(
            "Add more job-related technical skills."
        )

    # Projects

    if "project" not in text_lower:

        suggestions.append(
            "Mention your projects clearly."
        )

    # Experience

    if (
        "experience" not in text_lower
        and "internship" not in text_lower
    ):

        suggestions.append(
            "Add internship or work experience if available."
        )

    # Keywords

    suggestions.append(
        "Use relevant technical keywords in your resume."
    )

    return suggestions


# =========================================================
# HOME ROUTE
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({

        "message":
        "AI Resume Screening Backend is running",

        "status":
        "success"

    })


# =========================================================
# ANALYZE RESUME
# =========================================================

@app.route("/analyze", methods=["POST"])
def analyze_resume():

    try:

        # -------------------------------------------------
        # CHECK FILE
        # -------------------------------------------------

        if "resume" not in request.files:

            return jsonify({

                "success": False,

                "error":
                "No resume file uploaded."

            }), 400

        file = request.files["resume"]

        # -------------------------------------------------
        # CHECK FILE NAME
        # -------------------------------------------------

        if file.filename == "":

            return jsonify({

                "success": False,

                "error":
                "No file selected."

            }), 400

        # -------------------------------------------------
        # CHECK PDF
        # -------------------------------------------------

        if not allowed_file(file.filename):

            return jsonify({

                "success": False,

                "error":
                "Only PDF files are allowed."

            }), 400

        # -------------------------------------------------
        # SAFE FILE NAME
        # -------------------------------------------------

        original_filename = secure_filename(
            file.filename
        )

        # Give uploaded file a unique name

        unique_filename = (
            str(uuid.uuid4())
            + "_"
            + original_filename
        )

        file_path = os.path.join(
            UPLOAD_FOLDER,
            unique_filename
        )

        file.save(file_path)

        # -------------------------------------------------
        # EXTRACT PDF TEXT
        # -------------------------------------------------

        extracted_text = extract_pdf_text(
            file_path
        )

        print("--------------------------------")
        print("File:", original_filename)
        print(
            "Extracted characters:",
            len(extracted_text)
        )
        print("--------------------------------")

        # -------------------------------------------------
        # CHECK TEXT
        # -------------------------------------------------

        if not extracted_text.strip():

            return jsonify({

                "success": False,

                "error":
                "Could not extract text from this PDF. "
                "Please upload a text-based PDF.",

                "file_name":
                original_filename,

                "extracted_text_length":
                0

            }), 400

        # -------------------------------------------------
        # DETECT ALL SKILLS
        # -------------------------------------------------

        resume_skills = detect_skills(
            extracted_text
        )

        # -------------------------------------------------
        # SEPARATE FRONTEND / BACKEND / OTHER
        # -------------------------------------------------

        frontend_skills, backend_skills, other_skills = (
            categorize_skills(resume_skills)
        )

        # -------------------------------------------------
        # DEFAULT JOB SKILLS
        # -------------------------------------------------

        job_skills = get_default_job_skills()

        # -------------------------------------------------
        # MATCH SCORE
        # -------------------------------------------------

        score, matched_skills = calculate_score(
            resume_skills,
            job_skills
        )

        # -------------------------------------------------
        # MISSING SKILLS
        # -------------------------------------------------

        missing_skills = get_missing_skills(
            resume_skills,
            job_skills
        )

        # -------------------------------------------------
        # SCORE BREAKDOWN
        # -------------------------------------------------

        sections = calculate_sections(
            extracted_text
        )

        # -------------------------------------------------
        # RECOMMENDED SKILLS
        # -------------------------------------------------

        recommended_skills = get_recommended_skills(
            resume_skills
        )

        # -------------------------------------------------
        # JOB ROLES
        # -------------------------------------------------

        job_roles = get_job_roles(
            resume_skills
        )

        # -------------------------------------------------
        # SUGGESTIONS
        # -------------------------------------------------

        suggestions = get_suggestions(
            extracted_text,
            resume_skills
        )

        # -------------------------------------------------
        # MATCH MESSAGE
        # -------------------------------------------------

        if score >= 80:

            match_message = (
                "Excellent match! The resume contains "
                "most of the required skills."
            )

        elif score >= 60:

            match_message = (
                "Good match. A few important skills "
                "could be added."
            )

        elif score >= 40:

            match_message = (
                "Moderate match. Some important skills "
                "are missing."
            )

        else:

            match_message = (
                "Low match. The resume needs improvement "
                "for this job."
            )

        # -------------------------------------------------
        # FINAL RESPONSE
        # -------------------------------------------------

        response = {

            "success": True,

            "file_name":
            original_filename,

            "extracted_text":
            extracted_text,

            "extracted_text_length":
            len(extracted_text),

            # --------------------------------------------
            # ALL SKILLS
            # --------------------------------------------

            "total_skills":
            len(resume_skills),

            "skills_detected":
            resume_skills,

            # --------------------------------------------
            # SKILL CATEGORIES
            # --------------------------------------------

            "frontend_skills":
            frontend_skills,

            "backend_skills":
            backend_skills,

            "other_skills":
            other_skills,

            # --------------------------------------------
            # JOB MATCH
            # --------------------------------------------

            "job_skills":
            job_skills,

            "matched_skills":
            matched_skills,

            "missing_skills":
            missing_skills,

            "match_score":
            score,

            "match_message":
            match_message,

            # --------------------------------------------
            # RECOMMENDATIONS
            # --------------------------------------------

            "recommended_skills":
            recommended_skills,

            "recommended_job_roles":
            job_roles,

            # --------------------------------------------
            # SCORE BREAKDOWN
            # --------------------------------------------

            "score_breakdown":
            sections,

            # --------------------------------------------
            # SUGGESTIONS
            # --------------------------------------------

            "improvement_suggestions":
            suggestions
        }

        return jsonify(response)

    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as e:

        print("ERROR:", str(e))

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    print("---------------------------------------")
    print("AI Resume Screening System")
    print("Backend running on:")
    print("http://127.0.0.1:5000")
    print("---------------------------------------")

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )