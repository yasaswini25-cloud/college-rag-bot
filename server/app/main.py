import os
import glob
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func
from app.config.settings import settings
from app.config.database import engine, Base, AsyncSessionLocal
from app.models.user import User
from app.models.document import Document
from app.services.auth_service import AuthService
from app.services.document_service import DocumentService
from app.services.processing_service import ProcessingService
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.documents import router as documents_router
from app.routes.rag import router as rag_router
from app.routes.admin import router as admin_router
from app.routes.feedback import router as feedback_router
from app.routes.health import router as health_router

async def seed_initial_data():
    """
    Creates default users and automatically seeds and indexes sample college documents.
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    async with AsyncSessionLocal() as db:
        # 1. Seed Admin User
        admin_stmt = select(User).where(User.email == "admin@college.edu")
        admin_user = (await db.execute(admin_stmt)).scalars().first()
        if not admin_user:
            admin_user = User(
                name="College Administrator",
                email="admin@college.edu",
                password_hash=AuthService.get_password_hash("admin123"),
                role="ADMIN"
            )
            db.add(admin_user)

        # 2. Seed Student User
        student_stmt = select(User).where(User.email == "student@college.edu")
        student_user = (await db.execute(student_stmt)).scalars().first()
        if not student_user:
            student_user = User(
                name="Alex Student",
                email="student@college.edu",
                password_hash=AuthService.get_password_hash("student123"),
                role="STUDENT"
            )
            db.add(student_user)

        await db.commit()
        await db.refresh(admin_user)

        # 3. Seed Sample Documents if knowledge base is empty
        doc_count = (await db.execute(select(func.count(Document.id)))).scalar() or 0
        if doc_count == 0:
            sample_dir = os.path.join(os.path.dirname(__file__), "..", "sample_docs")
            sample_files = glob.glob(os.path.join(sample_dir, "*.txt"))

            meta_mapping = {
                "Academic_Regulations_2026.txt": ("Academic Regulations 2026", "Regulations", "All"),
                "Admission_Guidelines_2026.txt": ("Admission Guidelines 2026", "Admissions", "All"),
                "Hostel_Fee_Structure_2026.txt": ("Hostel & Residence Fee Structure 2026", "Hostel & Fees", "All"),
                "Placement_Policy_2026.txt": ("Placement Policy & Recruitment Rules 2026", "Placements", "All"),
                "Scholarship_And_Library_Policy_2026.txt": ("Library Guidelines & Scholarships 2026", "Library & Scholarships", "All")
            }

            for s_path in sample_files:
                fname = os.path.basename(s_path)
                title, category, dept = meta_mapping.get(fname, (fname, "General", "All"))
                file_size = os.path.getsize(s_path)

                # Copy to upload dir
                dest_path = os.path.join(settings.UPLOAD_DIR, fname)
                with open(s_path, "rb") as src_f, open(dest_path, "wb") as dst_f:
                    dst_f.write(src_f.read())

                doc = Document(
                    title=title,
                    filename=fname,
                    category=category,
                    department=dept,
                    version="2026.1",
                    file_url=dest_path,
                    file_size_bytes=file_size,
                    status="PENDING",
                    uploaded_by=admin_user.id
                )
                db.add(doc)
                await db.commit()
                await db.refresh(doc)

                # Process immediately
                await ProcessingService.process_document(doc.id)

            print("[Seed] Successfully seeded initial users and indexed sample college documents.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables & seed data
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await seed_initial_data()
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-stack AI-Powered College Information Assistant with grounded RAG pipeline.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers under API Prefix
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(chat_router, prefix=settings.API_PREFIX)
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(rag_router, prefix=settings.API_PREFIX)
app.include_router(admin_router, prefix=settings.API_PREFIX)
app.include_router(feedback_router, prefix=settings.API_PREFIX)

# Also expose direct /health for standard health probes
@app.get("/health", tags=["Health"])
async def root_health():
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
