import json
import re
from pathlib import Path
from docx2python import docx2python

def parse_resume_json(json_path: str) -> dict:
    with open(json_path, 'r') as f:
        return json.load(f)

def parse_resume_docx(docx_path: str) -> dict:
    """
    Converts a .docx resume into structured dict with name, tagline, projects.
    Assumes a simple format:
      - Name as first line
      - Section headings like 'Projects', 'Experience'
      - Each project as a paragraph under 'Projects'
    """
    doc = docx2python(docx_path)
    full_text = doc.text.strip()

    # Split into lines
    lines = [line.strip() for line in full_text.split('\n') if line.strip()]

    if not lines:
        raise ValueError("Empty resume")

    # Heuristic: first non-empty line = name
    name = lines[0]

    # Find 'Projects' section
    projects = []
    in_projects = False

    for line in lines[1:]:
        if line.lower().startswith('project') or line.lower() == 'projects':
            in_projects = True
            continue
        elif in_projects and (line.isupper() or line.endswith(':') or line in ['Experience', 'Education', 'Skills']):
            # Next section started
            break
        elif in_projects and line:
            # Assume each non-empty line in Projects = one project summary
            # You can improve this later with better parsing
            projects.append({
                "title": "Project",  # We'll let LLM infer/enhance title if needed
                "summary": line
            })

    # Fallback tagline
    tagline = "AI & DevOps Engineer | AWS | GenAI"

    return {
        "name": name,
        "tagline": tagline,
        "projects": projects
    }

def parse_resume(resume_path: str) -> dict:
    path = Path(resume_path)
    if path.suffix.lower() == '.json':
        return parse_resume_json(path)
    elif path.suffix.lower() == '.docx':
        return parse_resume_docx(path)
    else:
        raise ValueError("Unsupported resume format. Use .json or .docx")