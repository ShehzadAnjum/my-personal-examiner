"""
Seed Economics 9708 Syllabus Points

Creates sample syllabus points for Economics A-Level (9708).
This is test data for Phase II validation.
"""

from src.database import get_engine
from src.models.subject import Subject
from src.models.syllabus_point import SyllabusPoint
from sqlmodel import Session, select


def seed_economics_syllabus():
    """Seed Economics 9708 syllabus points"""
    engine = get_engine()

    with Session(engine) as session:
        # Get Economics subject
        subject = session.exec(select(Subject).where(Subject.code == "9708")).first()

        if not subject:
            print("❌ Economics subject not found! Run migrations first:")
            print("   uv run alembic upgrade head")
            return

        print(f"✅ Found subject: {subject.name} ({subject.code})\n")

        syllabus_points = [
            {
                "code": "9708.1.1",
                "description": "The central economic problem",
                "topics": "Scarcity, Choice, Opportunity cost",
                "learning_outcomes": "Understand the nature of the economic problem",
            },
            {
                "code": "9708.1.2",
                "description": "The role of markets",
                "topics": "Free market economy, Mixed economy, Command economy",
                "learning_outcomes": "Understand different economic systems",
            },
            {
                "code": "9708.2.1",
                "description": "Supply and demand",
                "topics": "Demand curves, Supply curves, Market equilibrium",
                "learning_outcomes": "Analyze market mechanisms",
            },
            {
                "code": "9708.2.2",
                "description": "Price elasticity",
                "topics": "PED, PES, Income elasticity, Cross elasticity",
                "learning_outcomes": "Calculate and interpret elasticity",
            },
            {
                "code": "9708.3.1",
                "description": "Market failure",
                "topics": "Externalities, Public goods, Merit goods, Information failure",
                "learning_outcomes": "Identify and analyze market failures",
            },
            {
                "code": "9708.3.2",
                "description": "Government intervention",
                "topics": "Taxes, Subsidies, Price controls, Regulation",
                "learning_outcomes": "Evaluate government policies",
            },
            {
                "code": "9708.4.1",
                "description": "Macroeconomic objectives",
                "topics": "Economic growth, Inflation, Unemployment, Balance of payments",
                "learning_outcomes": "Understand macroeconomic goals",
            },
            {
                "code": "9708.4.2",
                "description": "Aggregate demand and supply",
                "topics": "AD curve, AS curve, Macroeconomic equilibrium",
                "learning_outcomes": "Analyze macroeconomic models",
            },
            {
                "code": "9708.5.1",
                "description": "Fiscal policy",
                "topics": "Government spending, Taxation, Budget deficit/surplus",
                "learning_outcomes": "Evaluate fiscal policy effectiveness",
            },
            {
                "code": "9708.5.2",
                "description": "Monetary policy",
                "topics": "Interest rates, Money supply, Central bank operations",
                "learning_outcomes": "Evaluate monetary policy effectiveness",
            },
        ]

        created_count = 0
        existing_count = 0

        for sp_data in syllabus_points:
            # Check if already exists
            existing = session.exec(
                select(SyllabusPoint).where(SyllabusPoint.code == sp_data["code"])
            ).first()

            if not existing:
                sp = SyllabusPoint(subject_id=subject.id, **sp_data)
                session.add(sp)
                print(f"✅ Created: {sp.code} - {sp.description}")
                created_count += 1
            else:
                print(f"⏭️  Already exists: {sp_data['code']}")
                existing_count += 1

        session.commit()

        print(f"\n📊 Summary:")
        print(f"   Created: {created_count}")
        print(f"   Already existed: {existing_count}")
        print(f"   Total: {created_count + existing_count}")
        print(f"\n✅ Economics syllabus seeded successfully!")


if __name__ == "__main__":
    seed_economics_syllabus()
