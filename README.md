# Project Dumper

## Overview
**Project Dumper** is a command-line utility that recursively scans a directory, displays a tree view of its structure, and exports the contents of selected files into a single text file. It's ideal for feeding large codebases into LLMs for analysis or debugging.

## Features
- Visual tree representation of the directory structure
- Dumps file contents into a single `.txt` file
- Customizable filtering via a `config.json` file
- Avoids duplicate file dumps
- Force include or exclude specific files or directories

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/comrados/project-dump.git
cd project-dump
```

### 2. Configure
Edit or create a `config.json` file to specify the file types and directories to include or exclude.

Example `config.json`:
```json
{
  "allowed_extensions": [
    ".py",
    ".txt",
    ".json",
    ".env",
    ".yml",
    ".yaml",
    ".dockerfile",
    "Dockerfile",
    ".gitignore",
    ".dockerignore"
  ],
  "ignored_dirs": [
    ".git",
    "__pycache__",
    ".idea",
    ".vscode",
    "node_modules",
    "venv",
    ".env",
    "dist",
    "build"
  ]
}
```

### 3. Run the Script
Use the command below to generate a project dump:

```bash
python project_dump.py /path/to/project --config config.json --output output.txt
```

**Options:**
- `--config`: (Optional) Path to a custom configuration file.
- `--output`: (Optional) Output file name (default: `project_dump.txt`).

### 4. Output Format
The generated output file includes:
- A hierarchical view of the project directory
- The contents of each selected file, grouped under clear headers

## License
Copyright (c) 2025 comrados

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
