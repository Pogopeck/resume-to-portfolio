Project structure:

resume-to-portfolio/
├── resume/               # your input resume (docx or JSON)
│   └── resume.docx
├── src/
│   ├── parsers/
│   │   └── resume_parser.py
│   ├── templates/
│   │   └── portfolio.html.j2
│   ├── outputs/
│   ├── utils/
│   ├── rag/
│   │   └── enhancer.py
│   └── main.py
├── static/               # for CSS/JS/images (copied to output)
├── requirements.txt
└── .github/workflows/deploy.yml
