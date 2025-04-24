import os
import argparse
import json

def load_config(config_path="config.json"):
    with open(config_path, "r") as f:
        return json.load(f)

def is_path_forced(path, forced_list):
    return any(os.path.normpath(path).startswith(os.path.normpath(p)) for p in forced_list)

def should_include(file_path, config, dumped_files):
    # Normalize path
    file_path = os.path.normpath(file_path)

    # Already dumped
    if file_path in dumped_files:
        return False

    # Check force exclude
    if is_path_forced(file_path, config.get("force_exclude", [])):
        return False

    # Check force include
    if is_path_forced(file_path, config.get("force_include", [])):
        return True

    # Filter by extension
    ext = os.path.splitext(file_path)[1]
    if ext and ext not in config.get("allowed_extensions", []):
        return False

    # Check ignored dirs
    for ignore_dir in config.get("ignored_dirs", []):
        if ignore_dir in file_path.split(os.sep):
            return False

    return True

def build_tree(start_path, prefix=""):
    tree_lines = []

    # List items and sort with folders first
    items = sorted(os.listdir(start_path), key=lambda x: (not os.path.isdir(os.path.join(start_path, x)), x.lower()))

    for index, item in enumerate(items):
        path = os.path.join(start_path, item)
        connector = "└── " if index == len(items) - 1 else "├── "
        tree_lines.append(prefix + connector + item)

        if os.path.isdir(path):
            extension = "    " if index == len(items) - 1 else "│   "
            tree_lines.extend(build_tree(path, prefix + extension))

    return tree_lines


def dump_file(file_path, output_file):
    output_file.write(f"File: {file_path}\n\n")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        output_file.write(content)
    except Exception as e:
        output_file.write(f"[Error reading file: {e}]\n")

def main():
    parser = argparse.ArgumentParser(description="Dump project files into a single text file.")
    parser.add_argument("directory", help="Path to the root directory to dump")
    parser.add_argument("--config", default="config.json", help="Path to the config file")
    parser.add_argument("--output", default="project_dump.txt", help="Output text file path")
    args = parser.parse_args()

    config = load_config(args.config)
    dumped_files = set()

    with open(args.output, "w", encoding="utf-8") as output_file:
        output_file.write("Project Tree:\n\n")
        output_file.write("\n".join(build_tree(args.directory)))

        for dirpath, _, filenames in os.walk(args.directory):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                if should_include(full_path, config, dumped_files):

                    output_file.write("\n\n" + "="*40 + "\n\n")

                    dump_file(full_path, output_file)
                    dumped_files.add(os.path.normpath(full_path))

                    

if __name__ == "__main__":
    main()
