
import os
import http.server
import socketserver
import webbrowser
from rich.console import Console

console = Console()

def run_serve():
    port = 8000
    directory = "out/site"
    
    if not os.path.exists(directory):
        console.print(f"[red]Directory {directory} does not exist. Run 'uke site' first.[/red]")
        return
        
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    with socketserver.TCPServer(("", port), Handler) as httpd:
        url = f"http://localhost:{port}"
        console.print(f"[green]Serving static site at {url}[/green]")
        console.print("Press Ctrl+C to stop.")
        
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            console.print("\n[yellow]Server stopped.[/yellow]")
            httpd.server_close()
