"""Test script to verify Google credentials are working"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings as app_settings
from app.utils.auth import get_google_services
from googleapiclient.errors import HttpError


def test_credentials():
    """Test if Google credentials are valid and APIs are accessible"""
    print("=" * 60)
    print("Testing Google Credentials")
    print("=" * 60)
    
    # Step 1: Check if credentials file exists
    print("\n1. Checking credentials file...")
    creds_path = app_settings.google_credentials_path
    if creds_path.exists():
        print(f"   ✓ Credentials file found: {creds_path}")
    else:
        print(f"   ✗ Credentials file NOT found: {creds_path}")
        return False
    
    # Step 2: Try to initialize Google services
    print("\n2. Initializing Google services...")
    try:
        slides_api, drive_api = get_google_services()
        print("   ✓ Google services initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize Google services: {str(e)}")
        return False
    
    # Step 3: Test Google Slides API
    print("\n3. Testing Google Slides API...")
    try:
        # Try to create a test presentation to verify API access
        test_presentation = {'title': 'API Test - Will Delete'}
        result = slides_api.presentations().create(body=test_presentation).execute()
        test_id = result.get('presentationId')
        print(f"   ✓ Slides API working! Can create presentations")
        
        # Clean up test presentation
        try:
            drive_api.files().delete(fileId=test_id).execute()
        except:
            pass
    except HttpError as e:
        if e.resp.status == 403:
            print(f"   ⚠ Slides API accessible but permission denied")
            print(f"   This usually means the service account needs Drive folder access")
            print(f"   Error: {str(e)}")
        else:
            print(f"   ✗ Slides API error: {str(e)}")
            return False
    except Exception as e:
        print(f"   ✗ Unexpected error testing Slides API: {str(e)}")
        return False
    
    # Step 4: Test Google Drive API
    print("\n4. Testing Google Drive API...")
    try:
        # Try to list files (just to test API access)
        files = drive_api.files().list(pageSize=1, q="mimeType='application/vnd.google-apps.presentation'").execute()
        print(f"   ✓ Drive API working! Can access Drive")
    except HttpError as e:
        if e.resp.status == 403:
            print(f"   ⚠ Drive API accessible but permission denied")
            print(f"   This is normal - service account can still create files in shared folders")
        else:
            print(f"   ✗ Drive API error: {str(e)}")
            return False
    except Exception as e:
        print(f"   ✗ Unexpected error testing Drive API: {str(e)}")
        return False
    
    # Step 5: Try to create a test presentation (this will verify full access)
    print("\n5. Testing presentation creation...")
    try:
        from app.services.slides_service import SlidesService
        from app.services.drive_service import DriveService
        
        slides_svc = SlidesService(slides_api)
        drive_svc = DriveService(drive_api)
        
        presentation_id = slides_svc.create_presentation('Test Presentation - Credentials Check')
        print(f"   ✓ Successfully created test presentation!")
        print(f"   Presentation ID: {presentation_id}")
        
        # Try to move to folder if folder ID is configured
        if app_settings.GOOGLE_DRIVE_FOLDER_ID:
            try:
                drive_svc.move_to_folder(presentation_id, app_settings.GOOGLE_DRIVE_FOLDER_ID)
                print(f"   ✓ Moved presentation to shared folder")
            except Exception as e:
                print(f"   ⚠ Could not move to folder: {str(e)}")
        
        print(f"   Link: https://docs.google.com/presentation/d/{presentation_id}")
        
        # Clean up: Delete the test presentation
        try:
            drive_api.files().delete(fileId=presentation_id).execute()
            print(f"   ✓ Test presentation deleted (cleanup)")
        except:
            print(f"   ⚠ Could not delete test presentation (you can delete it manually)")
        
        return True
    except HttpError as e:
        if e.resp.status == 403:
            print(f"   ✗ Permission denied: Cannot create presentations")
            print(f"   This usually means:")
            print(f"   - The service account needs to be shared with a Google Drive folder")
            print(f"   - Or the APIs might not be fully enabled")
            print(f"   Error: {str(e)}")
            return False
        else:
            print(f"   ✗ Error creating presentation: {str(e)}")
            return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n")
    success = test_credentials()
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED - Credentials are working correctly!")
    else:
        print("✗ SOME TESTS FAILED - Please check the errors above")
    print("=" * 60 + "\n")

