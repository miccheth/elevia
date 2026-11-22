# Elevia Commands

See [Business Rules](../core/BUSINESS_RULES.md) and [Query](../core/QUERY.md) for the underlying rules.

## Reading commands

In a syntax line, replace `<name>` with a value. Square brackets mark an optional argument; do not type the brackets or angle brackets. For example:

```text
elevia tag add --name "<name>" [--description "<text>"]
```

```bash
elevia tag add --name "Ferrari"
elevia tag add --name "Ferrari" --description "Cars and models"
```

Put text values, including names, paths, and descriptions, in double quotes. Type keywords such as `TEXT` and `NUMBER` are written without quotes. The shell splits unquoted arguments at spaces:

```bash
elevia tag add --name "Ferrari Cars"
elevia object import "./purchase contract.pdf" --name "Purchase contract"
```

The shell removes these quotes before passing values to Elevia; they are not part of the name. Query expressions have additional quoting rules; see [Search](#search).

Choose `--name` for a name and `--id` for a numeric ID when identifying tags, branches, or other supported resources. Objects are identified only by ID after import. When a command has multiple references, use role-specific options such as `--from-name` or `--from-id`. Select one form for each reference. If a branch name is ambiguous, use its ID or full path.

A **tag** is a named concept. A **branch** is a tag's position in a tree, and a **path** identifies that position with tag names separated by dots, such as `Work.Ferrari`. The same tag can appear in different branches.

Modifying commands proceed without a preview or confirmation. The system checks references and business rules before applying changes in a transaction. If validation fails or an error occurs, none of the changes are applied. There is no `--force` option.

The Desktop interface provides a preview and confirmation for structural changes; the CLI does not. See [Business Rules](../core/BUSINESS_RULES.md).

## Tags

```text
elevia tags
elevia tag add --name "<name>" [--description "<text>"]
elevia tag rename (--name "<name>" | --id <id>) --to "<new-name>"
elevia tag delete (--name "<name>" | --id <id>)
```

Parentheses and `|` indicate alternatives; do not type them. Choose exactly one of `--name` and `--id`. Adding a tag also creates its root branch. Tag names are unique, ignoring case. Renaming a tag preserves its branch assignments; it does not create an alias for the old name.

```bash
elevia tags
elevia tag add --name "Ferrari"
elevia tag add --name "Ferrari Cars" --description "Cars and models"
elevia tag rename --name "Ferrari" --to "Ferrari Cars"
elevia tag rename --id 1 --to "Ferrari Cars"
elevia tag delete --name "Ferrari"
elevia tag delete --id 1
```

A tag can be deleted only after its non-root branches have been resolved; its root branch must be empty. The system tag `Untagged` cannot be renamed or deleted. It has one root branch and cannot be added beneath another tag.

## Paths

```text
elevia paths
elevia path add (--name "<path>" | --tag-id <id> ...) [--create-tags]
elevia path move (--name "<path>" | --id <branch-id>) (--to-name "<path>" | --to-id <branch-id>)
elevia path delete (--name "<path>" | --id <branch-id>)
```

For `path add`, provide a dotted path with `--name` or repeat `--tag-id` for each tag ID, from parent to child. `--create-tags` permits missing tags to be created. For `path move` and `path delete`, a number identifies a **branch**, not a tag.

An existing tag can appear in different branches, but only once under the same parent. Adding a branch does not copy children or assignments from another branch of the same tag.

```bash
elevia paths
elevia path add --name "Work.Ferrari"
elevia path add --tag-id 1 --tag-id 2
elevia path add --name "Work.Ferrari.Contracts" --create-tags
elevia path move --name "Work.Ferrari" --to-name "Interests"
elevia path move --id 10 --to-name "Interests"
elevia path delete --name "Work.Ferrari"
elevia path delete --id 10
```

Moving a branch preserves its descendants and object assignments. A branch cannot be moved into itself or one of its descendants; cycles and conflicting branches are not allowed. A branch can be deleted only when it has no children or assignments. Deletion is not recursive.

Cycles between tag identities are also forbidden across different branches: if `A` is under `B`, `B` cannot be under `A` elsewhere.

## Objects

### List, show, and create

```text
elevia objects
elevia object show --id <id>
elevia object import "<file-path>" --name "<name>" [--in-name "<path>" | --in-id <branch-id>] ...
```

Importing a file is currently the only way to create an object. `--name` supplies a required label; the file path and object name are separate, and names need not be unique. After import, use the object's ID in commands. `elevia objects` lists object IDs and names. `--in-name` or `--in-id` selects a branch; repeat either option to assign the object to more than one branch. An object without another assignment is assigned to `Untagged`.

```bash
elevia objects
elevia object show --id 1
elevia object import "./document.pdf" --name "Document"
elevia object import "./document.pdf" --name "Document" --in-name "Work.Ferrari"
elevia object import "./document.pdf" --name "Document" --in-name "Work" --in-name "Interests"
```

File imports register a reference to the original external file, not a copy. The original is not moved or modified. If the file changes during a read, Elevia discards results from the inconsistent read and retries or reports an error. See [Business Rules](../core/BUSINESS_RULES.md).

### Rename and delete

```text
elevia object rename --id <id> --to "<new-name>"
elevia object delete --id <id>
```

```bash
elevia object rename --id 1 --to "New name"
elevia object delete --id 1
```

Renaming preserves the object's identity and associations. Deleting an object removes its assignments and attributes, not the original file.

### Assignments

```text
elevia object assign --id <id> (--to-name "<path>" | --to-id <branch-id>)
elevia object move --id <id> (--from-name "<path>" | --from-id <branch-id>) (--to-name "<path>" | --to-id <branch-id>)
elevia object unassign --id <id> (--from-name "<path>" | --from-id <branch-id>)
```

```bash
elevia object assign --id 1 --to-name "Work.Ferrari"
elevia object move --id 1 --from-name "Work.Ferrari" --to-name "Interests.Ferrari"
elevia object move --id 1 --from-id 10 --to-id 20
elevia object unassign --id 1 --from-name "Work.Ferrari"
```

An object can be assigned to multiple branches. A move requires an existing assignment at the source and an existing destination. Removing the last assignment places the object in `Untagged`. The same object cannot have duplicate assignments to the same branch. An unknown object or destination causes an error; assignments in other contexts are not synchronized automatically.

## Tree

Display the tag branch structure:

```bash
elevia tree
```

## Controlled Vocabulary

Define attributes in the controlled vocabulary before assigning them to an object. A namespace is an optional group of attribute definitions that can be reused as a template. Attributes without a namespace are also defined in the vocabulary, but stand on their own outside any group. Creating an object or setting an attribute does not invent a namespace or attribute definition.

Assign a namespace to an object as a whole, not as individual definitions. Its attribute values can be filled in later. An attribute without a namespace can be set individually after its definition exists.

### Namespaces

Namespaces group attribute definitions, such as `photo.year`. They are independent of tags and paths. Create the namespace `photo` before defining `photo.year`; creating the namespace alone does not define any attributes.

```text
elevia namespaces
elevia namespace add --name "<name>" [--description "<text>"]
elevia namespace delete (--name "<name>" | --id <id>)
```

Namespace names are unique, ignoring case. Deleting a namespace also deletes its assignments, definitions, and their values on objects.

```bash
elevia namespaces
elevia namespace add --name "photo" --description "Photo attributes"
elevia namespace add --name "work"
elevia namespace delete --name "photo"
elevia namespace delete --id 1
```

### Attribute definitions

```text
elevia attr definitions [--namespace-name "<name>" | --namespace-id <id>]
elevia attr define --name "<attribute>" --type <type> [--value-type <primitive-type> --values '<json-array>']
elevia attr delete (--name "<attribute>" | --id <id>)
```

Filter definitions by namespace name or ID. A namespace is optional: an attribute can belong to a namespace, as in `photo.year`, or have no namespace, as in `color`. In both cases, define the attribute in the controlled vocabulary before assigning a value. A namespace must exist before defining an attribute inside it.

The primitive types are `TEXT`, `NUMBER`, `DATE`, and `BOOLEAN`. An `ENUM` requires `--value-type` to declare one of these primitive types and `--values` to provide a non-empty JSON array. Every value must match that type; mixed types are not allowed. Dates are strings in `YYYY-MM-DD` format, numbers are JSON numbers, and Boolean values are `true` or `false`. Other attribute types do not use `--value-type` or `--values`. Enclose the JSON array in single quotes so the shell preserves the double quotes inside it.

```bash
elevia attr definitions
elevia attr definitions --namespace-name "photo"
elevia attr definitions --namespace-id 1
elevia namespace add --name "photo"
elevia namespace add --name "work"
elevia namespace add --name "review"
elevia attr define --name "photo.year" --type NUMBER
elevia attr define --name "photo.camera" --type TEXT
elevia attr define --name "work.remote" --type BOOLEAN
elevia attr define --name "work.status" --type ENUM --value-type TEXT --values '["draft","in_review","approved","archived"]'
elevia attr define --name "rating" --type ENUM --value-type NUMBER --values '[1,2,3]'
elevia attr define --name "review.date" --type ENUM --value-type DATE --values '["2026-01-01","2026-06-01"]'
elevia attr define --name "published" --type ENUM --value-type BOOLEAN --values '[true,false]'
elevia attr define --name "color" --type TEXT
elevia attr define --name "price" --type NUMBER
elevia attr delete --name "photo.year"
elevia attr delete --id 10
```

Deleting a definition also deletes object values that use it. Attribute keys must be unique within a namespace.

## Object attributes

```text
elevia object namespace assign --id <object-id> (--namespace-name "<namespace>" | --namespace-id <id>)
elevia object attr set --id <object-id> (--attr-name "<attribute>" | --attr-id <id>) (<value> | --null)
elevia object attr unset --id <object-id> (--attr-name "<attribute>" | --attr-id <id>)
elevia object attr show --id <object-id>
```

Define attributes in the controlled vocabulary before using them in these CLI commands. Before setting a namespaced attribute, assign the entire namespace to the object. An applicable attribute defaults to `NULL` until a value is supplied. Use `--null` to set it to `NULL` explicitly, or use `unset` to restore that state. The text value `"NULL"` remains text: shell quotes alone cannot distinguish it from an unquoted argument. Non-null values must match the attribute type; an `ENUM` value must be in its allowed list, with the same type. For example, numeric `1` and text `"1"` are different values. An object has at most one value per attribute. Attributes belong to the object, independently of its branch assignments.

For an attribute without a namespace, define it and then set its value:

```bash
elevia attr define --name "color" --type TEXT
elevia object attr set --id 1 --attr-name "color" "red"
```

For an attribute with a namespace, create `photo`, define its attributes, assign the whole namespace, and set values when ready:

```bash
elevia namespace add --name "photo"
elevia attr define --name "photo.year" --type NUMBER
elevia attr define --name "photo.camera" --type TEXT
elevia object namespace assign --id 1 --namespace-name "photo"
elevia object attr set --id 1 --attr-name "photo.year" 2025
```

Attributes without a namespace also require a definition; their type is not inferred from the first value.

The following examples assume the relevant namespaces have already been assigned to the object:

```bash
elevia object attr set --id 1 --attr-name "photo.year" 2025
elevia object attr set --id 1 --attr-id 10 2025
elevia object attr set --id 1 --attr-name "work.status" "approved"
elevia object attr set --id 1 --attr-name "rating" 1
elevia object attr set --id 1 --attr-name "work.remote" true
elevia object attr set --id 1 --attr-name "color" "red"
elevia object attr set --id 1 --attr-name "price" 1500.50
elevia object attr set --id 1 --attr-name "photo.year" --null
elevia object attr unset --id 1 --attr-name "photo.year"
elevia object attr unset --id 1 --attr-id 10
elevia object attr show --id 1
```

## Search

```text
elevia find <expression>
```

Wrap the whole expression in single quotes so the shell does not interpret characters such as `>` and `<` as redirections. Inside the expression, use double quotes for names and for text, text-enum, and date values. Query names use the query syntax rather than `--name` or `--id` options.

```bash
elevia find 'tag:"Ferrari"'
elevia find 'tag:"Work"."Ferrari"."Contracts"'
elevia find 'tag:"Coop Receipts"'
elevia find 'tag:*'
elevia find '(tag:"Ferrari") AND (tag:"Photos")'
elevia find '(tag:"Ferrari") OR (tag:"Interests")'
elevia find '(tag:"Ferrari") AND NOT (tag:"Photos")'
elevia find '"photo"."year" = 2025'
elevia find '"work"."status" = "approved"'
elevia find '"rating" = 1'
elevia find '"price" > 500'
elevia find '"work"."deadline" < "2025-12-31"'
elevia find '(tag:"Ferrari") AND ("photo"."year" = 2025)'
elevia find '("photo"."year" >= 2020) AND ("photo"."year" <= 2025)'
```

`tag:*` includes objects in `Untagged`. Tag searches include matching branches and their descendants. Use `=`, `!=`, `>`, `<`, `>=`, or `<=` for attribute comparisons; ordering comparisons apply only to `NUMBER` and `DATE`. Dates use `YYYY-MM-DD`; Boolean values are `true` or `false`. Search is read-only. See [Query](../core/QUERY.md) for the grammar and matching rules.

Search rules:

- A tag path matches consecutive names anywhere in a branch path. For example,
  `tag:Ferrari.Contracts` can match `Work.Ferrari.Contracts` and its
  descendants. Use the longer path to restrict the context.
- Tag names and attribute keys are compared without regard to case. Each object
  appears at most once in the results.
- `NOT` takes precedence over `AND`, which takes precedence over `OR`. Use
  parentheses to make grouping explicit, for example
  `'((tag:"Ferrari") OR (tag:"Interests")) AND (tag:"Contracts")'`.
- An invalid query or a condition using a nonexistent namespace produces an
  error, not partial results. A nonexistent free attribute returns no results.
- Text and date enum values are double-quoted inside the expression; numeric
  and Boolean enum values are not. Numbers are integers or decimals, dates are double-quoted,
  and Boolean values are `true` or `false`. Values incompatible with the
  attribute type produce an error.

## Reset

```bash
elevia reset
```

Reset proceeds without preview or confirmation, subject to validation and transaction checks.
