from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Optional
import aiomysql
import os
from dotenv import load_dotenv
load_dotenv()



from app.routes import user_router

ALLOWED_ORIGINS = ["*"]

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "mysql_db"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "Admin@123"),
    "db": os.getenv("MYSQL_DATABASE", "FastAPIPractical"),
}


class DB:
    pool: Optional[aiomysql.Pool] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Establishes and closes DB connection pool
    """
    app.state.db = DB()
    app.state.db.pool = await aiomysql.create_pool(**DB_CONFIG)
    yield
    app.state.db.pool.close()
    await app.state.db.pool.wait_closed()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# user routes
app.include_router(user_router)

os.makedirs("uploads", exist_ok=True)

#static files configuration
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
