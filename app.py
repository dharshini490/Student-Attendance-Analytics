
import streamlit as st
import pandas as pd
from database import connect_db, create_tables

create_tables()

st.set_page_config(
    page_title="Student Attendance Analytics",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Attendance Analytics")

menu = st.sidebar.selectbox(
    "Select Option",
    [
        "Dashboard",
        "Add Student",
        "View Students",
        "Mark Attendance",
        "Attendance Report"
    ]
)

# 1. ADD STUDENT
if menu == "Add Student":

    st.header("Register New Student")

    with st.form("student_form"):

        register_no = st.text_input("Register Number")
        name = st.text_input("Student Name")
        class_name = st.text_input("Class")
        department = st.text_input("Department")

        submit = st.form_submit_button("Save Student")

        if submit:

            if register_no and name and class_name and department:

                conn = connect_db()
                cursor = conn.cursor()

                try:
                    cursor.execute("""
                        INSERT INTO students
                        (register_no, name, class_name, department)
                        VALUES (?, ?, ?, ?)
                    """, (register_no, name, class_name, department))

                    conn.commit()
                    st.success("Student registered successfully!")

                except Exception as e:
                    st.error("Could not register student. Register number may already exist.")

                finally:
                    conn.close()

            else:
                st.warning("Please fill in all details.")

# 2. VIEW STUDENTS
elif menu == "View Students":

    st.header("Registered Students")

    conn = connect_db()

    df = pd.read_sql_query(
        "SELECT * FROM students",
        conn
    )

    conn.close()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
        st.metric("Total Students", len(df))
    else:
        st.info("No students registered yet.")

# 3. MARK ATTENDANCE
elif menu == "Mark Attendance":

    st.header("Mark Daily Attendance")

    conn = connect_db()

    students = pd.read_sql_query(
        "SELECT * FROM students",
        conn
    )

    conn.close()

    if not students.empty:

        selected_date = st.date_input("Select Attendance Date")

        attendance_data = []

        for _, student in students.iterrows():

            status = st.selectbox(
                student["name"] + " (" + student["register_no"] + ")",
                ["Present", "Absent"],
                key="attendance_" + str(student["register_no"])
            )

            attendance_data.append(
                (student["register_no"], str(selected_date), status)
            )

        if st.button("Save Attendance"):

            conn = connect_db()
            cursor = conn.cursor()

            for record in attendance_data:
                cursor.execute("""
                    INSERT INTO attendance
                    (register_no, date, status)
                    VALUES (?, ?, ?)
                    ON CONFLICT(register_no, date)
                    DO UPDATE SET status = excluded.status
                """, record)

            conn.commit()
            conn.close()

            st.success("Attendance saved successfully!")

    else:
        st.warning("Please register students first.")

# 4. ATTENDANCE REPORT
elif menu == "Attendance Report":

    st.header("Student Attendance Report")

    conn = connect_db()

    report = pd.read_sql_query("""
        SELECT
            s.register_no,
            s.name,
            s.class_name,
            COUNT(a.id) AS total_classes,
            SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS absent
        FROM students s
        LEFT JOIN attendance a
        ON s.register_no = a.register_no
        GROUP BY s.register_no, s.name, s.class_name
    """, conn)

    conn.close()

    if not report.empty:

        report["attendance_percentage"] = (
            report["present"] /
            report["total_classes"].replace(0, 1)
        ) * 100

        report.loc[
            report["total_classes"] == 0,
            "attendance_percentage"
        ] = 0

        report["attendance_percentage"] = (
            report["attendance_percentage"].round(2)
        )

        st.dataframe(report, use_container_width=True)

        st.metric(
            "Total Students",
            len(report)
        )

        st.metric(
            "Average Attendance",
            str(round(report["attendance_percentage"].mean(), 2)) + "%"
        )

        low_attendance = report[
            report["attendance_percentage"] < 75
        ]

        st.subheader("Students Below 75% Attendance")

        st.dataframe(low_attendance, use_container_width=True)

        csv = report.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Attendance Report",
            csv,
            "attendance_report.csv",
            "text/csv"
        )

    else:
        st.info("No students registered yet.")

# 5. DASHBOARD
else:

    st.header("Dashboard")

    conn = connect_db()

    students = pd.read_sql_query(
        "SELECT * FROM students",
        conn
    )

    attendance = pd.read_sql_query(
        "SELECT * FROM attendance",
        conn
    )

    conn.close()

    total_students = len(students)
    total_present = len(attendance[attendance["status"] == "Present"])
    total_absent = len(attendance[attendance["status"] == "Absent"])

    total_records = len(attendance)

    average = (
        total_present / total_records * 100
        if total_records > 0 else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Students", total_students)
    col2.metric("Present", total_present)
    col3.metric("Absent", total_absent)
    col4.metric("Average Attendance", f"{average:.2f}%")

    st.info("Use the sidebar to manage students and attendance.")
