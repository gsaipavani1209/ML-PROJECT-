
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import PerformanceInput
from backend.prediction import predict_performance, performance_model
from backend.database import (
    initialize_database,
    save_prediction,
    get_prediction_history,
)

app = FastAPI(
    title="Student Performance Prediction System",
    description="ML-powered student academic performance prediction API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    initialize_database()


@app.get("/")
def home():
    return {
        "message": "Student Performance Prediction System API is running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}



    
@app.get("/dataset/average-cgpa")
def dataset_average_cgpa():
    import pandas as pd
    from pathlib import Path

    project_root = Path(__file__).resolve().parent.parent
    dataset_path = (
        project_root / "data" / "Students_Performance_data_set.xlsx"
    )

    if not dataset_path.exists():
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail="Performance dataset file was not found.",
        )

    df = pd.read_excel(dataset_path)
    target_column = "What is your current CGPA?"

    if target_column not in df.columns:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"CGPA column not found: {target_column}",
        )

    cgpa = pd.to_numeric(df[target_column], errors="coerce").dropna()

    if cgpa.empty:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail="No valid CGPA values were found in the dataset.",
        )

    return {
        "dataset_average_cgpa": round(float(cgpa.mean()), 2),
        "total_students": int(cgpa.count()),
    }




@app.get("/dataset/eda")
def dataset_eda():
    df = pd.read_excel(PERFORMANCE_DATASET)

    target = "What is your current CGPA?"
    attendance_col = "Average attendance on class"
    study_col = "How many hour do you study daily?"

    if target not in df.columns:
        raise HTTPException(
            status_code=500,
            detail=f"CGPA column not found: {target}",
        )

    df[target] = pd.to_numeric(df[target], errors="coerce")
    valid = df.dropna(subset=[target]).copy()

    if valid.empty:
        raise HTTPException(
            status_code=500,
            detail="No valid CGPA values were found.",
        )

    # CGPA distribution
    bins = [0, 1, 2, 2.5, 3, 3.5, 4.01]
    labels = ["0–1", "1–2", "2–2.5", "2.5–3", "3–3.5", "3.5–4"]

    cgpa_bins = pd.cut(
        valid[target],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True,
    )

    cgpa_distribution = [
        {
            "range": label,
            "count": int((cgpa_bins == label).sum()),
        }
        for label in labels
    ]

    # Attendance category vs average CGPA
    attendance_vs_cgpa = []

    if attendance_col in valid.columns:
        attendance_df = valid[[attendance_col, target]].dropna().copy()
        attendance_df[attendance_col] = (
            attendance_df[attendance_col].astype(str).str.strip()
        )

        grouped = attendance_df.groupby(attendance_col)[target].mean()

        attendance_vs_cgpa = [
            {
                "attendance": str(label),
                "average_cgpa": round(float(value), 2),
            }
            for label, value in grouped.items()
        ]

    # Daily study hours vs average CGPA
    study_hours_vs_cgpa = []

    if study_col in valid.columns:
        study_df = valid[[study_col, target]].copy()
        study_df[study_col] = pd.to_numeric(
            study_df[study_col], errors="coerce"
        )
        study_df = study_df.dropna(subset=[study_col, target])

        grouped = study_df.groupby(study_col)[target].mean().sort_index()

        study_hours_vs_cgpa = [
            {
                "study_hours": str(label),
                "average_cgpa": round(float(value), 2),
            }
            for label, value in grouped.items()
        ]

    return {
        "cgpa_distribution": cgpa_distribution,
        "attendance_vs_cgpa": attendance_vs_cgpa,
        "study_hours_vs_cgpa": study_hours_vs_cgpa,
    }









@app.get("/predictions/history")
def prediction_history():
    history = get_prediction_history()

    # Keep only student performance predictions
    performance_history = [
        record
        for record in history
        if record.get("prediction_type") == "performance"
    ]

    return {
        "total": len(performance_history),
        "predictions": performance_history,
    }



@app.post("/predict/performance")
def performance_prediction(student: PerformanceInput):
    data = {
        "University Admission year": student.university_admission_year,
        "Gender": student.gender,
        "Age": student.age,
        "H.S.C passing year": student.hsc_passing_year,
        "Program": student.program,
        "Current Semester": student.current_semester,
        "Do you have meritorious scholarship ?": student.meritorious_scholarship,
        "Do you use University transportation?": student.university_transportation,
        "How many hour do you study daily?": student.daily_study_hours,
        "How many times do you seat for study in a day?": student.study_sessions_per_day,
        "What is your preferable learning mode?": student.preferable_learning_mode,
        "Do you use smart phone?": student.smartphone,
        "Do you have personal Computer?": student.personal_computer,
        "How many hour do you spent daily in social media?": student.daily_social_media_hours,
        "Status of your English language proficiency": student.english_proficiency,
        "Average attendance on class": student.average_attendance,
        "Did you ever fall in probation?": student.probation,
        "Did you ever got suspension?": student.suspension,
        "Do you attend in teacher consultancy for any kind of academical problems?": student.teacher_consultancy,
        "What are the skills do you have ?": student.skills,
        "How many hour do you spent daily on your skill development?": student.skill_development_hours,
        "What is you interested area?": student.interested_area,
        "What is your relationship status?": student.relationship_status,
        "Are you engaged with any co-curriculum activities?": student.cocurriculum_activities,
        "With whom you are living with?": student.living_status,
        "Do you have any health issues?": student.health_issues,
        "What was your previous SGPA?": student.previous_sgpa,
        "Do you have any physical disabilities?": student.physical_disabilities,
        "How many Credit did you have completed?": student.completed_credits,
        "What is your monthly family income?": student.monthly_family_income,
    }

    df = pd.DataFrame([data])
    predicted_cgpa = predict_performance(df)

    result = {
        "predicted_cgpa": round(predicted_cgpa, 2)
    }

    prediction_id = save_prediction(
        "performance",
        student.dict(),
        result,
    )

    return {
        **result,
        "prediction_id": prediction_id,
        "message": "Prediction saved successfully",
    }


# Performance prediction using Roll Number

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PERFORMANCE_DATASET = (
    PROJECT_ROOT / "data" / "Students_Performance_data_set.xlsx"
)


def get_performance_category(cgpa):
    if cgpa >= 3.50:
        return "Good"
    elif cgpa >= 2.50:
        return "Average"
    return "Poor"


def clean_component_value(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        value = value.item()

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


@app.post("/predict/performance/roll/{roll_no}")
def predict_performance_by_roll(roll_no: int):
    if not PERFORMANCE_DATASET.exists():
        raise HTTPException(
            status_code=500,
            detail="Performance dataset file was not found.",
        )

    try:
        df = pd.read_excel(PERFORMANCE_DATASET)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not read performance dataset: {exc}",
        )

    df.columns = (
        df.columns.astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    if "Roll No" not in df.columns:
        raise HTTPException(
            status_code=500,
            detail="Roll No column is missing from the dataset.",
        )

    student_rows = df[df["Roll No"] == roll_no]

    if student_rows.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Roll No {roll_no} was not found.",
        )

    actual = student_rows.iloc[0]
    target_column = "What is your current CGPA?"

    if target_column not in df.columns:
        raise HTTPException(
            status_code=500,
            detail="Current CGPA column is missing from the dataset.",
        )

    actual_cgpas = pd.to_numeric(
        df[target_column], errors="coerce"
    ).dropna()

    dataset_average = (
        float(actual_cgpas.mean())
        if not actual_cgpas.empty else None
    )

    student = student_rows.iloc[[0]].copy()
    student = student.drop(
        columns=["Roll No", target_column],
        errors="ignore",
    )

    rename_columns = {
        "Whatare the skills do you have ?":
            "What are the skills do you have ?",
        "How many times doyou seat for study in a day?":
            "How many times do you seat for study in a day?",
    }

    student = student.rename(columns=rename_columns)
    expected_columns = list(performance_model.feature_names_in_)

    missing = [
        column for column in expected_columns
        if column not in student.columns
    ]

    if missing:
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Required model features are missing.",
                "missing_columns": missing,
            },
        )

    model_input = student[expected_columns]
    predicted_cgpa = predict_performance(model_input)
    category = get_performance_category(predicted_cgpa)

    components = {
        "attendance": clean_component_value(
            actual.get("Average attendance on class")
        ),
        "previous_sgpa": clean_component_value(
            actual.get("What was your previous SGPA?")
        ),
        "daily_study_hours": clean_component_value(
            actual.get("How many hour do you study daily?")
        ),
        "completed_credits": clean_component_value(
            actual.get("How many Credit did you have completed?")
        ),
    }

    recommendations = []

    attendance = str(
        components["attendance"] or ""
    ).strip().lower()

    if attendance:
        if any(word in attendance for word in ["low", "poor", "below"]):
            recommendations.append(
                "Improve class attendance and attend lessons regularly."
            )
        else:
            recommendations.append(
                "Maintain regular attendance and review any missed lessons."
            )

    try:
        previous_sgpa = float(components["previous_sgpa"])

        if previous_sgpa < 2.50:
            recommendations.append(
                "Revise foundational topics and follow a structured study plan."
            )
        elif previous_sgpa < 3.50:
            recommendations.append(
                "Set weekly learning goals to improve on your previous SGPA."
            )
        else:
            recommendations.append(
                "Maintain your academic progress with consistent revision."
            )
    except (TypeError, ValueError):
        pass

    try:
        study_hours = float(components["daily_study_hours"])

        if study_hours < 2:
            recommendations.append(
                "Consider adding more focused study time to your daily routine."
            )
        else:
            recommendations.append(
                "Continue your study routine and include regular revision."
            )
    except (TypeError, ValueError):
        pass

    if not recommendations:
        recommendations.append(
            "Set academic goals, review your progress weekly, and seek help when needed."
        )

    result = {
        "roll_no": roll_no,
        "predicted_cgpa": round(predicted_cgpa, 2),
        "performance_category": category,
        "dataset_average_cgpa": (
            round(dataset_average, 2)
            if dataset_average is not None else None
        ),
        "components": components,
        "recommendations": recommendations,
    }

    prediction_id = save_prediction(
        "performance",
        {"roll_no": roll_no},
        result,
    )

    return {
        **result,
        "prediction_id": prediction_id,
        "message": "Prediction saved successfully",
    }
