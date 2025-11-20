"""Tool definitions for the AI agent"""
from typing import List, Dict, Any

# Tool definitions for Anthropic Claude API
# These tools allow the agent to interact with Google Slides

TOOLS: List[Dict[str, Any]] = [
    {
        "name": "create_presentation",
        "description": "Initializes the presentation template by clearing all existing slides. Call this first before adding new slides. Uses a pre-configured presentation template.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title/theme of the presentation (for reference, used to guide slide creation)"
                }
            },
            "required": ["title"]
        }
    },
    {
        "name": "add_slide",
        "description": "Adds a new slide to the presentation. Use this to add content slides after creating the presentation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "layout": {
                    "type": "string",
                    "enum": ["TITLE", "TITLE_AND_BODY", "TITLE_AND_TWO_COLUMNS", "BLANK"],
                    "description": "The layout type for the slide. Use TITLE for title slides, TITLE_AND_BODY for content slides."
                },
                "title": {
                    "type": "string",
                    "description": "The title text for the slide"
                },
                "content": {
                    "type": "string",
                    "description": "The body content for the slide. Use bullet points or paragraphs. Use \\n for line breaks."
                }
            },
            "required": ["layout", "title", "content"]
        }
    },
    {
        "name": "review_presentation",
        "description": "Reviews the current state of the presentation. Returns information about all slides created so far, including their titles and content. Use this to check your work before finalizing.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "refine_slide",
        "description": "Refines or updates an existing slide's content. Use this to improve slides after reviewing the presentation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "slide_index": {
                    "type": "integer",
                    "description": "The index of the slide to refine (0-based, where 0 is the first slide after title slide)"
                },
                "new_content": {
                    "type": "string",
                    "description": "The updated content for the slide. This will replace the existing content."
                },
                "new_title": {
                    "type": "string",
                    "description": "Optional: New title for the slide. If not provided, title remains unchanged."
                }
            },
            "required": ["slide_index", "new_content"]
        }
    },
    {
        "name": "finalize_presentation",
        "description": "Finalizes the presentation by sharing it and generating a shareable link. Call this when you're done creating and refining all slides. This should be your last action.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


def get_tools() -> List[Dict[str, Any]]:
    """Get the list of available tools for the agent"""
    return TOOLS

