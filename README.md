# Project Dumper

## Overview
This utility is a command-line tool to recursively scan a given directory, print a tree view of the project structure, and dump the contents of selected files into a single text file. It's particularly useful for feeding entire codebases into LLMs for analysis or debugging purposes.

## Features
- Tree-style directory structure output
- Dump file contents into a single readable `.txt` file
- Configurable inclusion/exclusion rules via `config.json`
- Prevents duplicate file dumps
- Supports force-inclusion and force-exclusion of specific files or directories

## Getting Started

### 1. Clone or Download
```bash
git clone https://github.com/comrados/project-dump.git
```

### 2. Configuration
Edit the `config.json` file to define:
- Allowed file extensions
- Ignored directories
- Force-included and force-excluded paths

Example:
```json
{
    "allowed_extensions": [".py", ".txt", ".json", ".env", ".yml", ".yaml", ".dockerfile"],
    "ignored_dirs": [".git", "__pycache__", ".idea", ".vscode"],
    "force_include": ["Dockerfile"],
    "force_exclude": ["logs/", "data/"]
}

```

### 3. Usage
Run the script from the command line:

```bash
python project_dump.py /path/to/your/project --config config.json --output output.txt
```

- `--config` (optional): Path to your custom config file.
- `--output` (optional): Path where the result file will be saved.

### 4. Output
The script creates a single file (default `project_dump.txt`) that includes:
- A visual directory tree of the project
- The full contents of included files under appropriate headers

## License
Copyright (c) 2025 comrados

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


