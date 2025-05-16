from fastapi import FastAPI
from database import Base, engine
from routers import user, appointment, availability,search, documents, prescription, review, medicine
from routers import admin
from routers import auth_routes
from routers import document_rag



Base.metadata.create_all(bind=engine)

app = FastAPI(title="Online Patient Doctor Management System",)

app.include_router(user.router)
app.include_router(auth_routes.router)
app.include_router(admin.router)
app.include_router(availability.router)
app.include_router(search.router)
app.include_router(appointment.router)
app.include_router(documents.router)
app.include_router(prescription.router)
app.include_router(review.router)
app.include_router(medicine.router)
app.include_router(document_rag.router)
