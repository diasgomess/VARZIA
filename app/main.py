from fastapi import FastAPI

from app.api.routes.player_stats import router as player_stats_router

app = FastAPI(title="VARZIA API")
app.include_router(player_stats_router)
