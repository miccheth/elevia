# Elevia Commands

Use a name or numeric ID to identify a tag, branch, or object. Elevia detects which one you provided. If a numeric name is ambiguous, Elevia asks for clarification.

Add `--force` to a modifying command to skip its preview and confirmation. Transaction and validation checks still apply.

## Tags

```bash
elevia tags

# Create a tag and place it at the root
elevia tag add "Ferrari"
elevia tag add "Ferrari" --description "Cars and models"

# Rename by name or ID
elevia tag rename "Ferrari" "Ferrari Cars"
elevia tag rename 1 "Ferrari Cars"

# Delete by name or ID
elevia tag delete "Ferrari"
elevia tag delete 1 --force
```

`Untagged` is a system tag with a single root branch. It cannot be used to
create another branch, such as `Elevia.Untagged`.

## Paths

```bash
elevia paths

# Add a path using tag names or IDs, from parent to child
elevia path add "Work.Ferrari"
elevia path add 1 2
elevia path add "Work.Ferrari.Contracts" --create-tags

# Move a path using its path or branch ID
elevia path move "Work.Ferrari" --to "Interests"
elevia path move 10 --to "Interests" --force

# Delete a path using its path or branch ID
elevia path delete "Work.Ferrari"
elevia path delete 10
```

For `path add`, numbers are **tag IDs**. For `path move` and `path delete`, a number is a **branch ID**.

## Objects

```bash
elevia objects

# Show or create an object
elevia object show "Document"
elevia object show 1
elevia object add "Document"
elevia object add "Document" --in "Work.Ferrari"

# Import a file
elevia object import "./document.pdf"
elevia object import "./document.pdf" --as "Document" --in "Work.Ferrari"
elevia object import "./document.pdf" --in "Work" --in "Interests"

# Rename or delete
elevia object rename 1 "New name"
elevia object delete 1 --force

# Assign, move or remove from a path
elevia object assign 1 "Work.Ferrari"
elevia object move 1 "Work.Ferrari" "Interests.Ferrari"
elevia object unassign 1 "Work.Ferrari"
```

If a name matches multiple objects or branches, Elevia asks for an ID or a full path.

## Tree

```bash
elevia tree
```

## Controlled Vocabulary

### Namespaces

```bash
elevia namespaces
elevia namespace add "photo" --description "Photo attributes"
elevia namespace add "work"

elevia namespace delete "photo"
elevia namespace delete 1 --force
```

### Attribute Definitions

```bash
# List all definitions or filter by namespace name or ID
elevia attr definitions
elevia attr definitions "photo"
elevia attr definitions 1

# Define attributes with a namespace
elevia attr define "photo.year" --type NUMBER
elevia attr define "photo.camera" --type TEXT
elevia attr define "work.remote" --type BOOLEAN
elevia attr define "work.status" --type ENUM --values "draft,in_review,approved,archived"

# Define attributes without a namespace
elevia attr define "color" --type TEXT
elevia attr define "price" --type NUMBER

# Delete by name or definition ID
elevia attr delete "photo.year"
elevia attr delete 10 --force
```

## Object Attributes

```bash
# Set values using object and attribute names or IDs
elevia object attr set "Document" "photo.year" 2025
elevia object attr set 1 10 2025
elevia object attr set 1 "work.status" "approved"
elevia object attr set 1 "work.remote" true
elevia object attr set 1 "color" "red"
elevia object attr set 1 "price" 1500.50

# Remove values
elevia object attr unset "Document" "photo.year"
elevia object attr unset 1 10
elevia object attr unset 1 "color"

# Show values
elevia object attr show "Document"
elevia object attr show 1
```

All attributes must be defined in the Controlled Vocabulary before use.

## Query

Put the expression in single quotes. Otherwise, the shell may interpret
`>` and `<` as redirections.

### Tags

```bash
elevia find 'tag:Ferrari'
elevia find 'tag:Work.Ferrari.Contracts'
elevia find 'tag:"Coop Receipts"'
elevia find 'tag:*'

elevia find '(tag:Ferrari) AND (tag:Photos)'
elevia find '(tag:Ferrari) OR (tag:Interests)'
elevia find '(tag:Ferrari) AND NOT (tag:Photos)'
```

### Attributes

```bash
# Equality and comparisons
elevia find 'photo.year = 2025'
elevia find 'work.status = "approved"'
elevia find 'price > 500'
elevia find 'work.deadline < "2025-12-31"'

# Combine conditions
elevia find '(tag:Ferrari) AND (photo.year = 2025)'
elevia find '(photo.year >= 2020) AND (photo.year <= 2025)'
```

## Reset

```bash
elevia reset
elevia reset --force
```

`--force` skips the preview and confirmation, but not validation or
transaction checks.