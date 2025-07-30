#!/usr/bin/env python3
"""
Database seeding script for Hospital Management System
Run this to populate the database with sample data for demo purposes.
"""

import asyncio
from datetime import date, time, datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

from models import Base, User, Patient, Doctor, Appointment, MedicalRecord, Department, UserRole, AppointmentStatus
from auth import get_password_hash
import uuid

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://hospital_user:hospital_pass@localhost:5432/hospital_db")

def create_sample_data():
    """Create sample data for the hospital management system."""
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            print("Sample data already exists. Skipping...")
            return
        
        print("Creating sample data...")
        
        # Create admin user
        admin_user = User(
            email="admin@hospital.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            first_name="Hospital",
            last_name="Administrator",
            phone="+1234567890",
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        
        # Create sample doctors
        doctors_data = [
            {
                "user": {
                    "email": "john.smith@hospital.com",
                    "username": "doctor1",
                    "password": "doctor123",
                    "first_name": "John",
                    "last_name": "Smith",
                    "phone": "+1234567891"
                },
                "doctor_id": "DOC001",
                "specialization": "Cardiology",
                "qualification": "MD, FACC",
                "experience_years": 15,
                "license_number": "LIC001",
                "consultation_fee": 200.00,
                "available_days": "Monday,Tuesday,Wednesday,Thursday,Friday",
                "available_hours_start": time(9, 0),
                "available_hours_end": time(17, 0)
            },
            {
                "user": {
                    "email": "sarah.johnson@hospital.com",
                    "username": "doctor2",
                    "password": "doctor123",
                    "first_name": "Sarah",
                    "last_name": "Johnson",
                    "phone": "+1234567892"
                },
                "doctor_id": "DOC002",
                "specialization": "Pediatrics",
                "qualification": "MD, FAAP",
                "experience_years": 12,
                "license_number": "LIC002",
                "consultation_fee": 180.00,
                "available_days": "Monday,Tuesday,Wednesday,Thursday,Friday",
                "available_hours_start": time(8, 0),
                "available_hours_end": time(16, 0)
            },
            {
                "user": {
                    "email": "michael.brown@hospital.com",
                    "username": "doctor3",
                    "password": "doctor123",
                    "first_name": "Michael",
                    "last_name": "Brown",
                    "phone": "+1234567893"
                },
                "doctor_id": "DOC003",
                "specialization": "Orthopedics",
                "qualification": "MD, FAAOS",
                "experience_years": 18,
                "license_number": "LIC003",
                "consultation_fee": 250.00,
                "available_days": "Monday,Wednesday,Friday",
                "available_hours_start": time(10, 0),
                "available_hours_end": time(18, 0)
            }
        ]
        
        created_doctors = []
        for doctor_data in doctors_data:
            # Create doctor user
            doctor_user = User(
                email=doctor_data["user"]["email"],
                username=doctor_data["user"]["username"],
                hashed_password=get_password_hash(doctor_data["user"]["password"]),
                first_name=doctor_data["user"]["first_name"],
                last_name=doctor_data["user"]["last_name"],
                phone=doctor_data["user"]["phone"],
                role=UserRole.DOCTOR
            )
            db.add(doctor_user)
            db.flush()  # Get the ID
            
            # Create doctor profile
            doctor = Doctor(
                user_id=doctor_user.id,
                doctor_id=doctor_data["doctor_id"],
                specialization=doctor_data["specialization"],
                qualification=doctor_data["qualification"],
                experience_years=doctor_data["experience_years"],
                license_number=doctor_data["license_number"],
                consultation_fee=doctor_data["consultation_fee"],
                available_days=doctor_data["available_days"],
                available_hours_start=doctor_data["available_hours_start"],
                available_hours_end=doctor_data["available_hours_end"]
            )
            db.add(doctor)
            created_doctors.append(doctor)
        
        # Create sample patients
        patients_data = [
            {
                "user": {
                    "email": "alice.wilson@email.com",
                    "username": "patient1",
                    "password": "patient123",
                    "first_name": "Alice",
                    "last_name": "Wilson",
                    "phone": "+1234567894"
                },
                "patient_id": "PAT001",
                "date_of_birth": date(1985, 3, 15),
                "gender": "Female",
                "address": "123 Main St, City, State 12345",
                "emergency_contact_name": "Bob Wilson",
                "emergency_contact_phone": "+1234567895",
                "blood_group": "A+",
                "allergies": "Penicillin",
                "medical_history": "Hypertension, managed with medication"
            },
            {
                "user": {
                    "email": "david.lee@email.com",
                    "username": "patient2",
                    "password": "patient123",
                    "first_name": "David",
                    "last_name": "Lee",
                    "phone": "+1234567896"
                },
                "patient_id": "PAT002",
                "date_of_birth": date(1978, 7, 22),
                "gender": "Male",
                "address": "456 Oak Ave, City, State 12345",
                "emergency_contact_name": "Susan Lee",
                "emergency_contact_phone": "+1234567897",
                "blood_group": "O-",
                "allergies": "None",
                "medical_history": "Diabetes Type 2, well controlled"
            },
            {
                "user": {
                    "email": "emma.davis@email.com",
                    "username": "patient3",
                    "password": "patient123",
                    "first_name": "Emma",
                    "last_name": "Davis",
                    "phone": "+1234567898"
                },
                "patient_id": "PAT003",
                "date_of_birth": date(1992, 11, 8),
                "gender": "Female",
                "address": "789 Pine St, City, State 12345",
                "emergency_contact_name": "James Davis",
                "emergency_contact_phone": "+1234567899",
                "blood_group": "B+",
                "allergies": "Shellfish",
                "medical_history": "No significant medical history"
            }
        ]
        
        created_patients = []
        for patient_data in patients_data:
            # Create patient user
            patient_user = User(
                email=patient_data["user"]["email"],
                username=patient_data["user"]["username"],
                hashed_password=get_password_hash(patient_data["user"]["password"]),
                first_name=patient_data["user"]["first_name"],
                last_name=patient_data["user"]["last_name"],
                phone=patient_data["user"]["phone"],
                role=UserRole.PATIENT
            )
            db.add(patient_user)
            db.flush()  # Get the ID
            
            # Create patient profile
            patient = Patient(
                user_id=patient_user.id,
                patient_id=patient_data["patient_id"],
                date_of_birth=patient_data["date_of_birth"],
                gender=patient_data["gender"],
                address=patient_data["address"],
                emergency_contact_name=patient_data["emergency_contact_name"],
                emergency_contact_phone=patient_data["emergency_contact_phone"],
                blood_group=patient_data["blood_group"],
                allergies=patient_data["allergies"],
                medical_history=patient_data["medical_history"]
            )
            db.add(patient)
            created_patients.append(patient)
        
        # Create nurse user
        nurse_user = User(
            email="nurse@hospital.com",
            username="nurse1",
            hashed_password=get_password_hash("nurse123"),
            first_name="Nancy",
            last_name="Williams",
            phone="+1234567880",
            role=UserRole.NURSE
        )
        db.add(nurse_user)
        
        # Create receptionist user
        receptionist_user = User(
            email="reception@hospital.com",
            username="reception1",
            hashed_password=get_password_hash("reception123"),
            first_name="Rachel",
            last_name="Green",
            phone="+1234567881",
            role=UserRole.RECEPTIONIST
        )
        db.add(receptionist_user)
        
        # Commit users and profiles first
        db.commit()
        db.refresh(admin_user)
        for doctor in created_doctors:
            db.refresh(doctor)
        for patient in created_patients:
            db.refresh(patient)
        
        # Create departments
        departments_data = [
            {
                "name": "Cardiology",
                "description": "Heart and cardiovascular system",
                "head_doctor_id": created_doctors[0].id,
                "location": "Building A, Floor 2",
                "phone": "+1234567870"
            },
            {
                "name": "Pediatrics",
                "description": "Children's healthcare",
                "head_doctor_id": created_doctors[1].id,
                "location": "Building B, Floor 1",
                "phone": "+1234567871"
            },
            {
                "name": "Orthopedics",
                "description": "Bone and joint care",
                "head_doctor_id": created_doctors[2].id,
                "location": "Building A, Floor 3",
                "phone": "+1234567872"
            }
        ]
        
        for dept_data in departments_data:
            department = Department(**dept_data)
            db.add(department)
        
        # Create sample appointments
        today = date.today()
        appointments_data = [
            {
                "patient_id": created_patients[0].id,
                "doctor_id": created_doctors[0].id,
                "appointment_date": today + timedelta(days=1),
                "appointment_time": time(10, 0),
                "reason": "Regular checkup",
                "status": AppointmentStatus.SCHEDULED
            },
            {
                "patient_id": created_patients[1].id,
                "doctor_id": created_doctors[1].id,
                "appointment_date": today,
                "appointment_time": time(14, 0),
                "reason": "Follow-up consultation",
                "status": AppointmentStatus.CONFIRMED
            },
            {
                "patient_id": created_patients[2].id,
                "doctor_id": created_doctors[2].id,
                "appointment_date": today + timedelta(days=2),
                "appointment_time": time(11, 30),
                "reason": "Knee pain evaluation",
                "status": AppointmentStatus.SCHEDULED
            },
            {
                "patient_id": created_patients[0].id,
                "doctor_id": created_doctors[0].id,
                "appointment_date": today - timedelta(days=7),
                "appointment_time": time(9, 30),
                "reason": "Annual physical",
                "status": AppointmentStatus.COMPLETED
            }
        ]
        
        created_appointments = []
        for apt_data in appointments_data:
            appointment = Appointment(
                appointment_id=f"APT-{str(uuid.uuid4())[:8].upper()}",
                **apt_data
            )
            db.add(appointment)
            created_appointments.append(appointment)
        
        db.commit()
        for appointment in created_appointments:
            db.refresh(appointment)
        
        # Create sample medical records
        medical_records_data = [
            {
                "patient_id": created_patients[0].id,
                "doctor_id": created_doctors[0].id,
                "appointment_id": created_appointments[3].id,  # Completed appointment
                "visit_date": datetime.now() - timedelta(days=7),
                "chief_complaint": "Chest discomfort and shortness of breath",
                "diagnosis": "Mild hypertension, stress-related anxiety",
                "treatment": "Lifestyle modifications, stress management techniques",
                "prescription": "Lisinopril 10mg daily, follow-up in 3 months",
                "vital_signs": '{"blood_pressure": "140/90", "heart_rate": "78", "temperature": "98.6", "weight": "70kg"}',
                "notes": "Patient advised to reduce sodium intake and increase physical activity"
            },
            {
                "patient_id": created_patients[1].id,
                "doctor_id": created_doctors[1].id,
                "visit_date": datetime.now() - timedelta(days=14),
                "chief_complaint": "Routine diabetes management",
                "diagnosis": "Type 2 Diabetes Mellitus, well controlled",
                "treatment": "Continue current medication regimen",
                "prescription": "Metformin 500mg twice daily, continue current dosage",
                "vital_signs": '{"blood_pressure": "125/80", "heart_rate": "72", "temperature": "98.4", "weight": "80kg", "blood_glucose": "120mg/dl"}',
                "notes": "HbA1c levels within target range. Continue current management plan."
            }
        ]
        
        for record_data in medical_records_data:
            medical_record = MedicalRecord(
                record_id=f"MR-{str(uuid.uuid4())[:8].upper()}",
                **record_data
            )
            db.add(medical_record)
        
        db.commit()
        
        print("✅ Sample data created successfully!")
        print("\n📋 Demo Credentials:")
        print("Admin: admin / admin123")
        print("Doctor: doctor1 / doctor123")
        print("Patient: patient1 / patient123")
        print("Nurse: nurse1 / nurse123")
        print("Receptionist: reception1 / reception123")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()