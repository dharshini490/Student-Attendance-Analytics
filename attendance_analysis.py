
import csv

# Read attendance data
students = {}

with open("attendance.csv", "r", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        student_id = row["student_id"]
        name = row["name"]
        status = row["status"].strip().upper()

        if student_id not in students:
            students[student_id] = {
                "name": name,
                "present": 0,
                "absent": 0
            }

        if status == "P":
            students[student_id]["present"] += 1
        elif status == "A":
            students[student_id]["absent"] += 1

# Calculate attendance percentage
results = []

for student_id, data in students.items():
    total = data["present"] + data["absent"]

    if total == 0:
        continue

    percentage = (data["present"] / total) * 100

    results.append({
        "student_id": student_id,
        "name": data["name"],
        "total_classes": total,
        "present": data["present"],
        "absent": data["absent"],
        "percentage": round(percentage, 2)
    })

# Display complete report
print("\n===== STUDENT ATTENDANCE REPORT =====")
print("ID    Name     Present  Absent  Attendance")

for student in results:
    print(
        student["student_id"],
        student["name"],
        student["present"],
        student["absent"],
        str(student["percentage"]) + "%"
    )

# Find students below 75%
print("\n===== LOW ATTENDANCE STUDENTS =====")

for student in results:
    if student["percentage"] < 75:
        print(student["name"], "-", student["percentage"], "%")

# Save complete report
with open("attendance_report.csv", "w", newline="") as file:
    fields = [
        "student_id", "name", "total_classes",
        "present", "absent", "percentage"
    ]

    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(results)

print("\nReport saved successfully!")
