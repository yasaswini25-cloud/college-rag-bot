import asyncio
import os
import sys

# Set standard output encoding to utf-8 for Windows PowerShell/CMD
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure server root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.database import engine, Base, AsyncSessionLocal
from app.main import seed_initial_data
from app.services.auth_service import AuthService
from app.services.rag_service import RAGService
from app.services.chat_service import ChatService
from app.services.admin_service import AdminService
from app.models.user import User
from app.models.document import Document
from sqlalchemy import select

async def run_verification():
    print("==================================================")
    print("[*] RUNNING COLLEGE RAG PIPELINE VERIFICATION SUITE")
    print("==================================================")

    # 1. Initialize Tables & Seed Data
    print("\n[Step 1] Initializing Database & Seeding Knowledge Base...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    print("[OK] Database tables and seed data created successfully.")

    async with AsyncSessionLocal() as db:
        # 2. Verify Seed Users & Auth
        print("\n[Step 2] Testing User Authentication & Passwords...")
        admin_res = await AuthService.authenticate_user(db, "admin@college.edu", "admin123")
        assert admin_res["user"]["role"] == "ADMIN"
        assert "token" in admin_res
        print(f"[OK] Admin authenticated successfully: {admin_res['user']['email']}")

        student_res = await AuthService.authenticate_user(db, "student@college.edu", "student123")
        assert student_res["user"]["role"] == "STUDENT"
        assert "token" in student_res
        print(f"[OK] Student authenticated successfully: {student_res['user']['email']}")

        # 3. Verify Documents & Chunks
        print("\n[Step 3] Verifying Ingested College Documents...")
        docs = (await db.execute(select(Document))).scalars().all()
        print(f"[OK] Found {len(docs)} seeded documents in knowledge base:")
        for d in docs:
            print(f"   - {d.title} ({d.category}) - Status: {d.status}, Chunks: {d.total_chunks}")
        assert len(docs) > 0, "No documents were seeded!"

        # 4. Test RAG Query on Attendance Regulations
        print("\n[Step 4] Testing RAG Query: Attendance Regulations...")
        rag = RAGService()
        query1 = "What is the minimum attendance requirement and condonation fee?"
        res1 = await rag.query(db, question=query1)
        print(f"Query: '{query1}'")
        print(f"Answer:\n{res1['answer']}\n")
        print(f"Sources Cited ({len(res1['sources'])}):")
        for s in res1['sources']:
            print(f"   [Doc] {s['documentName']} (Page {s['page']}) - Match: {int(s['similarityScore']*100)}%")
        assert len(res1["sources"]) > 0, "RAG should cite at least one official source!"
        assert "75%" in res1["answer"] or "attendance" in res1["answer"].lower(), "Answer should contain attendance facts!"
        print("[OK] Attendance query passed.")

        # 5. Test RAG Query on Hostel Charges & Curfew
        print("\n[Step 5] Testing RAG Query: Hostel Charges & Curfew...")
        query2 = "What are the hostel room charges and curfew timings?"
        res2 = await rag.query(db, question=query2)
        print(f"Query: '{query2}'")
        print(f"Answer:\n{res2['answer']}\n")
        print(f"Sources Cited ({len(res2['sources'])}):")
        for s in res2['sources']:
            print(f"   [Doc] {s['documentName']} (Page {s['page']}) - Match: {int(s['similarityScore']*100)}%")
        assert len(res2["sources"]) > 0, "Hostel query should return sources."
        print("[OK] Hostel query passed.")

        # 6. Test Unknown Question Handling (Anti-Hallucination Guardrail)
        print("\n[Step 6] Testing Anti-Hallucination Guardrail on Unknown Query...")
        unknown_query = "What is the recipe for baking chocolate chip cookies?"
        res_unknown = await rag.query(db, question=unknown_query)
        print(f"Query: '{unknown_query}'")
        print(f"Output: '{res_unknown['answer']}'")
        print(f"Grounded: {res_unknown['grounded']}, Sources: {len(res_unknown['sources'])}")
        assert "couldn't find reliable information" in res_unknown["answer"].lower() or len(res_unknown["sources"]) == 0
        print("[OK] Anti-hallucination guardrail passed.")

        # 7. Test Admin Analytics
        print("\n[Step 7] Testing Admin Dashboard Metrics...")
        metrics = await AdminService.get_dashboard_metrics(db)
        print(f"[OK] Dashboard metrics: {metrics}")
        assert metrics["totalDocuments"] >= 4
        assert metrics["totalUsers"] >= 2

    print("\n==================================================")
    print("[SUCCESS] ALL VERIFICATION SUITE TESTS PASSED 100%!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
