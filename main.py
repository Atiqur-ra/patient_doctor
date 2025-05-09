from fastapi import FastAPI
from database import Base, engine
from routers import user, appointment, availability,search, documents, prescription, review

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router)
app.include_router(availability.router)
app.include_router(search.router)
app.include_router(appointment.router)
app.include_router(documents.router)
app.include_router(prescription.router, prefix="/api", tags=["Prescriptions"])
app.include_router(review.router)