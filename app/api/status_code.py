from typing import Optional, Any, Dict
from pydantic import BaseModel
from fastapi import status, HTTPException

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

class SuccessMessage:
    # Auth
    USER_REGISTERED = "User registered successfully"
    LOGIN_SUCCESS = "Login successful"
    LOGOUT_SUCCESS = "Logout successful"
    TOKEN_REFRESHED = "Token refreshed successfully"
    
    # User
    USER_CREATED = "User created successfully"
    USER_UPDATED = "User updated successfully"
    USER_DELETED = "User deleted successfully"
    USER_RETRIEVED = "User retrieved successfully"
    
    # Report
    REPORT_CREATED = "Report created successfully"
    REPORT_UPDATED = "Report updated successfully"
    REPORT_DELETED = "Report deleted successfully"
    REPORT_RETRIEVED = "Report retrieved successfully"
    REPORTS_RETRIEVED = "Reports retrieved successfully"
    
    # Verification
    VERIFICATION_CREATED = "Verification created successfully"
    VERIFICATION_UPDATED = "Verification updated successfully"
    VERIFICATION_RETRIEVED = "Verification retrieved successfully"
    VERIFICATION_DELETED = "Verification deleted successfully"
    
    # Location
    LOCATION_CREATED = "Location created successfully"
    LOCATION_UPDATED = "Location updated successfully"
    LOCATION_RETRIEVED = "Location retrieved successfully"
    LOCATION_DELETED = "Location deleted successfully"
    
    # Media
    MEDIA_UPLOADED = "Media uploaded successfully"
    MEDIA_DELETED = "Media deleted successfully"

# Error Messages & Codes
class ErrorMessage:
    def __init__(self):
        pass

    # Auth Errors
    EMAIL_EXISTS = {
        "code": "EMAIL_EXISTS",
        "message": "Email is already registered",
        "status_code": status.HTTP_400_BAD_REQUEST
    }
    INVALID_CREDENTIALS = {
        "code": "INVALID_CREDENTIALS",
        "message": "Invalid email or password",
        "status_code": status.HTTP_401_UNAUTHORIZED
    }
    TOKEN_EXPIRED = {
        "code": "TOKEN_EXPIRED",
        "message": "Token has expired",
        "status_code": status.HTTP_401_UNAUTHORIZED
    }
    TOKEN_INVALID = {
        "code": "TOKEN_INVALID",
        "message": "Invalid token",
        "status_code": status.HTTP_401_UNAUTHORIZED
    }
    UNAUTHORIZED = {
        "code": "UNAUTHORIZED",
        "message": "Unauthorized access",
        "status_code": status.HTTP_401_UNAUTHORIZED
    }
    FORBIDDEN = {
        "code": "FORBIDDEN",
        "message": "Access forbidden",
        "status_code": status.HTTP_403_FORBIDDEN
    }
    
    # User Errors
    USER_NOT_FOUND = {
        "code": "USER_NOT_FOUND",
        "message": "User not found",
        "status_code": status.HTTP_404_NOT_FOUND
    }
    USER_CREATION_FAILED = {
        "code": "USER_CREATION_FAILED",
        "message": "Failed to create user",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    
    # Report Errors
    REPORT_NOT_FOUND = {
        "code": "REPORT_NOT_FOUND",
        "message": "Report not found",
        "status_code": status.HTTP_404_NOT_FOUND
    }
    REPORT_CREATION_FAILED = {
        "code": "REPORT_CREATION_FAILED",
        "message": "Failed to create report",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    
    # Validation Errors
    VALIDATION_ERROR = {
        "code": "VALIDATION_ERROR",
        "message": "Validation error",
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
    }
    MISSING_REQUIRED_FIELD = {
        "code": "MISSING_REQUIRED_FIELD",
        "message": "Required field is missing",
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
    }
    INVALID_FORMAT = {
        "code": "INVALID_FORMAT",
        "message": "Invalid data format",
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
    }
    
    # Database Errors
    DB_CONNECTION_ERROR = {
        "code": "DB_CONNECTION_ERROR",
        "message": "Database connection error",
        "status_code": status.HTTP_503_SERVICE_UNAVAILABLE
    }
    DB_OPERATION_FAILED = {
        "code": "DB_OPERATION_FAILED",
        "message": "Database operation failed",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    
    # Media Errors
    MEDIA_UPLOAD_FAILED = {
        "code": "MEDIA_UPLOAD_FAILED",
        "message": "Failed to upload media",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
    }
    MEDIA_NOT_FOUND = {
        "code": "MEDIA_NOT_FOUND",
        "message": "Media not found",
        "status_code": status.HTTP_404_NOT_FOUND
    }
    INVALID_FILE_TYPE = {
        "code": "INVALID_FILE_TYPE",
        "message": "Invalid file type",
        "status_code": status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    }
    FILE_TOO_LARGE = {
        "code": "FILE_TOO_LARGE",
        "message": "File size exceeds limit",
        "status_code": status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    }
    
    @classmethod
    def raise_exception(
        cls,
        error_type: Dict[str, Any],
        details: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        error_detail = {
            "success": False,
            "message": error_type['message'],
            "error": {"code": error_type['code']}
        }
        if details:
            error_detail['error']['details'] = details
        
        raise HTTPException(
            status_code=error_type['status_code'],
            detail=error_detail,
            headers=headers
        )

# HTTP Status Codes
class HTTPStatus:
    # Success
    OK = status.HTTP_200_OK
    CREATED = status.HTTP_201_CREATED
    ACCEPTED = status.HTTP_202_ACCEPTED
    NO_CONTENT = status.HTTP_204_NO_CONTENT
    
    # Client Errors
    BAD_REQUEST = status.HTTP_400_BAD_REQUEST
    UNAUTHORIZED = status.HTTP_401_UNAUTHORIZED
    FORBIDDEN = status.HTTP_403_FORBIDDEN
    NOT_FOUND = status.HTTP_404_NOT_FOUND
    METHOD_NOT_ALLOWED = status.HTTP_405_METHOD_NOT_ALLOWED
    CONFLICT = status.HTTP_409_CONFLICT
    UNPROCESSABLE_ENTITY = status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Server Errors
    INTERNAL_SERVER_ERROR = status.HTTP_500_INTERNAL_SERVER_ERROR
    SERVICE_UNAVAILABLE = status.HTTP_503_SERVICE_UNAVAILABLE