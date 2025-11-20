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
        """Get absolute path to Google credentials file"""
        return Path(self.GOOGLE_CREDENTIALS_PATH).resolve()
    
    def validate(self) -> None:
        """Validate that required settings are present"""
        if not self.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        if not self.google_credentials_path.exists():
            raise FileNotFoundError(
                f"Google credentials file not found at: {self.google_credentials_path}"
            )


# Global settings instance
settings = Settings()

