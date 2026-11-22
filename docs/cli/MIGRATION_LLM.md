# Migration Assistant in Elevia with an LLM

Start with a folder containing your documents, including any subfolders. The
LLM will use file names and paths to propose an Elevia structure and generate
the commands needed to import the files.

The original files remain where they are. Import registers references to them;
it does not create copies.

This workflow creates tags and branches only. It does not analyze file
contents or assign attributes.

## 1. Create a file list

On macOS or Linux, open a terminal and run the following command, replacing
the folder path:

```bash
find "/full/path/to/folder" -type f \
  ! -name '.DS_Store' \
  > "$HOME/Desktop/files-to-import.txt"
```

This creates a file on your Desktop with one full path per line:

```text
/Users/mario/Documents/Work/Company/January payslip.pdf
/Users/mario/Documents/Health/Sports certificate.pdf
/Users/mario/Documents/Notes/Artificial intelligence.md
```

Choose a folder containing the documents you want to organize, not the entire
disk. File names containing newline characters cannot be represented reliably
in this list and need separate handling.

## 2. Prepare the LLM conversation

Attach:

- `files-to-import.txt`, created in the previous step;
- [CLI_COMMANDS.md](CLI_COMMANDS.md), containing the Elevia commands.

If you already have a structure in Elevia, also attach the output of:

```bash
elevia tags
elevia paths
```

File names and paths can contain personal information. Check what you are
sharing before sending them to an external LLM service.

## 3. Paste this prompt

```text
I want to organize my files in Elevia. Analyze the attachments and
prepare a single Bash script to create the structure and import the
files. Do not execute any commands.

ATTACHMENTS
- A list of files with full paths.
- CLI_COMMANDS.md: the only source for command syntax.
- Optional lists of tags and branches already present in Elevia.

HOW ELEVIA WORKS
- An Object is an abstract resource; currently only imported files create Objects.
  Each Object has a unique ID and a required, non-unique name.
- A Tag represents a concept with a unique name.
- A Branch puts a Tag in a context. It has one parent or is a root.
- The same Tag can appear in different branches, for example:
  Health.Medical certificates and Sports.Medical certificates.
- An object can be assigned to multiple branches.
- Children of a branch are not automatically shared with other
  branches of the same Tag.
- Cycles are not allowed, including cycles involving Tags through
  different branches.
- Importing does not move or delete the original file.

HOW TO DESIGN THE STRUCTURE
1. Use existing names and folders as clues, but do not automatically
   reproduce the filesystem structure.
2. Organize by subject and context, using a few main branches.
3. Create sub-branches only when they make documents easier to find.
4. Do not automatically create a tag for every file, year, extension
   or source folder.
5. Reuse existing tags and branches when appropriate.
6. Use multiple assignments when a document is useful in different
   contexts.
7. Do not assume a file's contents from its name. Leave ambiguous
   files out of the script and ask for clarification.
8. Do not treat files as duplicates just because their names are
   similar or identical.
9. Do not open files. Work only from the supplied list of names
   and paths.
10. Do not create attribute definitions or assign attribute values.

REQUIRED OUTPUT
A. A tree of proposed branches.
B. A complete table: original path → assigned branches.
C. Files requiring clarification and exclusions, with reasons.
D. Counts: files received, included in the script, requiring
   clarification and excluded. The counts must add up.
E. A single Bash script ready to save and run. Create the structure
   first, then import the files.
F. A few example find commands based on the proposed contexts.

SCRIPT RULES
- Use only commands documented in CLI_COMMANDS.md.
- Create parent branches before their children. Do not assume
  --create-tags creates intermediate branches.
- Do not recreate branches already present in the attached lists.
- Import each included path once with an explicit object name using --name.
  Treat the file path and object name as separate values.
- Use --in-name or --in-id for each
  necessary assignment; repeat the options for multiple branches.
- Every imported file must have at least one branch.
- Preserve original paths exactly and use safe Bash quoting, including
  for spaces, apostrophes and special characters.
- Use `set -euo pipefail` to stop on errors.
- Do not use reset, delete, move or rename commands.
- Do not create or assign attributes.
- Finish with `elevia tree` to show the resulting structure.
- Warn that the script may not be safe to rerun. After an error,
  check what was already created or imported before continuing.

If essential information is missing, ask for it before generating
the script. Do not claim complete coverage if the attached list is
truncated or cannot be read in full.
```

## 4. Review and run

Before running the script, review the **file → branch** table. A tree can
look organized even when assignments are wrong or documents are missing.

Save the approved script as `import-elevia.sh`, then run it with the Elevia CLI
available:

```bash
bash import-elevia.sh
```

The script creates the structure and imports the files. If it stops, **do not
immediately run it again from the beginning**: some operations may already
have succeeded.
