"""Google API authentication utilities"""
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path
from typing import Tuple

from app.config import settings


def get_google_credentials():
    """
    Load and return Google service account credentials
    
    Returns:
        service_account.Credentials: Authenticated credentials object
        
    Raises:
        FileNotFoundError: If credentials file doesn't exist
        ValueError: If credentials are invalid
    """
    creds_path = settings.google_credentials_path
    
    if not creds_path.exists():
        raise FileNotFoundError(
            f"Google credentials file not found at: {creds_path}"
        )
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(creds_path),
            scopes=settings.GOOGLE_SCOPES
        )
        return credentials
    except Exception as e:
        raise ValueError(f"Failed to load Google credentials: {str(e)}")


def get_google_services() -> Tuple:
    """
    Create and return authenticated Google Slides and Drive service objects
    
    Returns:
        Tuple[slides_service, drive_service]: Authenticated service objects
        
    Raises:
        HttpError: If authentication fails
    """
    credentials = get_google_credentials()
    
    try:
        slides_service = build('slides', 'v1', credentials=credentials)
        drive_service = build('drive', 'v3', credentials=credentials)
        return slides_service, drive_service
    except HttpError as error:
        raise HttpError(
            f"Failed to create Google API services: {error.resp.status}",
            error.resp
        )

