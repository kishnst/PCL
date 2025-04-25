import os
import google.generativeai as genai
from dotenv import load_dotenv
import sys
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
import time

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()

def initialize_gemini():
    """Initialize the Gemini API with the API key."""
    try:
        # Get API key from environment variables
        api_key = os.getenv('GEMINI_API_KEY')
        
        # Check if API key exists
        if not api_key:
            console.print("[red]Error: GEMINI_API_KEY not found in environment variables[/red]")
            console.print("[yellow]Please make sure your .env file contains:[/yellow]")
            console.print("[yellow]GEMINI_API_KEY=your_api_key_here[/yellow]")
            sys.exit(1)
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        try:
            model = genai.GenerativeModel('gemini-pro')
            return model
        except Exception as e:
            console.print(f"[red]Error creating Gemini model: {str(e)}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error initializing Gemini: {str(e)}[/red]")
        sys.exit(1)

def get_chat_response(model, message):
    """Get a response from Gemini API."""
    try:
        response = model.generate_content(message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main function to run the chat program."""
    console.print(Panel.fit(
        "[bold blue]Gemini Chat[/bold blue]\n"
        "Type 'exit' or 'quit' to end the conversation",
        title="Welcome",
        border_style="blue"
    ))
    
    # Initialize Gemini
    model = initialize_gemini()
    
    # Chat history
    chat_history = []
    
    while True:
        # Get user input
        user_input = Prompt.ask("\n[bold green]You[/bold green]")
        
        # Check for exit command
        if user_input.lower() in ['exit', 'quit']:
            console.print("\n[bold blue]Goodbye![/bold blue]")
            break
        
        # Add user message to history
        chat_history.append(("user", user_input))
        
        # Show thinking indicator
        with console.status("[bold yellow]Thinking...[/bold yellow]"):
            # Get response from Gemini
            response = get_chat_response(model, user_input)
        
        # Add response to history
        chat_history.append(("assistant", response))
        
        # Display response
        console.print("\n[bold blue]Gemini[/bold blue]")
        console.print(Markdown(response))
        
        # Add a small delay for better readability
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold blue]Goodbye![/bold blue]")
    except Exception as e:
        console.print(f"\n[red]An error occurred: {str(e)}[/red]") 