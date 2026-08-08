"""
Skill Compass — Student Skill Gap Analysis & Career Recommendation System
Backend: Flask (Python)

Run:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, jsonify
from dataclasses import dataclass, field
from typing import Dict, List

app = Flask(__name__)

# ---------------------------------------------------------------------------
# 1. DATA MODEL
# ---------------------------------------------------------------------------
# Every skill has a category, used purely for grouping in the UI.
SKILL_CATALOG: Dict[str, str] = {
    "HTML/CSS": "Web Development",
    "JavaScript": "Web Development",
    "React": "Web Development",
    "Node.js": "Web Development",
    "REST APIs": "Web Development",
    "Python": "Programming",
    "Java": "Programming",
    "C++": "Programming",
    "SQL": "Data",
    "Data Analysis": "Data",
    "Machine Learning": "Data",
    "Statistics": "Data",
    "Pandas/NumPy": "Data",
    "Data Visualization": "Data",
    "Git/GitHub": "Tools",
    "Linux": "Tools",
    "Docker": "Cloud & DevOps",
    "AWS/Cloud": "Cloud & DevOps",
    "CI/CD": "Cloud & DevOps",
    "Networking": "Cloud & DevOps",
    "Cybersecurity Basics": "Security",
    "UI/UX Design": "Design",
    "Figma": "Design",
    "Mobile Development": "Programming",
    "Agile/Scrum": "Soft Skills",
    "Communication": "Soft Skills",
    "Problem Solving": "Soft Skills",
    "Project Management": "Soft Skills",
}

# Each career maps required skill -> importance weight (1 = nice-to-have, 3 = core).
# min_level is the proficiency (1-5) expected for a job-ready candidate.
@dataclass
class Career:
    name: str
    description: str
    required_skills: Dict[str, Dict[str, int]]  # skill -> {"weight": int, "min_level": int}
    avg_salary_inr: str
    growth: str


CAREERS: List[Career] = [
    Career(
        "Frontend Developer",
        "Builds the visual, interactive parts of websites and web apps.",
        {
            "HTML/CSS": {"weight": 3, "min_level": 4},
            "JavaScript": {"weight": 3, "min_level": 4},
            "React": {"weight": 3, "min_level": 3},
            "Git/GitHub": {"weight": 2, "min_level": 3},
            "REST APIs": {"weight": 2, "min_level": 2},
            "UI/UX Design": {"weight": 1, "min_level": 2},
        },
        "4-9 LPA",
        "High",
    ),
    Career(
        "Backend Developer",
        "Designs servers, databases, and the logic behind applications.",
        {
            "Python": {"weight": 3, "min_level": 4},
            "SQL": {"weight": 3, "min_level": 3},
            "REST APIs": {"weight": 3, "min_level": 3},
            "Git/GitHub": {"weight": 2, "min_level": 3},
            "Linux": {"weight": 2, "min_level": 2},
            "Docker": {"weight": 1, "min_level": 2},
        },
        "5-10 LPA",
        "High",
    ),
    Career(
        "Full Stack Developer",
        "Handles both the interface and the server side of an application.",
        {
            "HTML/CSS": {"weight": 2, "min_level": 3},
            "JavaScript": {"weight": 3, "min_level": 4},
            "React": {"weight": 2, "min_level": 3},
            "Node.js": {"weight": 2, "min_level": 3},
            "SQL": {"weight": 2, "min_level": 3},
            "Git/GitHub": {"weight": 2, "min_level": 3},
            "REST APIs": {"weight": 3, "min_level": 3},
        },
        "6-12 LPA",
        "Very High",
    ),
    Career(
        "Data Analyst",
        "Turns raw data into charts and insights that guide decisions.",
        {
            "SQL": {"weight": 3, "min_level": 4},
            "Data Analysis": {"weight": 3, "min_level": 4},
            "Pandas/NumPy": {"weight": 2, "min_level": 3},
            "Data Visualization": {"weight": 3, "min_level": 3},
            "Statistics": {"weight": 2, "min_level": 3},
            "Communication": {"weight": 1, "min_level": 3},
        },
        "4-8 LPA",
        "High",
    ),
    Career(
        "Data Scientist",
        "Builds statistical & ML models to solve business problems.",
        {
            "Python": {"weight": 3, "min_level": 4},
            "Statistics": {"weight": 3, "min_level": 4},
            "Machine Learning": {"weight": 3, "min_level": 3},
            "Pandas/NumPy": {"weight": 2, "min_level": 4},
            "SQL": {"weight": 2, "min_level": 3},
            "Data Visualization": {"weight": 1, "min_level": 2},
        },
        "6-14 LPA",
        "Very High",
    ),
    Career(
        "Machine Learning Engineer",
        "Deploys and scales ML models into production systems.",
        {
            "Python": {"weight": 3, "min_level": 4},
            "Machine Learning": {"weight": 3, "min_level": 4},
            "Statistics": {"weight": 2, "min_level": 3},
            "Docker": {"weight": 2, "min_level": 2},
            "AWS/Cloud": {"weight": 2, "min_level": 2},
            "SQL": {"weight": 1, "min_level": 2},
        },
        "7-16 LPA",
        "Very High",
    ),
    Career(
        "DevOps Engineer",
        "Automates deployment pipelines and manages cloud infrastructure.",
        {
            "Linux": {"weight": 3, "min_level": 4},
            "Docker": {"weight": 3, "min_level": 3},
            "AWS/Cloud": {"weight": 3, "min_level": 3},
            "CI/CD": {"weight": 3, "min_level": 3},
            "Git/GitHub": {"weight": 2, "min_level": 3},
            "Networking": {"weight": 1, "min_level": 2},
        },
        "6-13 LPA",
        "High",
    ),
    Career(
        "UI/UX Designer",
        "Designs intuitive, user-friendly digital experiences.",
        {
            "UI/UX Design": {"weight": 3, "min_level": 4},
            "Figma": {"weight": 3, "min_level": 4},
            "Communication": {"weight": 2, "min_level": 3},
            "HTML/CSS": {"weight": 1, "min_level": 2},
            "Problem Solving": {"weight": 1, "min_level": 3},
        },
        "4-9 LPA",
        "Medium",
    ),
    Career(
        "Cybersecurity Analyst",
        "Protects systems and networks from digital threats.",
        {
            "Cybersecurity Basics": {"weight": 3, "min_level": 4},
            "Networking": {"weight": 3, "min_level": 3},
            "Linux": {"weight": 2, "min_level": 3},
            "Python": {"weight": 1, "min_level": 2},
            "Problem Solving": {"weight": 1, "min_level": 3},
        },
        "5-11 LPA",
        "High",
    ),
    Career(
        "Mobile App Developer",
        "Builds applications for Android and iOS devices.",
        {
            "Mobile Development": {"weight": 3, "min_level": 4},
            "Java": {"weight": 2, "min_level": 3},
            "REST APIs": {"weight": 2, "min_level": 2},
            "Git/GitHub": {"weight": 1, "min_level": 2},
            "UI/UX Design": {"weight": 1, "min_level": 2},
        },
        "5-10 LPA",
        "High",
    ),
    Career(
        "Product Manager",
        "Bridges business, design and engineering to ship products.",
        {
            "Communication": {"weight": 3, "min_level": 4},
            "Project Management": {"weight": 3, "min_level": 4},
            "Agile/Scrum": {"weight": 2, "min_level": 3},
            "Data Analysis": {"weight": 2, "min_level": 2},
            "Problem Solving": {"weight": 2, "min_level": 3},
        },
        "7-15 LPA",
        "Medium",
    ),
    Career(
        "QA / Test Engineer",
        "Ensures software quality through manual and automated testing.",
        {
            "Problem Solving": {"weight": 2, "min_level": 3},
            "Python": {"weight": 2, "min_level": 2},
            "SQL": {"weight": 1, "min_level": 2},
            "Git/GitHub": {"weight": 1, "min_level": 2},
            "Communication": {"weight": 1, "min_level": 2},
        },
        "3-7 LPA",
        "Medium",
    ),
]

CAREER_MAP = {c.name: c for c in CAREERS}


# ---------------------------------------------------------------------------
# 2. ANALYSIS ENGINE
# ---------------------------------------------------------------------------
def analyze_gap(user_skills: Dict[str, int], career: Career) -> dict:
    """Compare a student's skill levels against one career's requirements."""
    matched, weak, missing = [], [], []
    total_weight = 0
    earned_weight = 0.0

    for skill, req in career.required_skills.items():
        weight, min_level = req["weight"], req["min_level"]
        total_weight += weight
        user_level = user_skills.get(skill, 0)

        if user_level <= 0:
            missing.append({"skill": skill, "required_level": min_level, "weight": weight})
            continue

        contribution = min(user_level / min_level, 1.0) * weight
        earned_weight += contribution

        if user_level >= min_level:
            matched.append({"skill": skill, "your_level": user_level, "required_level": min_level})
        else:
            weak.append({"skill": skill, "your_level": user_level, "required_level": min_level, "weight": weight})

    match_percent = round((earned_weight / total_weight) * 100, 1) if total_weight else 0.0

    return {
        "career": career.name,
        "description": career.description,
        "avg_salary_inr": career.avg_salary_inr,
        "growth": career.growth,
        "match_percent": match_percent,
        "matched_skills": matched,
        "weak_skills": weak,
        "missing_skills": missing,
    }


def recommend_careers(user_skills: Dict[str, int], top_n: int = 5) -> List[dict]:
    results = [analyze_gap(user_skills, c) for c in CAREERS]
    results.sort(key=lambda r: r["match_percent"], reverse=True)
    return results[:top_n]


# ---------------------------------------------------------------------------
# 3. ROUTES
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    grouped: Dict[str, List[str]] = {}
    for skill, category in SKILL_CATALOG.items():
        grouped.setdefault(category, []).append(skill)
    career_names = [c.name for c in CAREERS]
    return render_template("index.html", skill_groups=grouped, career_names=career_names)


@app.route("/api/careers")
def api_careers():
    return jsonify([c.name for c in CAREERS])


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    payload = request.get_json(force=True) or {}
    user_skills = payload.get("skills", {})
    target = payload.get("target_career")

    user_skills = {k: int(v) for k, v in user_skills.items() if int(v) > 0}

    if not user_skills:
        return jsonify({"error": "Select at least one skill and rate it."}), 400

    if target and target in CAREER_MAP:
        result = analyze_gap(user_skills, CAREER_MAP[target])
        return jsonify({"mode": "single", "result": result})

    recommendations = recommend_careers(user_skills, top_n=5)
    return jsonify({"mode": "recommend", "results": recommendations})


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)