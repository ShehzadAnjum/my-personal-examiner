"""
Seed Sample Economics Questions

Creates sample questions for Economics A-Level (9708).
This is test data for Phase II validation (search, exam generation, etc.).
"""

from src.database import get_engine
from src.models.subject import Subject
from src.models.question import Question
from src.models.syllabus_point import SyllabusPoint
from sqlmodel import Session, select


def seed_sample_questions():
    """Seed Economics 9708 sample questions"""
    engine = get_engine()

    with Session(engine) as session:
        # Get Economics subject
        subject = session.exec(select(Subject).where(Subject.code == "9708")).first()

        if not subject:
            print("❌ Economics subject not found! Run migrations first:")
            print("   uv run alembic upgrade head")
            return

        print(f"✅ Found subject: {subject.name} ({subject.code})\n")

        # Get syllabus points
        sp_1_1 = session.exec(
            select(SyllabusPoint).where(SyllabusPoint.code == "9708.1.1")
        ).first()
        sp_2_1 = session.exec(
            select(SyllabusPoint).where(SyllabusPoint.code == "9708.2.1")
        ).first()
        sp_2_2 = session.exec(
            select(SyllabusPoint).where(SyllabusPoint.code == "9708.2.2")
        ).first()
        sp_3_1 = session.exec(
            select(SyllabusPoint).where(SyllabusPoint.code == "9708.3.1")
        ).first()
        sp_3_2 = session.exec(
            select(SyllabusPoint).where(SyllabusPoint.code == "9708.3.2")
        ).first()

        if not sp_1_1:
            print(
                "⚠️  Syllabus points not found! Run seed_economics_syllabus.py first:"
            )
            print("   uv run python scripts/seed_economics_syllabus.py")
            print("\n   Continuing without syllabus tags...\n")

        questions = [
            # Easy questions (4-8 marks)
            {
                "question_text": "Explain the concept of opportunity cost and provide two examples from your daily life.",
                "max_marks": 8,
                "difficulty": "easy",
                "paper_number": 22,
                "question_number": 1,
                "year": 2022,
                "session": "MAY_JUNE",
                "source_paper": "9708_s22_qp_22",
                "syllabus_point_ids": [str(sp_1_1.id)] if sp_1_1 else [],
            },
            {
                "question_text": "Define scarcity and explain why it is the central economic problem.",
                "max_marks": 4,
                "difficulty": "easy",
                "paper_number": 22,
                "question_number": 4,
                "year": 2021,
                "session": "OCT_NOV",
                "source_paper": "9708_w21_qp_22",
                "syllabus_point_ids": [str(sp_1_1.id)] if sp_1_1 else [],
            },
            {
                "question_text": "State two characteristics of a free market economy.",
                "max_marks": 4,
                "difficulty": "easy",
                "paper_number": 31,
                "question_number": 1,
                "year": 2022,
                "session": "MAY_JUNE",
                "source_paper": "9708_s22_qp_31",
                "syllabus_point_ids": [],
            },
            # Medium questions (8-12 marks)
            {
                "question_text": "Using a demand and supply diagram, explain how a government subsidy affects market equilibrium.",
                "max_marks": 12,
                "difficulty": "medium",
                "paper_number": 22,
                "question_number": 2,
                "year": 2022,
                "session": "MAY_JUNE",
                "source_paper": "9708_s22_qp_22",
                "syllabus_point_ids": [str(sp_2_1.id), str(sp_3_2.id)]
                if (sp_2_1 and sp_3_2)
                else [],
            },
            {
                "question_text": "Calculate the price elasticity of demand if price increases from $10 to $12 and quantity demanded falls from 100 to 80 units. Interpret your result.",
                "max_marks": 10,
                "difficulty": "medium",
                "paper_number": 22,
                "question_number": 5,
                "year": 2021,
                "session": "OCT_NOV",
                "source_paper": "9708_w21_qp_22",
                "syllabus_point_ids": [str(sp_2_2.id)] if sp_2_2 else [],
            },
            {
                "question_text": "Explain two reasons why a government might impose a maximum price on a good.",
                "max_marks": 8,
                "difficulty": "medium",
                "paper_number": 31,
                "question_number": 3,
                "year": 2022,
                "session": "MAY_JUNE",
                "source_paper": "9708_s22_qp_31",
                "syllabus_point_ids": [str(sp_3_2.id)] if sp_3_2 else [],
            },
            {
                "question_text": "Using a diagram, explain the difference between a movement along a demand curve and a shift of the demand curve.",
                "max_marks": 10,
                "difficulty": "medium",
                "paper_number": 22,
                "question_number": 6,
                "year": 2020,
                "session": "MAY_JUNE",
                "source_paper": "9708_s20_qp_22",
                "syllabus_point_ids": [str(sp_2_1.id)] if sp_2_1 else [],
            },
            # Hard questions (15-20 marks)
            {
                "question_text": "Discuss whether government intervention is necessary to address negative externalities. Use real-world examples.",
                "max_marks": 20,
                "difficulty": "hard",
                "paper_number": 22,
                "question_number": 3,
                "year": 2022,
                "session": "MAY_JUNE",
                "source_paper": "9708_s22_qp_22",
                "syllabus_point_ids": [str(sp_3_1.id), str(sp_3_2.id)]
                if (sp_3_1 and sp_3_2)
                else [],
            },
            {
                "question_text": "Evaluate the effectiveness of indirect taxes as a method of reducing the consumption of demerit goods.",
                "max_marks": 15,
                "difficulty": "hard",
                "paper_number": 22,
                "question_number": 7,
                "year": 2021,
                "session": "OCT_NOV",
                "source_paper": "9708_w21_qp_22",
                "syllabus_point_ids": [str(sp_3_2.id)] if sp_3_2 else [],
            },
            {
                "question_text": "To what extent can price elasticity of demand help a government in deciding whether to impose a tax on a good?",
                "max_marks": 20,
                "difficulty": "hard",
                "paper_number": 31,
                "question_number": 5,
                "year": 2022,
                "session": "MAY_JUNE",
                "source_paper": "9708_s22_qp_31",
                "syllabus_point_ids": [str(sp_2_2.id), str(sp_3_2.id)]
                if (sp_2_2 and sp_3_2)
                else [],
            },
        ]

        created_count = 0

        for q_data in questions:
            q = Question(subject_id=subject.id, **q_data)
            session.add(q)
            print(
                f"✅ Created: {q.source_paper} Q{q.question_number} ({q.max_marks} marks, {q.difficulty})"
            )
            created_count += 1

        session.commit()

        print(f"\n📊 Summary:")
        print(f"   Total questions created: {created_count}")
        print(f"   Easy: {sum(1 for q in questions if q['difficulty'] == 'easy')}")
        print(
            f"   Medium: {sum(1 for q in questions if q['difficulty'] == 'medium')}"
        )
        print(f"   Hard: {sum(1 for q in questions if q['difficulty'] == 'hard')}")
        print(f"\n✅ Sample questions seeded successfully!")


if __name__ == "__main__":
    seed_sample_questions()
