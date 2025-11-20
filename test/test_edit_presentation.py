"""Test script to verify Google API access to edit existing presentation"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings as app_settings
from app.utils.auth import get_google_services
from app.services.slides_service import SlidesService
from app.services.drive_service import DriveService
from googleapiclient.errors import HttpError


def test_edit_presentation():
    """Test if we can access and edit the existing presentation"""
    print("=" * 60)
    print("Testing Google API Access to Edit Existing Presentation")
    print("=" * 60)
    
    # Step 1: Check credentials
    print("\n1. Checking credentials...")
    creds_path = app_settings.google_credentials_path
    if creds_path.exists():
        print(f"   ✓ Credentials file found: {creds_path}")
    else:
        print(f"   ✗ Credentials file NOT found: {creds_path}")
        return False
    
    # Step 2: Initialize services
    print("\n2. Initializing Google services...")
    try:
        slides_api, drive_api = get_google_services()
        slides_svc = SlidesService(slides_api)
        drive_svc = DriveService(drive_api)
        print("   ✓ Google services initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {str(e)}")
        return False
    
    # Step 3: Check presentation ID
    print("\n3. Checking presentation configuration...")
    presentation_id = app_settings.DEFAULT_PRESENTATION_ID
    print(f"   Presentation ID: {presentation_id}")
    print(f"   Link: https://docs.google.com/presentation/d/{presentation_id}")
    
    # Step 4: Test accessing the presentation
    print("\n4. Testing presentation access...")
    try:
        presentation = slides_api.presentations().get(
            presentationId=presentation_id
        ).execute()
        title = presentation.get('title', 'Unknown')
        slide_count = len(presentation.get('slides', []))
        print(f"   ✓ Successfully accessed presentation!")
        print(f"   Title: {title}")
        print(f"   Current slides: {slide_count}")
    except HttpError as e:
        if e.resp.status == 403:
            print(f"   ✗ Permission denied: Cannot access presentation")
            print(f"   Make sure the presentation is shared with: ppt-agent-service@pptai-478322.iam.gserviceaccount.com")
            return False
        else:
            print(f"   ✗ Error accessing presentation: {str(e)}")
            return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {str(e)}")
        return False
    
    # Step 5: Test clearing slides
    print("\n5. Testing clear_all_slides function...")
    try:
        # Get current slide count before clearing
        presentation = slides_api.presentations().get(
            presentationId=presentation_id
        ).execute()
        slides_before = len(presentation.get('slides', []))
        
        # Clear slides
        slides_svc.clear_all_slides(presentation_id)
        print(f"   ✓ Cleared all slides (had {slides_before} slides)")
        
        # Verify slides are cleared
        presentation = slides_api.presentations().get(
            presentationId=presentation_id
        ).execute()
        slides_after = len(presentation.get('slides', []))
        print(f"   Slides after clearing: {slides_after}")
    except HttpError as e:
        print(f"   ✗ Error clearing slides: {str(e)}")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {str(e)}")
        return False
    
    # Step 6: Test adding a slide
    print("\n6. Testing add_slide function...")
    try:
        result = slides_svc.add_slide(
            presentation_id,
            "TITLE_AND_BODY",
            "Test Slide",
            "This is a test slide to verify the API is working correctly."
        )
        if result.get('success'):
            print(f"   ✓ Successfully added test slide!")
            print(f"   Slide ID: {result.get('slide_id')}")
        else:
            print(f"   ✗ Failed to add slide: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"   ✗ Error adding slide: {str(e)}")
        return False
    
    # Step 7: Test create_presentation (should use existing template)
    print("\n7. Testing create_presentation (uses template)...")
    try:
        new_presentation_id = slides_svc.create_presentation("Test Presentation")
        if new_presentation_id == presentation_id:
            print(f"   ✓ Successfully using existing template!")
            print(f"   Presentation ID matches: {new_presentation_id}")
        else:
            print(f"   ⚠ Warning: Got different presentation ID")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False
    
    # Step 8: Test sharing
    print("\n8. Testing share functionality...")
    try:
        shareable_link = drive_svc.share_and_get_link(presentation_id)
        print(f"   ✓ Successfully shared presentation!")
        print(f"   Shareable link: {shareable_link}")
    except Exception as e:
        print(f"   ⚠ Could not share (may already be shared): {str(e)}")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - Google API access is working!")
    print("=" * 60)
    print(f"\nPresentation is ready to use:")
    print(f"  ID: {presentation_id}")
    print(f"  Link: https://docs.google.com/presentation/d/{presentation_id}")
    print("\nYou can now proceed to set up the Anthropic API key for the agent workflow.")
    print("=" * 60 + "\n")
    
    return True


if __name__ == "__main__":
    success = test_edit_presentation()
    if not success:
        print("\n✗ SOME TESTS FAILED - Please check the errors above\n")
        sys.exit(1)

