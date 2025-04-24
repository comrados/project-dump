import os
import json
import argparse
from pathlib import Path
import textwrap

# --- Default configuration embedded here ---
DEFAULT_CONFIG = {
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
# --- End of Default configuration ---

def load_config(config_path):
    """Loads configuration from a JSON file, using embedded defaults if necessary."""
    try:
        with open(config_path, 'r') as f:
            content = f.read()
            if not content:
                print(f"Warning: Config file '{config_path}' is empty. Using built-in default config.")
                return DEFAULT_CONFIG, "built-in defaults (config file empty)"

            loaded_config = json.loads(content)
            # Start with defaults, override with loaded, ensure keys exist
            final_config = DEFAULT_CONFIG.copy()
            final_config.update(loaded_config)

            # Validate essential keys after potential overwrite
            if "allowed_extensions" not in final_config or "ignored_dirs" not in final_config:
                 print(f"Warning: Config file '{config_path}' is missing essential keys ('allowed_extensions', 'ignored_dirs'). Reverting to built-in defaults.")
                 return DEFAULT_CONFIG, f"built-in defaults (config file '{config_path}' incomplete)"

            print(f"Successfully loaded and merged configuration from '{config_path}'.")
            return final_config, f"'{config_path}' merged with defaults"

    except FileNotFoundError:
        print(f"Info: Config file '{config_path}' not found. Using built-in default config.")
        return DEFAULT_CONFIG, "built-in defaults (config file not found)"
    except json.JSONDecodeError:
        print(f"Error: Config file '{config_path}' contains invalid JSON. Using built-in default config.")
        return DEFAULT_CONFIG, f"built-in defaults (invalid JSON in '{config_path}')"
    except Exception as e:
        print(f"Error loading config file '{config_path}': {e}. Using built-in default config.")
        return DEFAULT_CONFIG, f"built-in defaults (error loading '{config_path}')"

def build_tree(start_path, ignored_dirs, allowed_extensions):
    """Builds the directory tree string and collects files to dump."""
    tree_lines = []
    files_to_dump = []
    start_path = Path(start_path).resolve()

    ignored_dirs_set = set(ignored_dirs)
    allowed_extensions_set = set(allowed_extensions)

    if start_path.name in ignored_dirs_set:
        print(f"Warning: Root directory '{start_path.name}' is in ignored_dirs. Skipping.")
        return "", []

    tree_lines.append(f"{start_path.name}/")

    # Use topdown=True to allow pruning ignored dirs
    for root, dirs, files in os.walk(start_path, topdown=True, onerror=lambda err: print(f"Error accessing {err.filename}: {err.strerror}")):
        current_path = Path(root)

        # Prune ignored directories before descending
        dirs[:] = [d for d in dirs if d not in ignored_dirs_set]

        try:
            relative_path = current_path.relative_to(start_path)
            level = len(relative_path.parts)
        except ValueError:
             print(f"Warning: Could not determine relative path for {current_path}. Skipping content.")
             continue

        indent = '    ' * level
        sub_indent = '    ' * (level + 1)

        dirs.sort()
        files.sort()

        for d in dirs:
            tree_lines.append(f"{sub_indent}├── {d}/")

        files_in_dir = files # No need to copy if not modifying 'files' list itself
        for i, f_name in enumerate(files_in_dir):
            file_ext = os.path.splitext(f_name)[1]
            is_allowed_name = f_name in allowed_extensions_set
            is_allowed_ext = file_ext in allowed_extensions_set and file_ext != ''

            if is_allowed_name or is_allowed_ext:
                # Determine connector style for the tree view
                is_last_item = (i == len(files_in_dir) - 1) and not dirs
                connector = "└──" if is_last_item else "├──"
                tree_lines.append(f"{sub_indent}{connector} {f_name}")

                file_relative_path = relative_path / f_name
                files_to_dump.append(str(file_relative_path))

    return "\n".join(tree_lines), files_to_dump


def dump_files(start_path, relative_file_paths, output_file):
    """Dumps the content of specified files into the output file."""
    start_path = Path(start_path).resolve()
    output_file.write("\n\n" + "=" * 80 + "\n")
    output_file.write(" " * 30 + "FILE CONTENTS\n")
    output_file.write("=" * 80 + "\n\n")

    dumped_paths = set()

    for rel_path_str in relative_file_paths:
        rel_path = Path(rel_path_str.replace('\\', '/')) # Normalize separators
        rel_path_key = str(rel_path)

        if rel_path_key in dumped_paths:
            print(f"Warning: Skipping duplicate file path '{rel_path_key}'")
            continue

        full_path = start_path / rel_path
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as infile:
                content = infile.read()
                output_file.write(f"---\n")
                output_file.write(f"File: {rel_path_key}\n")
                output_file.write(f"---\n\n")
                output_file.write(content)
                output_file.write("\n\n")
                dumped_paths.add(rel_path_key)
        except FileNotFoundError:
             print(f"Warning: File '{full_path}' not found during dump phase. Skipping.")
        except IsADirectoryError:
             print(f"Warning: Path '{full_path}' is a directory, not a file. Skipping dump.")
        except Exception as e:
            print(f"Error reading file {full_path}: {e}")
            output_file.write(f"---\n")
            output_file.write(f"File: {rel_path_key}\n")
            output_file.write(f"---\n\n")
            output_file.write(f"[Error reading file: {e}]\n\n")
            dumped_paths.add(rel_path_key)


def format_list_for_header(items):
    """Formats a list nicely for the header, wrapping lines."""
    if not items:
        return "  []"
    # Wrap items, indent subsequent lines
    return textwrap.fill(str(items), width=70, initial_indent='  ', subsequent_indent='  ')

def main():
    parser = argparse.ArgumentParser(description="Generate a project tree and dump selected file contents.")
    parser.add_argument("project_dir", help="Path to the project directory.")
    parser.add_argument("--config", default="config.json", help="Path to the configuration JSON file (default: config.json).")
    parser.add_argument("--output", default="project_dump.txt", help="Path to the output file (default: project_dump.txt).")

    args = parser.parse_args()
    project_dir = Path(args.project_dir)

    if not project_dir.is_dir():
        print(f"Error: Project directory '{args.project_dir}' not found or is not a directory.")
        return

    config, config_source_msg = load_config(args.config)
    ignored_dirs = config.get("ignored_dirs", []) # Should always exist
    allowed_extensions = config.get("allowed_extensions", []) # Should always exist

    print(f"Starting project dump for: {project_dir.resolve()}")
    print(f"Ignoring directories: {ignored_dirs}")
    print(f"Allowing extensions/files: {allowed_extensions}")
    print(f"Output file: {args.output}")

    tree_string, files_to_dump = build_tree(project_dir.resolve(), ignored_dirs, allowed_extensions)

    # Prepare header content
    header_content = f"""# Project Dump for: {project_dir.resolve()}
# Config Source: {config_source_msg}
#
# Ignored Directories:
{format_list_for_header(ignored_dirs)}
#
# Allowed Extensions/Files:
{format_list_for_header(allowed_extensions)}
"""

    if not tree_string and not files_to_dump:
        print("No files or directories found matching the criteria.")
        try:
            with open(args.output, 'w', encoding='utf-8') as outfile:
                 outfile.write(header_content) # Write header even if empty
                 outfile.write("\nNo files or directories found matching the criteria.\n")
            print(f"Empty dump file created: {args.output}")
        except Exception as e:
             print(f"\nError writing empty output file '{args.output}': {e}")
        return

    try:
        with open(args.output, 'w', encoding='utf-8') as outfile:
            outfile.write(header_content) # Write the detailed header
            outfile.write("\n" + "=" * 80 + "\n")
            outfile.write(" " * 30 + "DIRECTORY TREE\n")
            outfile.write("=" * 80 + "\n\n")
            outfile.write(tree_string)

            dump_files(project_dir.resolve(), files_to_dump, outfile)

        print(f"\nProject dump successfully created: {args.output}")
        print(f"Included {len(files_to_dump)} files in the dump.")

    except Exception as e:
        print(f"\nError writing output file '{args.output}': {e}")

if __name__ == "__main__":
    main()