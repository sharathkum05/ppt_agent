"""Google API authentication utilities"""
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path
from typing import Tuple, Dict, Any

from app.config import settings


def get_google_credentials():
    """
    Load and return Google service account credentials
    Supports both environment variables (Vercel) and file path (local)
    
    Returns:
        service_account.Credentials: Authenticated credentials object
        
    Raises:
        FileNotFoundError: If credentials file doesn't exist (local only)
        ValueError: If credentials are invalid
    """
    # Try to load from environment variables first (for Vercel/serverless)
    if os.getenv("GOOGLE_PROJECT_ID") or os.getenv("project_id"):
        # Build credentials dict from environment variables
        try:
            creds_dict = _build_credentials_from_env()
        except ValueError as e:
            # Re-raise ValueError with clearer message
            raise ValueError(f"Missing Google credentials environment variables: {str(e)}")
        
        try:
            credentials = service_account.Credentials.from_service_account_info(
                creds_dict,
                scopes=settings.GOOGLE_SCOPES
            )
            return credentials
        except Exception as e:
            error_msg = str(e)
            # Provide more helpful error message
            if "private_key" in error_msg.lower():
                raise ValueError(
                    f"Invalid private key format. Make sure it includes BEGIN/END markers and newlines. "
                    f"Original error: {error_msg}"
                )
            raise ValueError(f"Failed to load Google credentials from env vars: {error_msg}")
    
    # Fall back to file path (for local development)
    creds_path = settings.google_credentials_path
    
    if not creds_path.exists():
        raise FileNotFoundError(
            f"Google credentials file not found at: {creds_path}. "
            "Either provide a file or set environment variables."
        )
    
    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(creds_path),
            scopes=settings.GOOGLE_SCOPES
        )
        return credentials
    except Exception as e:
        raise ValueError(f"Failed to load Google credentials: {str(e)}")


def _build_credentials_from_env() -> Dict[str, Any]:
    """
    Build credentials dictionary from individual environment variables
    
    Returns:
        dict: Service account credentials dictionary
    """
    # Support both GOOGLE_* prefix and direct field names
    def get_env(key: str, alt_key: str = None) -> str:
        value = os.getenv(key) or os.getenv(alt_key) if alt_key else os.getenv(key)
        if not value:
            raise ValueError(f"Missing required environment variable: {key} or {alt_key}")
        return value
    
    # Handle private key - may have \n escaped as \\n in env vars
    private_key = get_env("GOOGLE_PRIVATE_KEY", "private_key")
    # Replace escaped newlines with actual newlines
    private_key = private_key.replace("\\n", "\n")
    
    creds_dict = {
        "type": "service_account",
        "project_id": get_env("GOOGLE_PROJECT_ID", "project_id"),
        "private_key_id": get_env("GOOGLE_PRIVATE_KEY_ID", "private_key_id"),
        "private_key": private_key,
        "client_email": get_env("GOOGLE_CLIENT_EMAIL", "client_email"),
        "client_id": get_env("GOOGLE_CLIENT_ID", "client_id"),
        "auth_uri": get_env("GOOGLE_AUTH_URI", "auth_uri"),
        "token_uri": get_env("GOOGLE_TOKEN_URI", "token_uri"),
        "auth_provider_x509_cert_url": get_env("GOOGLE_AUTH_PROVIDER_X509_CERT_URL", "auth_provider_x509_cert_url"),
        "client_x509_cert_url": get_env("GOOGLE_CLIENT_X509_CERT_URL", "client_x509_cert_url"),
        "universe_domain": get_env("GOOGLE_UNIVERSE_DOMAIN", "universe_domain"),
    }
    
    return creds_dict


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

