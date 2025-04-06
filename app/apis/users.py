from fastapi import Depends, APIRouter
from app.schema.user_schema import  UserResponse, LoginRequest, Token, SuccessUserResponse
from app.dependencies import get_conn, oauth2_scheme, ROLE_ADMIN  
from app.utils import hash_password, verify_password, get_user_by_token, format_user
from app.common import success_response, error_response
from datetime import datetime
import uuid
from app.utils import create_access_token
from pydantic import  EmailStr
from fastapi import File, Form, UploadFile
from typing import Optional
from fastapi import UploadFile, File, Form
from dotenv import load_dotenv 
import os
from pymysql.err import IntegrityError
import logging
import os


load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/users", response_model=UserResponse)
async def create_user(
    name: str = Form(...),
    cellnumber: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    roleId: int = Form(...),
    profilepic: UploadFile = File(...),
    conn_cur=Depends(get_conn)
):
    """Create a new user."""
    conn, cur = conn_cur

    # Save profile pic to disk
    pic_filename = f"{uuid.uuid4()}_{profilepic.filename}"
    upload_path = os.path.join("uploads", pic_filename)
    try:
        content = await profilepic.read()
        with open(upload_path, "wb") as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to save profile picture: {e}")
        return error_response("Failed to upload profile picture", 500)

    hashed_pwd = hash_password(password)
    now = datetime.now()

    try:
        await cur.execute("""
            INSERT INTO user (profilepic, name, cellnumber, password, email, roleId, created, modified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (upload_path, name, cellnumber, hashed_pwd, email, roleId, now, now))
        await conn.commit()

    except IntegrityError as e:
        await conn.rollback()
        error_msg = str(e)

        if "cellnumber" in error_msg:
            return error_response("A user with this phone number already exists.", 409)
        elif "email" in error_msg:
            return error_response("A user with this email address already exists.", 409)
        else:
            logger.error(f"Integrity error: {error_msg}")
            return error_response("A database integrity error occurred.", 500)

    except Exception as e:
        await conn.rollback()
        logger.exception("Unexpected error while creating user.")
        return error_response("An unexpected error occurred. Please try again later.", 500)

    return success_response({
        "id": cur.lastrowid,
        "name": name,
        "cellnumber": cellnumber,
        "email": email,
        "profilepic": f"{BASE_URL}/{upload_path}",
        "roleId": roleId,
        "created": now,
        "modified": now
    }, message="User created successfully.")



@router.post("/users/login", response_model=Token)
async def login_user(credentials: LoginRequest, conn_cur=Depends(get_conn)):
    conn, cur = conn_cur
    await cur.execute("SELECT * FROM user WHERE cellnumber=%s", (credentials.cellnumber,))
    user = await cur.fetchone()
    
    if not user or not verify_password(credentials.password, user['password']):
        return error_response("Invalid credentials", 401)

    access_token, ttl = create_access_token(data={"user_id": user['id']})
    now = datetime.now()

    await cur.execute(
        "INSERT INTO accesstoken (token, ttl, userId, created) VALUES (%s, %s, %s, %s)",
        (access_token, ttl, user['id'], now)
    )
    await conn.commit()

    return Token(token=access_token, ttl=ttl, userId=user['id'], created=now)


@router.get("/users/{id}", response_model=SuccessUserResponse)
async def get_user(id: int, token: str = Depends(oauth2_scheme), conn_cur=Depends(get_conn)):
    """Fetch a specific user's details. Admins or the user themself can access."""

    conn, cur = conn_cur
    user = await get_user_by_token(token, conn, cur)
    if user['roleId'] != ROLE_ADMIN and user['id'] != id:
        return error_response("Access denied", 403)

    await cur.execute("SELECT * FROM user WHERE id=%s AND deletedAt IS NULL", (id,))
    result = await cur.fetchone()

    if result is None:
        return error_response("User not found", 404)

    return success_response(result)


@router.patch("/users/{id}")
async def update_user(
    id: int,
    token: str = Depends(oauth2_scheme),
    profilepic: Optional[UploadFile] = File(None),
    name: Optional[str] = Form(None),
    cellnumber: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    email: Optional[EmailStr] = Form(None),
    roleId: Optional[int] = Form(None),
    conn_cur=Depends(get_conn),
):
    """Partially update an existing user's data. Admin only."""

    conn, cur = conn_cur
    user = await get_user_by_token(token, conn, cur)

    if not user:
        return error_response("Invalid or expired token", 401)

    if user["roleId"] != ROLE_ADMIN:
        return error_response("Only admin can update users", 403)


    await cur.execute("SELECT * FROM user WHERE id=%s AND deletedAt IS NULL", (id,))
    existing = await cur.fetchone()
    if not existing:
        return error_response("User not found", 404)

    update_fields = []
    update_values = []

    if profilepic:
        
        content = await profilepic.read()
        filename = f"profile_{id}_{datetime.utcnow().timestamp()}.{profilepic.filename.split('.')[-1]}"
        with open(f"uploads/{filename}", "wb") as f:
            f.write(content)
        update_fields.append("profilepic = %s")
        update_values.append(filename)

    if name:
        update_fields.append("name = %s")
        update_values.append(name)

    if cellnumber:
        update_fields.append("cellnumber = %s")
        update_values.append(cellnumber)

    if password:
        update_fields.append("password = %s")
        update_values.append(hash_password(password))

    if email:
        update_fields.append("email = %s")
        update_values.append(email)

    if roleId is not None:
        update_fields.append("roleId = %s")
        update_values.append(roleId)

    if not update_fields:
        return error_response("No fields provided for update", 400)

    update_values.append(datetime.now())
    update_values.append(id)

    query = f"""
        UPDATE user
        SET {', '.join(update_fields)}, modified = %s
        WHERE id = %s
    """
    await cur.execute(query, tuple(update_values))
    await conn.commit()

    return success_response({}, "User updated successfully")



@router.delete("/users/{id}")
async def delete_user(id: int, token: str = Depends(oauth2_scheme), conn_cur=Depends(get_conn)):
    """Soft delete a user. Admin only."""

    conn, cur = conn_cur
    user = await get_user_by_token(token, conn, cur)

    if user['roleId'] != ROLE_ADMIN:
        return error_response("Only admin can delete users", 403)

    await cur.execute("SELECT * FROM user WHERE id=%s AND deletedAt IS NULL", (id,))
    existing = await cur.fetchone()
    if not existing:
        return error_response("User not found", 404)

    await cur.execute("UPDATE user SET deletedAt=%s WHERE id=%s", (datetime.now(), id))
    await conn.commit()

    return success_response({}, "User soft-deleted")


@router.get("/users")
async def list_users(token: str = Depends(oauth2_scheme), conn_cur=Depends(get_conn)):
    """List all users. Admin only."""
    conn, cur = conn_cur

    user = await get_user_by_token(token, conn, cur)
    
    if not user:
        return error_response("Invalid or expired token", 401)

    if user['roleId'] != ROLE_ADMIN:
        return error_response("Only admin can list users", 403)

    await cur.execute("SELECT * FROM user WHERE deletedAt IS NULL")
    users = await cur.fetchall()

    # Optional: format users before returning (e.g., full profilepic URLs)
    formatted_users = [format_user(dict(u)) for u in users]

    return success_response(formatted_users)
