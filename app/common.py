from fastapi import HTTPException


def success_response(data, message="Success") -> dict:
    """
    Returns a standardized success response for API endpoints.
    """
    return {"success": True, "message": message, "data": data}

def error_response(message="Something went wrong", status_code=400) -> None:
    """
        Raises a standardized HTTP exception to be returned as an error response.
    """
    raise HTTPException(status_code=status_code, detail=message)

