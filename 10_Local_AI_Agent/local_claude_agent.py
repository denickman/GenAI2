import os
from pathlib import Path
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Явно указываем путь к .env — не зависит от того, откуда запущен скрипт
# (терминал, PyCharm и т.д.)
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

console = Console(force_terminal=True, color_system="truecolor")

llm = init_chat_model(
    "claude-sonnet-4-6",
    model_provider='anthropic',
    temperature=0.5
)


def list_directory(path: str = ".") -> str:
    """List all files and folders in the given directory path. Default is current directory."""
    try:
        folder_names = []
        file_names = []

        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                folder_names.append(item)
            else:
                file_names.append(item)

        parts = []
        if folder_names:
            parts.append("Folders:\n" + "\n".join(folder_names))
        if file_names:
            parts.append("Files:\n" + "\n".join(file_names))

        if not parts:
            return f"Directory '{path}' is empty"

        return "\n\n".join(parts)
    except Exception as e:
        return f"Error listing directories: {str(e)}"


def write_file(filepath: str, content: str) -> str:
    """Write content to a file. Creates new file or overwrites existing file."""
    try:
        with open(filepath, 'w') as file:
            file.write(content)
        return f"File {filepath} created successfully"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def read_file(filepath: str) -> str:
    """Read and return the contents of a file at the given filepath"""
    try:
        with open(filepath, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"


def create_directory(path: str) -> str:
    """Create a new directory at the given path. Can create nested directories."""
    try:
        os.makedirs(path, exist_ok=True)
        return f"Successfully created directory {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"


system_prompt = """
You are a helpful coding assistant that can help users navigate, read and edit files.

You have access to four tools:
- list_directory: Show files and folders in a directory
- read_file: Read the contents of a file
- write_file: Create or edit files
- create_directory: Create new directories (including nested directories)

Be helpful and clear in your responses. When editing files or creating directories, always confirm what changes you made.
"""

agent = create_agent(
    model=llm,
    tools=[list_directory, write_file, read_file, create_directory],
    system_prompt=system_prompt,
)

# История разговора накапливается здесь между итерациями диалога,
# поэтому объявляем список ДО начала цикла, а не внутри него.
messages = []

console.print("[bold green]Агент запущен. Напишите задание (или 'exit' для выхода).[/bold green]\n")

while True:
    user_input = console.input("[bold magenta]Вы: [/bold magenta]")

    if user_input.strip().lower() in ("exit", "quit", "выход"):
        console.print("[bold red]Завершение работы.[/bold red]")
        break

    if not user_input.strip():
        continue

    # добавляем новое сообщение пользователя в общую историю
    messages.append({"role": "user", "content": user_input})

    ai_message = None
    chunks = agent.stream({"messages": messages}, stream_mode='updates')

    for chunk in chunks:
        for step, data in chunk.items():
            if step == 'model':
                msg = data['messages'][-1]
                if msg.tool_calls:
                    for call in msg.tool_calls:
                        console.print(f"[bold yellow]🔧 Using tool: [/bold yellow][cyan]{call['name']}[/cyan]")
                else:
                    ai_message = msg.content
                    # добавляем ответ модели в историю, чтобы она помнила его в следующий раз
                    messages.append({"role": "assistant", "content": ai_message})
            elif step == 'tools':
                result = data['messages'][-1].content
                result = result if len(result) < 50 else result[:50] + "..."
                console.print(f"🗒[bold green] Tool result:[/bold green]\n [dim]{result}[/dim]")

    if ai_message:
        markdown_output = Markdown(ai_message)
        panel_output = Panel(markdown_output,
                             title="[bold cyan]Assistant Response[/bold cyan]",
                             border_style="blue",
                             padding=(1, 2))
        console.print(panel_output)
    else:
        console.print("[bold red]No final text response was produced by the agent.[/bold red]")

    console.print()  # пустая строка для читаемости перед следующим вопросом