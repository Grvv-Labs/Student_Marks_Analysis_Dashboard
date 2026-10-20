from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
import os

app = FastAPI(title="Student Marks Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Any website can talk to our backend
    allow_methods=["*"],    # GET POST PUT DELETE
    allow_headers=["*"],    # Allow all request headers.
)

# ── Load & clean data once at startup ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "..", "student_marks.csv")

def load_data() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df.drop_duplicates(inplace=True)
    
    subject_mean = df.groupby("Subject")["Marks"].transform("mean")

    df["Marks"] = df["Marks"].fillna(subject_mean)
    df["Marks"] = df["Marks"].round().astype(int)

    bins  = [-1, 39, 59, 79, 89, 100]
    grade_labels = ["F (<40)", "C (40-59)", "B (60-79)", "A (80-89)", "A+ (90-100)"]
    df["Grade"] = pd.cut(df["Marks"], bins=bins, labels=grade_labels)
    return df

df = load_data()

# ── REST API ───────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats():
    return {
        "total_students": int(df["Student_ID"].nunique()),
        "total_records":  int(len(df)),
        "overall_avg":    round(float(df["Marks"].mean()), 2),
        "highest_mark":   int(df["Marks"].max()),
        "lowest_mark":    int(df["Marks"].min()),
        "subjects_count": int(df["Subject"].nunique()),
        "classes_count":  int(df["Class"].nunique()),
    }


@app.get("/api/subject-averages")
def get_subject_averages():
    result = (
        df.groupby("Subject")["Marks"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
        .reset_index()
    )
    return result.rename(columns={"Marks": "average"}).to_dict(orient="records")


@app.get("/api/grade-distribution")
def get_grade_distribution():
    counts = df["Grade"].value_counts().sort_index()
    return [{"grade": str(k), "count": int(v)} for k, v in counts.items()]


@app.get("/api/top-students")
def get_top_students(limit: int = Query(default=10, ge=1, le=50)):
    student_stats = (
        df.groupby(["Student_ID", "Student_Name"])
        .agg(
            total_marks=("Marks", "sum"),
            avg_marks=("Marks", "mean"),
            subjects_taken=("Subject", "count"),
        )
        .reset_index()
    )
    student_stats["avg_marks"] = student_stats["avg_marks"].round(2)
    top = student_stats.nlargest(limit, "total_marks")
    top.insert(0, "rank", range(1, len(top) + 1))
    return top.to_dict(orient="records")


@app.get("/api/class-performance")
def get_class_performance():
    result = (
        df.groupby("Class")["Marks"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
        .reset_index()
    )
    return result.rename(columns={"Marks": "average"}).to_dict(orient="records")


@app.get("/api/subject-class-heatmap")
def get_subject_class_heatmap():
    pivot = df.pivot_table(
        values="Marks", index="Class", columns="Subject", aggfunc="mean"
    ).round(2)
    return pivot.reset_index().to_dict(orient="records")


@app.get("/api/students")
def get_students(
    search: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
):
    student_df = (
        df.groupby(["Student_ID", "Student_Name", "Class"])
        .agg(avg_marks=("Marks", "mean"), total_marks=("Marks", "sum"))
        .reset_index()
    )
    student_df["avg_marks"] = student_df["avg_marks"].round(2)

    if search:
        mask = (
            student_df["Student_Name"].str.contains(search, case=False, na=False)
            | student_df["Student_ID"].str.contains(search, case=False, na=False)
        )
        student_df = student_df[mask]

    total = len(student_df)
    start = (page - 1) * per_page
    records = student_df.iloc[start : start + per_page].to_dict(orient="records")
    return {"total": total, "page": page, "per_page": per_page, "students": records}


# ── Serve frontend static files ────────────────────────────────────────────────
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))
