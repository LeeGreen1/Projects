from database import init_db, get_past_assignments, add_assignment
from ai_service import get_ai_breakdown

class AssignmentBot:
    def __init__(self):
        """Initializes the bot and ensures the database is ready."""
        init_db()

    def analyze_brief(self, brief_text: str) -> str:
        """
        Analyzes an assignment brief using the full process.
        
        1. Gets past examples from the database.
        2. Sends the new brief and examples to the AI service.
        3. Stores the new analysis in the database for future learning.
        4. Returns the final breakdown.
        """
        # Get past examples to help the AI understand the task
        past_examples = get_past_assignments(limit=3)

        # Get the new breakdown from the AI service
        breakdown = get_ai_breakdown(brief_text, past_examples)
        
        # Save the new analysis for future use, if successful
        if "An error occurred" not in breakdown and "Ollama server is not running" not in breakdown:
            add_assignment(brief_text, breakdown)
        
        return breakdown