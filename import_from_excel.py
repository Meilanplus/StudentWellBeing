"""Import student data from Roles_task_data.xlsx"""
import openpyxl
from datetime import date
from app.main import app
from app.database import SessionLocal
from app.models.student import Student
from app.models.assessment import AssessmentResult

# Read Excel file
wb = openpyxl.load_workbook('Roles_task_data.xlsx')
ws = wb.active

db = SessionLocal()
created_count = 0
try:
    # Extract students from Excel
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 1):
        if row[0] is None:
            continue
            
        student_ic = str(int(row[0])).zfill(12)
        class_name = row[1]
        full_name = row[2]
        
        # Check if student already exists
        existing = db.query(Student).filter(Student.student_id == student_ic).first()
        if existing:
            print(f"Student {student_ic} already exists, skipping...")
            continue
        
        # Create student with default values for missing fields
        student = Student(
            student_id=student_ic,
            full_name=full_name,
            date_of_birth=date(2008, 1, 1),  # Default DOB
            gender="Unknown",  # Unknown since not in Excel
            class_name=class_name,
            school_year=2026,
            school_id=1,  # Default to SK La Salle
            socioeconomic_status="unknown"
        )
        db.add(student)
        db.flush()  # Get the student ID
        
        # Create assessment result with the Saringan Minda Sihat scores
        # Assessment ID 2 is Saringan Minda Sihat
        assessment_result = AssessmentResult(
            student_id=student.id,
            assessment_id=2,  # Saringan Minda Sihat
            administered_date=date.today(),
            raw_score=float(row[8]) if row[8] and not isinstance(row[8], str) else 0,  # Total Score
            responses={
                "emosi_diri": row[3],  # Emotional Self
                "hubungan_sosial": row[4],  # Social Relationships
                "tingkah_laku": row[5],  # Behavior
                "konsep_kendiri": row[6],  # Self-Concept
                "tekanan_kebimbangan": row[7],  # Stress & Anxiety
            },
            administered_by="import_script"
        )
        db.add(assessment_result)
        created_count += 1
        print(f"✓ Created student: {full_name} (IC: {student_ic}) - Class: {class_name}")
    
    db.commit()
    print(f"\n✅ Successfully imported {created_count} students with assessment data!")
    
finally:
    db.close()
