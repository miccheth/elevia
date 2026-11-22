# BUSINESS RULES

The rules below describe the model and intended file-reading behavior.

## File Import and Reading Rules

- Import registers a reference to the original external file. Elevia does not create a managed copy, move the file, or modify it.
- The user continues working on the original file. Subsequent reads use that file rather than a stored snapshot.
- If a change is detected during a read, Elevia discards results from that read and retries or reports an error. It must not treat a detected inconsistent read as successful.
- If a file is moved, deleted, or inaccessible, its Object remains registered and searchable, and the file is marked unavailable.
- Removing an Object removes its Elevia data but does not delete or modify the original file.

## OBJECT Rules (R1–R7)

- `Object` is an abstract base. Currently, objects are created only by importing files. Each object has a unique ID and a required name used as a non-unique label; its file path is separate from its name.
- **R1:** A registered Object has at least one TAGGING. If unassigned, it is assigned to the default `Untagged` Tag.
- **R2:** Renaming an Object does not change its identity or associations.
- **R3:** Updating `file_path` preserves the Object's identity. The operation is automatic and requires user confirmation.
- **R4:** `is_available = 0` indicates an unavailable resource. The Object remains searchable in the database.
- **R5:** Removing an Object deletes its associations, not the original file.
- **R6:** Elevia must never modify, move, or delete original files. It only stores `file_path` and never changes the filesystem.
- **R7:** A removed Object's original resource remains accessible: removal affects only Elevia's logical layer, not the original resource.

## TAG Rules (R8–R12, R46–R48)

- **R8:** Tag names are unique and case insensitive.
- **R9:** Every Tag is created with a root Branch. If it is not placed under a parent, it remains visible on its own as a parent Tag.
- **R10:** Renaming a Tag does not break assignments to its Branches.
- **R11:** A Tag can be deleted only after all its non-root Branches have been resolved. Its empty root Branch is removed with the Tag.
- **R12:** No automatic alias is created for a retired Tag.
- **R46:** `Untagged` is a built-in Tag. It exists from the initial seed with `is_system = 1`, together with its root Branch. A system Tag can have only its root Branch and cannot be used to create additional Branches.
- **R47:** A Tag with `is_system = 1` cannot be renamed, deleted, or used as the source of a merge.
- **R48:** `Untagged` is not a shortcut for Objects without Tags. Its Branch is assigned when the last Tagging is removed (R1, R25).

## BRANCH Rules (R13–R21)

- **R13:** A Branch has at most one parent.
- **R14:** `parent_id = NULL` indicates a root Branch.
- **R15:** A Tag has at most one root Branch.
- **R16:** The same Tag can appear at most once under the same parent.
- **R17:** The same Tag can have multiple Branches in different contexts.
- **R18:** Children are not automatically shared between Branches of the same Tag.
- **R19:** Moving a Branch preserves its identity, descendants, and assignments. A branch cannot be moved into itself or one of its descendants.
- **R20:** A Branch can be deleted only if it has no children and no assignments. Recursive deletion is not automatic.
- **R21:** Adding a Branch creates an empty Branch without copying anything. Moving a Branch where the same Tag already exists is not allowed without an explicit conflict.

## TAGGING Rules (R22–R29)

- **R22:** The pair `(object_id, branch_id)` is unique.
- **R23:** No global assignment exists without a Branch.
- **R24:** An Object can have multiple Taggings assigned to different Branches.
- **R25:** When an Object's last Tagging is removed, the Object is assigned to `Untagged`.
- **R26:** A transfer requires an existing source assignment. An Object cannot be transferred from a context where it is not assigned.
- **R27:** A nonexistent destination or Object results in an error.
- **R28:** Operations with no effect do not create new assignments.
- **R29:** Contexts are not synchronized automatically. A suggestion does not become an assignment without explicit confirmation.

## ATTRIBUTE NAMESPACE Rules (R49–R52)

- **R49:** Namespace names are unique and case insensitive.
- **R50:** A namespace can exist without definitions as an empty template. It is assigned to an Object as a whole, not as individual definitions; its attribute values default to NULL and may be supplied later.
- **R51:** Deleting a namespace deletes its Object assignments, all its definitions, and their values on Objects (CASCADE).
- **R52:** Renaming a namespace does not break values on Objects. The name is denormalized in `OBJECT_ATTRIBUTE.namespace`.

## ATTRIBUTE DEFINITION Rules (R53–R57)

- **R53:** Each key can appear at most once within a namespace, or once among definitions without a namespace.
- **R54:** The `ENUM` type requires an explicit primitive value type (`TEXT`, `NUMBER`, `DATE`, or `BOOLEAN`) and a non-empty JSON array of allowed values. Every value must match the declared type; mixed types are not allowed. Dates use `YYYY-MM-DD` strings.
- **R55:** The `TEXT`, `NUMBER`, `DATE`, and `BOOLEAN` types do not use an enum value type or `allowed_values`; both must be NULL.
- **R56:** Deleting a definition deletes the values on Objects that use it (CASCADE).
- **R57:** Changing a definition's type does not convert existing values; handling them is the user's responsibility.

## OBJECT_ATTRIBUTE Rules (R58–R65)

- **R58:** Attributes can be **namespaced** (grouped in a reusable template) or **free** (without a namespace). Both have a definition in the controlled vocabulary.
- **R59:** Every attribute definition must exist before assignment, whether or not it belongs to a namespace. A namespace must exist before an attribute is defined within it and must be assigned to the Object as a whole before any of its values can be set.
- **R60:** An attribute's type is specified in its definition, not inferred when a value is first assigned. Creating an Object or assigning a value does not create an attribute definition or namespace.
- **R61:** An Object can have only one value per key, with or without a namespace: `UNIQUE (object_id, namespace, key)`.
- **R62:** An applicable attribute defaults to NULL when no value is assigned; NULL may also be assigned explicitly. Unsetting a value restores NULL. Non-NULL values are validated against their definition's type when assigned.
- **R63:** For `ENUM` attributes, a non-NULL value must match the declared primitive value type and be one of the defined `allowed_values`. NULL is permitted independently of that list. A number and a string containing the same digits are distinct.
- **R64:** Deleting an Object deletes all its attributes (CASCADE).
- **R65:** Attributes are independent of Tags and Branches. They can be used in global queries or queries limited to a branch.

### QUERY Rules (R66–R73)

- **R66:** A query is read-only: it does not write data, open transactions, or pass through the TransactionManager.
- **R67:** An invalid query produces an explicit error, never a partial result.
- **R68:** Each Object appears only once in the results, even if it satisfies multiple conditions.
- **R69:** Tag name comparisons are case insensitive (R8).
- **R70:** `tag:*` matches all registered Objects, including those assigned to `Untagged`.
- **R71:** Attribute key comparisons are case insensitive.
- **R72:** The operators `>`, `<`, `>=`, and `<=` are allowed only for `NUMBER` or `DATE` attributes. They produce an error for other types.
- **R73:** A condition on an attribute in a nonexistent namespace produces an error. A condition on a nonexistent free attribute returns zero results.

## TRANSACTION and VALIDATION Rules (R74–R84)

The **TransactionManager** enforces all business rules (R1–R84). Every
operation passes through it: it validates the proposed state against all
rules and executes the transaction only if all rules are satisfied
(all-or-nothing).

- **R74:** No cycles are allowed between Branches. A Branch cannot be its own parent or the parent of one of its ancestors.
- **R75:** No cycles are allowed between Tag identities. The global graph must be acyclic.
- **R76:** A→B and B→A cannot coexist, even in separate contexts.
- **R77:** Deleting a link does not delete other equivalent links. Automatically merging two branches with the same Tag is forbidden. Merging two Tags when the substitution would create a cycle is also forbidden. A merge always requires an explicit choice.
- **R78:** Each executed plan, whether confirmed in Desktop or submitted through the CLI, is executed as a single transaction (all-or-nothing).
- **R79:** If any rule (R1–R84) is violated or an error occurs, no part of the plan is applied.
- **R80:** The Desktop interface provides a preview of structural changes, showing their impact and conflicts, before confirmation. CLI commands proceed without a preview or confirmation, subject to the same validation and transaction checks.
- **R81:** A preview does not modify data and does not count as confirmation.
- **R82:** For a Desktop preview, upon confirmation the TransactionManager rechecks references, constraints (R1–R84), and the state used for the preview. CLI operations check references and constraints before execution.
- **R83:** If data has changed since a Desktop preview, confirmation is rejected.
- **R84:** Concurrent operations cannot bypass constraints (database lock). Conflicts cannot be resolved automatically without an explicit user choice.
