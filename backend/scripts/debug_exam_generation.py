"""
Debug script for exam generation endpoint
"""

from src.database import get_engine
from src.models.subject import Subject
from src.services.exam_generation_service import ExamGenerationService
from sqlmodel import Session, select


def debug_exam_generation():
    """Debug the exam generation functionality"""
    engine = get_engine()

    with Session(engine) as session:
        # Check if subject exists
        subject = session.exec(select(Subject).where(Subject.code == "9708")).first()

        if not subject:
            print("❌ Subject 9708 not found!")
            print("Available subjects:")
            subjects = session.exec(select(Subject)).all()
            for s in subjects:
                print(f"   - {s.code}: {s.name}")
            return

        print(f"✅ Found subject: {subject.name} (ID: {subject.id})")

        # Test ExamGenerationService
        print("\n🔍 Testing ExamGenerationService...")
        try:
            exam_service = ExamGenerationService(session)
            exam = exam_service.generate_exam(
                subject_id=subject.id,
                exam_type="PRACTICE",
                question_count=5,
                strategy="balanced",
            )

            print(f"✅ Exam generation successful!")
            print(f"   Exam ID: {exam.id}")
            print(f"   Questions: {len(exam.question_ids)}")
            print(f"   Total marks: {exam.total_marks}")
            print(f"   Duration: {exam.duration} minutes")
            print(f"   Status: {exam.status}")

        except Exception as e:
            print(f"❌ Exam generation failed with error:")
            print(f"   {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    debug_exam_generation()
