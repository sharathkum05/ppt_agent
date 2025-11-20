"""Google Drive API service for sharing presentations"""
from googleapiclient.errors import HttpError


class DriveService:
    """Service for interacting with Google Drive API"""
    
    def __init__(self, drive_service):
        """
        Initialize with authenticated Google Drive service
        
        Args:
            drive_service: Authenticated Google Drive API service object
        """
        self.service = drive_service
    
    def share_presentation(self, file_id: str) -> None:
        """
        Share presentation with "anyone with link" permission
        
        Args:
            file_id: Google Drive file ID (presentation ID)
            
        Raises:
            HttpError: If Google API call fails
        """
        try:
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
        except HttpError as error:
            raise HttpError(
                f"Failed to share presentation: {error.resp.status} - {error.content}",
                error.resp
            )
    
    def get_shareable_link(self, file_id: str) -> str:
        """
        Get shareable link for the presentation
        
        Args:
            file_id: Google Drive file ID (presentation ID)
            
        Returns:
            str: Shareable web view link
            
        Raises:
            HttpError: If Google API call fails
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()
            
            return file.get('webViewLink', '')
        except HttpError as error:
            raise HttpError(
                f"Failed to get shareable link: {error.resp.status} - {error.content}",
                error.resp
            )
    
    def share_and_get_link(self, file_id: str) -> str:
        """
        Share presentation and get shareable link
        
        Args:
            file_id: Google Drive file ID (presentation ID)
            
        Returns:
            str: Shareable web view link
            
        Raises:
            HttpError: If Google API call fails
        """
        self.share_presentation(file_id)
        return self.get_shareable_link(file_id)
    
    def move_to_folder(self, file_id: str, folder_id: str) -> None:
        """
        Move a file to a specific folder in Google Drive
        
        Args:
            file_id: Google Drive file ID (presentation ID)
            folder_id: Google Drive folder ID where file should be moved
            
        Raises:
            HttpError: If Google API call fails
        """
        try:
            # Get the current parents of the file
            file = self.service.files().get(
                fileId=file_id,
                fields='parents'
            ).execute()
            
            previous_parents = ",".join(file.get('parents', []))
            
            # Move the file to the new folder
            self.service.files().update(
                fileId=file_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
        except HttpError as error:
            raise HttpError(
                f"Failed to move file to folder: {error.resp.status} - {error.content}",
                error.resp
            )

