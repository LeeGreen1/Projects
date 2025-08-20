from nicegui import ui, app
from bot import AssignmentBot
from file_parser import parse_document
import re
import asyncio  # <-- Import the asyncio library

# Initialize the bot once when the app starts
assignment_bot = AssignmentBot()

@ui.page('/')
def main_page():
    # --- Handler functions are defined first ---
    
    async def run_analysis(brief_text: str):
        """Run the bot's analysis and update the UI with structured results."""
        analysis_container.clear()
        
        with analysis_container:
            ui.label('Analyzing your document...').classes('text-lg text-grey-8')
            ui.spinner(size='lg', color='primary').classes('m-auto my-4')
            
            # Use asyncio's loop to run the blocking bot call in a thread
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, assignment_bot.analyze_brief, brief_text)

        analysis_container.clear()

        # --- Parse the result string to separate reasoning from the breakdown ---
        reasoning = "No specific reasoning section was found."
        breakdown = result

        reasoning_match = re.search(r"###\s*Reasoning\s*\n(.*?)(?=\n###\s*Task Breakdown|$)", result, re.DOTALL | re.IGNORECASE)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()
        
        breakdown_match = re.search(r"###\s*Task Breakdown\s*\n(.*)", result, re.DOTALL | re.IGNORECASE)
        if breakdown_match:
            breakdown = breakdown_match.group(1).strip()
        
        if not reasoning_match and not breakdown_match:
             reasoning = "The model provided a direct breakdown without a separate reasoning section."

        with analysis_container:
            ui.label('Analysis Complete').classes('text-h5 text-positive')
            
            with ui.expansion('Show Reasoning & Logic', icon='psychology').classes('w-full bg-grey-2 mt-2'):
                ui.markdown(reasoning)

            with ui.expansion('Show Final Task Breakdown', icon='checklist', value=True).classes('w-full bg-grey-2 mt-2'):
                ui.markdown(breakdown)
    
    async def handle_upload(e):
        """Called when a file is uploaded."""
        ui.notify('Parsing document...')
        
        # CORRECTED: Use asyncio.get_running_loop() instead of app.loop
        loop = asyncio.get_running_loop()
        brief_text = await loop.run_in_executor(None, parse_document, e.content, e.type)
        
        if brief_text.startswith("Error:"):
            ui.notify(brief_text, color='negative', position='center')
            return
            
        await run_analysis(brief_text)

    # --- Page Styling and UI Layout ---
    ui.add_head_html("""
    <style>
        body { background-color: #f0f2f5; }
        .main-card { width: 90%; max-width: 800px; margin: 2rem auto; }
    </style>
    """)

    with ui.card().classes('main-card'):
        ui.label('AI Assignment Analyzer').classes('text-h4 text-grey-8 text-weight-bold')
        ui.label('Upload your assignment brief (.docx or .pdf) to see its breakdown.').classes('text-subtitle1 text-grey-6')
        ui.separator().classes('my-4')

        ui.upload(
            label="Upload Brief",
            auto_upload=True,
            on_upload=handle_upload,
            max_file_size=5_000_000,
        ).props('accept=".pdf,.docx"').classes('w-full')
        
        analysis_container = ui.column().classes('w-full mt-4')

# Run the NiceGUI app
ui.run(title="AI Assignment Analyzer", dark=False)