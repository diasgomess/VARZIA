from fastapi import FastAPI

from app.db import Base, engine
from app.routes.matches import router as matches_router


app = FastAPI(title="VARZIA API")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(matches_router)
