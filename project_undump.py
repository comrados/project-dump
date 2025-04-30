import os
import re
import argparse
from pathlib import Path
from datetime import datetime


def parse_project_dump(dump_file):
    """Parse a project dump file and extract the directory structure and file contents."""
    with open(dump_file, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Extract project name from header
    project_name_match = re.search(r'<<PROJECT_INFO>>\nPROJECT_PATH: (.+)\n', content)
    project_name = os.path.basename(project_name_match.group(1)) if project_name_match else "undumped_project"
    
    # Parse file contents section
    file_contents = {}
    
    # Find all file sections using the distinct start and end delimiters
    file_pattern = r'<<FILE>>\nFILE_PATH: (.+?)\n<<CONTENT_START>>\n(.*?)<<CONTENT_END>>'
    
    for match in re.finditer(file_pattern, content, re.DOTALL):
        file_path = match.group(1)
        file_content = match.group(2)
        file_contents[file_path] = file_content
    
    return project_name, file_contents


def recreate_project(output_dir, project_name, file_contents, verbose=False):
    """Recreate the project structure from the parsed dump."""
    # Create the project root directory
    project_dir = Path(output_dir) / project_name
    
    try:
        project_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created project directory: {project_dir}")
        
        # Process all files
        for file_path, content in file_contents.items():
            full_path = project_dir / file_path
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            if verbose:
                print(f"Created file: {full_path}")
        
        return True
    except Exception as e:
        print(f"Error recreating project: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Project Undumper - Recreate a project from a dump file")
    parser.add_argument("--dump-file", "-d", default="project_dump.txt", help="Path to the project dump file")
    parser.add_argument("--output", "-o", default=".", help="Output directory where the project will be recreated")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Check if dump file exists
    if not os.path.isfile(args.dump_file):
        print(f"Error: Dump file '{args.dump_file}' not found.")
        return
    
    # Parse the dump file
    print(f"Parsing dump file: {args.dump_file}")
    start_time = datetime.now()
    project_name, file_contents = parse_project_dump(args.dump_file)
    
    # Create the output directory if it doesn't exist
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Recreate the project
    print(f"Recreating project '{project_name}' in {output_dir}")
    success = recreate_project(output_dir, project_name, file_contents, args.verbose)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    if success:
        print(f"Project successfully undumped into {output_dir / project_name}")
        print(f"Recreated {len(file_contents)} files in {duration:.2f} seconds.")
    else:
        print("Failed to recreate project from dump.")


if __name__ == "__main__":
    main()