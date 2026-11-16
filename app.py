
import streamlit as st
import pandas as pd
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="Student Attendance Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("🎓 Student Attendance Analytics")
st.write("Monitor and analyse student attendance records.")

# Read CSV file
df = pd.read_csv("attendance.csv")

# Remove unwanted spaces
df["status"] = df["status"].astype(str).str.strip().str.upper()

# Calculate student attendance
summary = df.groupby(
    ["student_id", "name"]
).agg(
    Total_Classes=("status", "count"),
    Present=("status", lambda x: (x == "P").sum()),
    Absent=("status", lambda x: (x == "A").sum())
).reset_index()

summary["Attendance_Percentage"] = (
    summary["Present"] / summary["Total_Classes"] * 100
).round(2)

# Dashboard metrics
total_students = len(summary)
total_classes = summary["Total_Classes"].sum()
total_present = summary["Present"].sum()
total_absent = summary["Absent"].sum()
average_attendance = summary["Attendance_Percentage"].mean()

st.subheader("📌 Attendance Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Students", total_students)
col2.metric("Average Attendance", f"{average_attendance:.2f}%")
col3.metric("Total Present", total_present)
col4.metric("Total Absent", total_absent)

# Student attendance table
st.subheader("📋 Student Attendance Report")

st.dataframe(summary, use_container_width=True)

# Attendance chart
st.subheader("📊 Student-wise Attendance")

fig = px.bar(
    summary,
    x="name",
    y="Attendance_Percentage",
    color="Attendance_Percentage",
    text="Attendance_Percentage",
    title="Attendance Percentage of Each Student",
    labels={
        "name": "Student Name",
        "Attendance_Percentage": "Attendance (%)"
    }
)

fig.add_hline(
    y=75,
    line_dash="dash",
    annotation_text="75% Minimum Attendance"
)

st.plotly_chart(fig, use_container_width=True)

# Low attendance students
st.subheader("⚠️ Students Below 75%")

low_attendance = summary[
    summary["Attendance_Percentage"] < 75
]

if len(low_attendance) > 0:
    st.dataframe(low_attendance, use_container_width=True)
else:
    st.success("All students have sufficient attendance!")

# Download report
st.subheader("⬇️ Download Attendance Report")

csv_data = summary.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Attendance Report",
    data=csv_data,
    file_name="attendance_report.csv",
    mime="text/csv"
)
