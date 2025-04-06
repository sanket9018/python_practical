from fastapi.security import OAuth2PasswordBearer
from typing import Optional
import aiomysql
from fastapi import Request

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

ROLE_ADMIN = 1
ROLE_USER = 2

async def get_conn(request: Request):
    async with request.app.state.db.pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            yield conn, cur
