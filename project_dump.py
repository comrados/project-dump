import os
import json
import argparse
from datetime import datetime
from pathlib import Path

def load_config(config_path):
    """Load configuration from a JSON file."""
    try:
        # Always resolve config relative to script location
        script_dir = Path(__file__).parent.resolve()
        config_path = (script_dir / config_path).resolve()
        
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        print(f"Successfully loaded configuration from '{config_path}'.")
        return config
    except FileNotFoundError:
        print(f"Configuration file '{config_path}' not found. Using default configuration.")
        return {
            "allowed_extensions": [".py", ".txt", ".json", ".env", ".yml", ".yaml", ".dockerfile", "Dockerfile", ".gitignore", ".dockerignore"],
            "ignored_dirs": [".git", "__pycache__", ".idea", ".vscode", "node_modules", "venv", ".env", "dist", "build"]
        }
    except json.JSONDecodeError:
        print(f"Error parsing configuration file '{config_path}'. Using default configuration.")
        return {
            "allowed_extensions": [".py", ".txt", ".json", ".env", ".yml", ".yaml", ".dockerfile", "Dockerfile", ".gitignore", ".dockerignore"],
            "ignored_dirs": [".git", "__pycache__", ".idea", ".vscode", "node_modules", "venv", ".env", "dist", "build"]
        }

def is_allowed_file(file_path, allowed_extensions):
    """Check if a file should be included based on its extension."""
    _, ext = os.path.splitext(file_path)
    
    # Check if the extension or full filename is in allowed_extensions
    return ext.lower() in allowed_extensions or os.path.basename(file_path) in allowed_extensions

def get_tree_structure(path, prefix="", ignored_dirs=None, allowed_extensions=None, processed_files=None):
    """Generate a tree structure of the directory."""
    if ignored_dirs is None:
        ignored_dirs = []
    if allowed_extensions is None:
        allowed_extensions = []
    if processed_files is None:
        processed_files = set()
    
    tree_output = ""
    items = sorted(os.listdir(path))
    
    # First, add directories
    dirs = [item for item in items if os.path.isdir(os.path.join(path, item)) and item not in ignored_dirs]
    for i, dir_name in enumerate(dirs):
        is_last_dir = i == len(dirs) - 1
        dir_path = os.path.join(path, dir_name)
        
        # Add directory to the tree
        tree_output += f"{prefix}{'└── ' if is_last_dir else '├── '}{dir_name}/\n"
        
        # Process subdirectory with updated prefix
        new_prefix = f"{prefix}{'    ' if is_last_dir else '│   '}"
        tree_output += get_tree_structure(
            dir_path, 
            new_prefix, 
            ignored_dirs, 
            allowed_extensions, 
            processed_files
        )
    
    # Then, add files
    files = [item for item in items if os.path.isfile(os.path.join(path, item))]
    allowed_files = [f for f in files if is_allowed_file(f, allowed_extensions)]
    
    for i, file_name in enumerate(allowed_files):
        is_last_file = i == len(allowed_files) - 1
        file_path = os.path.join(path, file_name)
        
        # Add file to the tree and to processed files
        tree_output += f"{prefix}{'└── ' if is_last_file else '├── '}{file_name}\n"
        processed_files.add(os.path.abspath(file_path))
    
    return tree_output

def dump_file_contents(path, output_file, ignored_dirs, allowed_extensions):
    """Dump the contents of allowed files to the output file."""
    processed_files = set()
    
    # First, create and write the tree structure
    tree_structure = get_tree_structure(
        path, 
        ignored_dirs=ignored_dirs, 
        allowed_extensions=allowed_extensions,
        processed_files=processed_files
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"# PROJECT DUMP: {os.path.abspath(path)}\n")
        f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Write tree structure
        f.write("## Directory Structure\n```\n")
        f.write(f"{os.path.basename(path)}/\n")
        f.write(tree_structure)
        f.write("```\n\n")
        
        # Write file contents
        f.write("## File Contents\n\n")
        
        file_count = 0
        for file_path in sorted(processed_files):
            rel_path = os.path.relpath(file_path, path)
            f.write(f"### {rel_path}\n```\n")
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                    f.write(file.read())
            except Exception as e:
                f.write(f"[Error reading file: {str(e)}]\n")
            
            f.write("\n```\n\n")
            file_count += 1
            
    return file_count

def main():
    parser = argparse.ArgumentParser(description="Project Dumper - Export project structure and file contents to a text file")
    parser.add_argument("path", nargs="?", default=".", help="Path to the project directory")
    parser.add_argument("--config", default="config.json", help="Path to the configuration file")
    parser.add_argument("--output", default="project_dump.txt", help="Output file name")
    args = parser.parse_args()
    
    # Load configuration using pathlib for robust path handling
    config = load_config(args.config)
    
    allowed_extensions = config.get("allowed_extensions", [])
    ignored_dirs = config.get("ignored_dirs", [])
    
    # Convert strings to lowercase for case-insensitive comparison
    allowed_extensions = [ext.lower() if ext.startswith('.') else ext for ext in allowed_extensions]
    
    # Normalize and resolve the project path
    project_path = os.path.abspath(args.path)
    
    print(f"Starting project dump for: {project_path}")
    print(f"Ignoring directories: {ignored_dirs}")
    print(f"Allowing extensions/files: {allowed_extensions}")
    print(f"Output file: {args.output}")
    
    # Generate the dump
    file_count = dump_file_contents(project_path, args.output, ignored_dirs, allowed_extensions)
    
    print(f"Project dump successfully created: {args.output}")
    print(f"Included {file_count} files in the dump.")

if __name__ == "__main__":
    main()