import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from parsers.resume_parser import parse_resume
from rag.enhancer import enhance_summaries

def main():
    # Paths
    resume_path = "resume/resume.docx"
    output_dir = Path("docs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse resume
    print("📄 Parsing resume...")
    data = parse_resume(resume_path)

    # Enhance with RAG + Gemini
    print("🤖 Enhancing summaries with Gemini + RAG...")
    data["projects"] = enhance_summaries(data["projects"])

    # Render HTML
    print("🎨 Rendering portfolio...")
    env = Environment(loader=FileSystemLoader("src/templates"))
    template = env.get_template("portfolio.html.j2")
    html = template.render(**data)

    # Save
    (output_dir / "index.html").write_text(html)
    shutil.copytree("static", output_dir / "static", dirs_exist_ok=True)
    os.system(f"cp static/style.css {output_dir}/")  # quick fix

    print(f"✅ Portfolio ready at: {output_dir}/index.html")
    print("👉 Run: python -m http.server 8000 --directory outputs/site")
    print("Then open http://localhost:8000 in preview")

if __name__ == "__main__":
    main()