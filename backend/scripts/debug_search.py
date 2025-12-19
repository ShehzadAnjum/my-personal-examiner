"""
Debug script for search endpoint
"""

from src.database import get_engine
from src.models.subject import Subject
from src.models.question import Question
from src.services.search_service import SearchService
from sqlmodel import Session, select

def debug_search():
    """Debug the search functionality"""
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

        # Check questions
        questions = session.exec(
            select(Question).where(Question.subject_id == subject.id)
        ).all()

        print(f"✅ Found {len(questions)} questions for Economics")

        if not questions:
            print("\n⚠️  No questions found. Run:")
            print("   uv run python scripts/seed_sample_questions.py")
            return

        # Test SearchService
        print("\n🔍 Testing SearchService...")
        try:
            search_service = SearchService(session)
            results = search_service.search_questions(
                subject_code="9708",
                sort_by="year",
                sort_order="desc",
                page=1,
                page_size=20
            )

            print(f"✅ Search successful!")
            print(f"   Total: {results['total']}")
            print(f"   Page: {results['page']}")
            print(f"   Questions returned: {len(results['questions'])}")

            # Print first question
            if results['questions']:
                q = results['questions'][0]
                print(f"\n📝 Sample question:")
                print(f"   ID: {q.get('id')}")
                print(f"   Text: {q.get('question_text', '')[:50]}...")
                print(f"   Marks: {q.get('max_marks')}")
                print(f"   Difficulty: {q.get('difficulty')}")

        except Exception as e:
            print(f"❌ Search failed with error:")
            print(f"   {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_search()
