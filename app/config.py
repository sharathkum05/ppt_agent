import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings and configuration"""
    
    # Anthropic API configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Google API configuration
    GOOGLE_CREDENTIALS_PATH: str = os.getenv(
        "GOOGLE_CREDENTIALS_PATH", 
        "credentials/service_account.json"
    )
    
    # Google Drive folder ID where presentations will be created
    GOOGLE_DRIVE_FOLDER_ID: str = os.getenv(
        "GOOGLE_DRIVE_FOLDER_ID",
        "1OUSgOEPTy9Bt3nd15ZHH5DgvCho2QUwS"  # Default folder from user setup
    )
    
    # Default presentation ID to use (hardcoded template)
    DEFAULT_PRESENTATION_ID: str = os.getenv(
        "DEFAULT_PRESENTATION_ID",
        "1ssIEyRV9ARbPZcKoUcl1sneIlUsW_p-ipRl7KnRRCDk"  # User's Untitled.ppt template
    )
    
    # Google API scopes
    GOOGLE_SCOPES = [
        "https://www.googleapis.com/auth/presentations",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Agent configuration
    AGENT_MAX_ITERATIONS: int = int(os.getenv("AGENT_MAX_ITERATIONS", "20"))
    AGENT_ENABLE_REVIEW: bool = os.getenv("AGENT_ENABLE_REVIEW", "true").lower() == "true"
    AGENT_MODEL: str = os.getenv("AGENT_MODEL", "claude-3-5-sonnet-20241022")
    
    @property
    def google_credentials_path(self) -> Path:
        """Get absolute path to Google credentials file (safe - doesn't fail if path doesn't exist)"""
        try:
            # Try to resolve the path, but don't fail if it doesn't exist
            path = Path(self.GOOGLE_CREDENTIALS_PATH)
            if path.is_absolute():
                return path
            # For relative paths, try to resolve, but catch errors
            try:
                return path.resolve()
            except (OSError, RuntimeError):
                # If resolve fails, return the path as-is
                return path
        except Exception:
            # If anything fails, return a Path object anyway
            return Path(self.GOOGLE_CREDENTIALS_PATH)
    
    def is_using_env_vars(self) -> bool:
        """Check if we're using environment variables for Google credentials"""
        return bool(os.getenv("GOOGLE_PROJECT_ID") or os.getenv("project_id"))
    
    def validate(self) -> None:
        """Validate that required settings are present (safe - doesn't crash on missing paths)"""
        errors = []
        
        # Check Anthropic API key
        if not self.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY environment variable is required")
        
        # Check Google credentials
        if self.is_using_env_vars():
            # Using environment variables (Vercel/serverless)
            missing_vars = []
            
            # Check for project_id (either GOOGLE_PROJECT_ID or project_id)
            if not (os.getenv("GOOGLE_PROJECT_ID") or os.getenv("project_id")):
                missing_vars.append("GOOGLE_PROJECT_ID or project_id")
            
            # Check for private_key (either GOOGLE_PRIVATE_KEY or private_key)
            if not (os.getenv("GOOGLE_PRIVATE_KEY") or os.getenv("private_key")):
                missing_vars.append("GOOGLE_PRIVATE_KEY or private_key")
            
            # Check for client_email (either GOOGLE_CLIENT_EMAIL or client_email)
            if not (os.getenv("GOOGLE_CLIENT_EMAIL") or os.getenv("client_email")):
                missing_vars.append("GOOGLE_CLIENT_EMAIL or client_email")
            
            # Check for token_uri (either GOOGLE_TOKEN_URI or token_uri)
            if not (os.getenv("GOOGLE_TOKEN_URI") or os.getenv("token_uri")):
                missing_vars.append("GOOGLE_TOKEN_URI or token_uri")
            
            if missing_vars:
                errors.append(
                    f"Missing Google credentials environment variables: {', '.join(missing_vars)}. "
                    "Please set these in Vercel environment variables."
                )
        else:
            # Using file-based credentials (local development)
            # Only check if file exists, don't fail on path resolution
            try:
                creds_path = self.google_credentials_path
                if not creds_path.exists():
                    errors.append(
                        f"Google credentials file not found at: {creds_path}. "
                        "Either provide a file or set Google credentials as environment variables."
                    )
            except Exception as e:
                # If path resolution fails, that's okay - we'll try env vars
                errors.append(
                    f"Could not resolve credentials path: {str(e)}. "
                    "Please set Google credentials as environment variables for serverless deployment."
                )
        
        if errors:
            raise ValueError("; ".join(errors))


# Global settings instance
settings = Settings()

