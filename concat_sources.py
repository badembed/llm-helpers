#!/usr/bin/env python3
import argparse
import pathlib
import sys

# Default source file extensions – adjust as needed
DEFAULT_EXTS = {
    ".c", ".h", ".cpp", ".hpp",
    ".cc", ".hh", ".py", ".js",
    ".ts", ".java", ".cs",
    ".go", ".rs", ".php",
    ".html", ".css"
}


def is_source_file(path: pathlib.Path, exts) -> bool:
    if not path.is_file():
        return False
    if exts is None:  # if exts is None, accept all files
        return True
    return path.suffix.lower() in exts


def collect_files(folder: pathlib.Path, recursive: bool, exts):
    if recursive:
        it = folder.rglob("*")
    else:
        it = folder.glob("*")

    files = [p for p in it if is_source_file(p, exts)]
    # Sort for deterministic output
    files.sort(key=lambda p: str(p).lower())
    return files


def make_big_file(files, output_path: pathlib.Path, base_folder: pathlib.Path):
    with output_path.open("w", encoding="utf-8") as out:
        for i, path in enumerate(files, start=1):
            # Relative name from base folder for nicer headings
            rel_name = path.relative_to(base_folder)

            # Write heading
            out.write(f"## {rel_name}\n")
            out.write("```" + "\n")

            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # Fallback: read as binary and replace undecodable bytes
                text = path.read_text(encoding="utf-8", errors="replace")

            out.write(text.rstrip("\n") + "\n")
            out.write("```" + "\n\n")

    print(f"Wrote {len(files)} files into: {output_path}")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Create a big Markdown file that contains all source files from a folder."
    )
    parser.add_argument(
        "folder",
        help="Folder containing source files."
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: <folder>/all_sources.md).",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recurse into subdirectories."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include ALL files (ignore extensions)."
    )
    parser.add_argument(
        "--ext",
        action="append",
        metavar="EXT",
        help=(
            "File extension to include (e.g. --ext .c --ext .h). "
            "If given, overrides the default extension list."
        ),
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    folder = pathlib.Path(args.folder).resolve()
    if not folder.is_dir():
        print(f"Error: {folder} is not a directory.", file=sys.stderr)
        return 1

    # Determine extensions to use
    if args.all:
        exts = None
    elif args.ext:
        exts = {e if e.startswith(".") else "." + e for e in args.ext}
    else:
        exts = DEFAULT_EXTS

    # Determine output file path
    if args.output:
        output_path = pathlib.Path(args.output).resolve()
    else:
        output_path = folder / "all_sources.md"

    files = collect_files(folder, recursive=args.recursive, exts=exts)
    if not files:
        print("No matching source files found.", file=sys.stderr)
        return 1

    make_big_file(files, output_path, base_folder=folder)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
