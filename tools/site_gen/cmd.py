
import os
import json
import yaml
from pathlib import Path
from rich.console import Console

console = Console()

class SiteGenerator:
    def __init__(self):
        self.out_dir = Path("out/site")
        self.data_dir = self.out_dir / "data"
        self.images_dir = Path("out/images") # External to site, but referenced
        self.status = {}
        if os.path.exists("out/status.json"):
            with open("out/status.json") as f:
                self.status = json.load(f)
        
        self.los = []
        self.load_los()

    def load_los(self):
        knowledge_dir = Path("knowledge/learning_objects")
        for root, dirs, files in os.walk(knowledge_dir):
            for file in files:
                if file.endswith(".yml") or file.endswith(".yaml"):
                    try:
                        with open(Path(root) / file) as f:
                            data = yaml.safe_load(f)
                            if "id" in data:
                                self.los.append(data)
                    except:
                        pass

    def generate(self):
        os.makedirs(self.out_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 1. Generate Data JSON
        self.generate_graph_json()
        self.generate_paths_json() # Reuse Planner output conceptually
        
        # 2. Generate HTML Pages
        self.generate_index()
        self.generate_lo_pages()
        self.generate_graph_page()
        self.generate_path_page()
        
        # 3. Copy CSS/JS string assets (inline or file write)
        self.write_assets()

    def generate_graph_json(self):
        nodes = []
        links = []
        for lo in self.los:
            status = self.status.get(lo["id"], "unknown")
            color = "#4caf50" if status=="verified" else "#ff9800" if status=="needs_review" else "#f44336"
            
            nodes.append({
                "id": lo["id"],
                "title": lo["title"],
                "type": lo["type"],
                "status": status,
                "color": color
            })
            
            for p in lo.get("prerequisites", []):
                links.append({"source": p, "target": lo["id"]})
                
        graph = {"nodes": nodes, "links": links}
        with open(self.data_dir / "graph.json", "w") as f:
            json.dump(graph, f, indent=2)

    def generate_paths_json(self):
        # Read from out/path/path.json if exists
        path_file = Path("out/path/path.json")
        if path_file.exists():
            with open(path_file) as f:
                data = json.load(f)
            with open(self.data_dir / "paths.json", "w") as f:
                json.dump(data, f, indent=2)

    def write_assets(self):
        # Simple CSS
        css = """
        body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #f5f5f5; color: #333; }
        header { background: #222; color: #fff; padding: 1rem; display: flex; justify-content: space-between; align-items: center; }
        nav a { color: #ccc; text-decoration: none; margin-left: 1rem; }
        nav a:hover { color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .card { background: #fff; padding: 1.5rem; margin-bottom: 1rem; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .badge { display: inline-block; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold; text-transform: uppercase; }
        .badge.verified { background: #e8f5e9; color: #2e7d32; }
        .badge.needs_review { background: #fff3e0; color: #ef6c00; }
        .badge.concept { background: #e3f2fd; color: #1565c0; }
        .badge.task { background: #fce4ec; color: #c2185b; }
        .badge.troubleshooting { background: #f3e5f5; color: #7b1fa2; }
        h1, h2, h3 { color: #222; }
        pre { background: #eee; padding: 1rem; overflow-x: auto; }
        img { max-width: 100%; border: 1px solid #ddd; }
        .status-container { margin-bottom: 2rem; }
        """
        with open(self.out_dir / "style.css", "w") as f:
            f.write(css)

    def _header(self):
        return """
        <header>
            <div class="logo">UKE v4.1</div>
            <nav>
                <a href="index.html">Home</a>
                <a href="graph.html">Graph</a>
                <a href="path.html">Learning Paths</a>
            </nav>
        </header>
        """

    def generate_index(self):
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Unreal Knowledge Engine</title><link rel="stylesheet" href="style.css"></head>
        <body>
            {self._header()}
            <div class="container">
                <h1>Knowledge Base</h1>
                <div class="search-bar">
                    <input type="text" placeholder="Search..." style="width: 100%; padding: 0.5rem;">
                </div>
                <div class="status-container">
                    <h3>Learning Objects</h3>
        """
        
        for lo in self.los:
            status = self.status.get(lo["id"], "unknown")
            html += f"""
                <div class="card">
                    <div style="display:flex; justify-content:space-between;">
                        <h3><a href="lo/{lo['id']}.html">{lo['title']}</a></h3>
                        <div>
                            <span class="badge {lo['type']}">{lo['type']}</span>
                            <span class="badge {status}">{status}</span>
                        </div>
                    </div>
                    <p>{lo['description']}</p>
                </div>
            """
            
        html += """
            </div>
            </div>
        </body>
        </html>
        """
        with open(self.out_dir / "index.html", "w") as f:
            f.write(html)

    def generate_lo_pages(self):
        lo_dir = self.out_dir / "lo"
        os.makedirs(lo_dir, exist_ok=True)
        
        for lo in self.los:
            status = self.status.get(lo["id"], "unknown")
            
            # Check for images
            img_path = Path("out/images") / lo["id"] / "step_01.final.png"
            img_html = ""
            if img_path.exists():
                # We need relative path from out/site/lo/FILE.html -> out/images/...
                # out/site/lo -> out/site (-1) -> out (-2) -> out/images
                rel_img_path = f"../../images/{lo['id']}/step_01.final.png"
                img_html = f"""
                <div class="card">
                    <h2>Tutorial Capture</h2>
                    <img src="{rel_img_path}" alt="Capture">
                </div>
                """
            
            evidence_html = "<ul>"
            for ev in lo.get("evidence", []):
                evidence_html += f"<li><b>{ev['symbol']}</b> in <i>{ev['file']}</i> (Hash: {ev['snippet_hash'][:8]}...)</li>"
            evidence_html += "</ul>"

            html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>{lo['title']}</title><link rel="stylesheet" href="../style.css"></head>
            <body>
                {self._header().replace('href="', 'href="../')}
                <div class="container">
                    <div style="margin-bottom:1rem;"><a href="../index.html">&larr; Back</a></div>
                    <div class="card">
                        <h1>{lo['title']}</h1>
                        <div style="margin-bottom:1rem;">
                            <span class="badge {lo['type']}">{lo['type']}</span>
                            <span class="badge {status}">{status}</span>
                        </div>
                        <p>{lo['description']}</p>
                    </div>
                    
                    {img_html}
                    
                    <div class="card">
                        <h3>Evidence</h3>
                        {evidence_html}
                    </div>
                    
                    <div class="card">
                        <h3>Prerequisites</h3>
                        <ul>
                            {''.join([f'<li><a href="{p}.html">{p}</a></li>' for p in lo.get("prerequisites", [])])}
                        </ul>
                    </div>
                </div>
            </body>
            </html>
            """
            with open(lo_dir / f"{lo['id']}.html", "w", encoding='utf-8') as f:
                f.write(html)

    def generate_graph_page(self):
        # Minimal Force Graph using D3 or just placeholder text for POC
        # Since "Internet required: None" and allowed deps are strictly Python libs, 
        # we can't easily fetch D3 from CDN.
        # We'll just dump a simple SVG or Canvas implementation if we really wanted, 
        # or just show the JSON data for now.
        # User requirement: "Verified against UE 5.6" -> "Repo must run without internet". 
        # But website viewing usually implies browser. 
        # I will include a very simple JS script to render nodes if possible, or just link the JSON.
        
        # Actually I can embed a tiny graph library or write a very simple canvas renderer in raw JS in the HTML.
        # Let's write a barebones JS renderer for thePOC.
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Knowledge Graph</title><link rel="stylesheet" href="style.css"></head>
        <body>
            {self._header()}
            <div class="container">
                <h1>Dependency Graph</h1>
                <canvas id="graphCanvas" width="800" height="600" style="border:1px solid #ccc; background:#fff;"></canvas>
            </div>
            <script>
                fetch('data/graph.json').then(r => r.json()).then(data => {{
                    const canvas = document.getElementById('graphCanvas');
                    const ctx = canvas.getContext('2d');
                    const nodes = data.nodes;
                    const links = data.links;
                    
                    // Simple random positioning then layout simulation? 
                    // Or just a circle layout for POC simplicity.
                    const cx = canvas.width / 2;
                    const cy = canvas.height / 2;
                    const radius = 200;
                    
                    nodes.forEach((n, i) => {{
                        const angle = (i / nodes.length) * 2 * Math.PI;
                        n.x = cx + radius * Math.cos(angle);
                        n.y = cy + radius * Math.sin(angle);
                    }});
                    
                    // Draw links
                    ctx.strokeStyle = '#999';
                    links.forEach(l => {{
                        const source = nodes.find(n => n.id === l.source);
                        const target = nodes.find(n => n.id === l.target);
                        if(source && target) {{
                            ctx.beginPath();
                            ctx.moveTo(source.x, source.y);
                            ctx.lineTo(target.x, target.y);
                            ctx.stroke();
                        }}
                    }});
                    
                    // Draw nodes
                    nodes.forEach(n => {{
                        ctx.fillStyle = n.color;
                        ctx.beginPath();
                        ctx.arc(n.x, n.y, 15, 0, 2 * Math.PI);
                        ctx.fill();
                        ctx.fillStyle = '#000';
                        ctx.fillText(n.id, n.x + 20, n.y);
                    }});
                    
                    // Click handler to go to LO page (simple bounding box check could go here)
                    canvas.addEventListener('click', (e) => {{
                         const rect = canvas.getBoundingClientRect();
                         const x = e.clientX - rect.left;
                         const y = e.clientY - rect.top;
                         nodes.forEach(n => {{
                             const dist = Math.sqrt((x-n.x)**2 + (y-n.y)**2);
                             if (dist < 15) {{
                                 window.location.href = 'lo/' + n.id + '.html';
                             }}
                         }});
                    }});
                }});
            </script>
        </body>
        </html>
        """
        with open(self.out_dir / "graph.html", "w") as f:
            f.write(html)

    def generate_path_page(self):
         html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Learning Path</title><link rel="stylesheet" href="style.css"></head>
        <body>
            {self._header()}
            <div class="container">
                <h1>Active Learning Path</h1>
                <div id="path-container"></div>
            </div>
            <script>
                fetch('data/paths.json').then(r => r.json()).then(data => {{
                    const container = document.getElementById('path-container');
                    const steps = data.details || [];
                    
                    let html = '';
                    steps.forEach((step, i) => {{
                        html += `
                        <div class="card">
                            <h3>${{i+1}}. <a href="lo/${{step.id}}.html">${{step.title}}</a></h3>
                            <p>${{step.description}}</p>
                        </div>
                        <div style="text-align:center; font-size:20px;">⬇️</div>
                        `;
                    }});
                    // Remove last arrow
                    html = html.substring(0, html.lastIndexOf('<div'));
                    
                    container.innerHTML = html;
                }});
            </script>
        </body>
        </html>
        """
         with open(self.out_dir / "path.html", "w", encoding='utf-8') as f:
            f.write(html)

def run_site():
    console.print(f"[bold]Generating Static Site...[/bold]")
    gen = SiteGenerator()
    gen.generate()
    console.print(f"[green]Site generated in out/site[/green]")
