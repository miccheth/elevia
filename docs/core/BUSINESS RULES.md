# BUSINESS RULES

## OBJECT Rules (R1–R7)

- **R1:** A registered Object has at least one TAGGING. If unassigned, it is assigned to the default `Untagged` Tag.
- **R2:** Renaming an Object does not change its identity or associations.
- **R3:** Updating `file_path` preserves the Object's identity. The operation is automatic and requires user confirmation.
- **R4:** `is_available = 0` indicates an unavailable resource. The Object remains searchable in the database.
- **R5:** Removing an Object deletes its associations, not the original file.
- **R6:** Elevia must never modify, move, or delete original files. It only stores `file_path` and never changes the filesystem.
- **R7:** A removed Object's original resource remains accessible: removal affects only Elevia's logical layer, not the original resource.

## TAG Rules (R8–R12, R46–R48)

- **R8:** Tag names are unique and case insensitive.
- **R9:** Every Tag is created with a root Placement. If it is not placed under a parent, it remains visible on its own as a parent Tag.
- **R10:** Renaming a Tag does not break assignments to its Placements.
- **R11:** A Tag can be deleted only after all its non-root Placements have been resolved. Its empty root Placement is removed with the Tag.
- **R12:** No automatic alias is created for a retired Tag.
- **R46:** `Untagged` is a built-in Tag. It exists from the initial seed with `is_system = 1`, together with its root Placement. A system Tag can have only its root Placement and cannot be used to create additional Placements.
- **R47:** A Tag with `is_system = 1` cannot be renamed, deleted, or used as the source of a merge.
- **R48:** `Untagged` is not a shortcut for Objects without Tags. Its Placement is assigned when the last Tagging is removed (R1, R25).

## PLACEMENT Rules (R13–R21)

- **R13:** A Placement has at most one parent.
- **R14:** `parent_id = NULL` indicates a root Placement.
- **R15:** A Tag has at most one root Placement.
- **R16:** The same Tag can appear at most once under the same parent.
- **R17:** The same Tag can have multiple Placements in different contexts.
- **R18:** Children are not automatically shared between Placements of the same Tag.
- **R19:** Moving a Placement preserves its identity, descendants, and assignments. A branch cannot be moved into itself or one of its descendants.
- **R20:** A Placement can be deleted only if it has no children and no assignments. Recursive deletion is not automatic.
- **R21:** Adding a Placement creates an empty Placement without copying anything. Moving a Placement where the same Tag already exists is not allowed without an explicit conflict.

## TAGGING Rules (R22–R29)

- **R22:** The pair `(object_id, placement_id)` is unique.
- **R23:** No global assignment exists without a Placement.
- **R24:** An Object can have multiple Taggings assigned to different Placements.
- **R25:** When an Object's last Tagging is removed, the Object is assigned to `Untagged`.
- **R26:** A transfer requires an existing source assignment. An Object cannot be transferred from a context where it is not assigned.
- **R27:** A nonexistent destination or Object results in an error.
- **R28:** Operations with no effect do not create new assignments.
- **R29:** Contexts are not synchronized automatically. A suggestion does not become an assignment without explicit confirmation.

## ATTRIBUTE NAMESPACE Rules (R49–R52)

- **R49:** Namespace names are unique and case insensitive.
- **R50:** A namespace can exist without definitions as an empty template.
- **R51:** Deleting a namespace deletes all its definitions and their values on Objects (CASCADE).
- **R52:** Renaming a namespace does not break values on Objects. The name is denormalized in `OBJECT_ATTRIBUTE.namespace`.

## ATTRIBUTE DEFINITION Rules (R53–R57)

- **R53:** The pair `(namespace_id, key)` is unique: each key can appear at most once per namespace.
- **R54:** The `ENUM` type requires `allowed_values` to be a non-empty JSON array.
- **R55:** The `TEXT`, `NUMBER`, `DATE`, and `BOOLEAN` types do not use `allowed_values`; it must be NULL.
- **R56:** Deleting a definition deletes the values on Objects that use it (CASCADE).
- **R57:** Changing a definition's type does not convert existing values; handling them is the user's responsibility.

## OBJECT_ATTRIBUTE Rules (R58–R65)

- **R58:** Attributes can be **namespaced** (defined in a template) or **free** (without a namespace, with `definition_id = NULL` and `namespace = NULL`).
- **R59:** For namespaced attributes, the definition must exist before assignment.
- **R60:** For free attributes, the type is **automatically inferred** from the value on the first assignment.
- **R61:** An Object can have only one value per key, with or without a namespace: `UNIQUE (object_id, namespace, key)`.
- **R62:** Values are validated against their type when assigned.
- **R63:** For `ENUM` attributes, the value must be one of the defined `allowed_values`.
- **R64:** Deleting an Object deletes all its attributes (CASCADE).
- **R65:** Attributes are independent of Tags and Placements. They can be used in global queries or queries limited to a branch.

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

- **R74:** No cycles are allowed between Placements. A Placement cannot be
  its own parent or the parent of one of its ancestors.
- **R75:** No cycles are allowed between Tag identities. The global graph
  must be acyclic.
- **R76:** A→B and B→A cannot coexist, even in separate contexts.
- **R77:** Deleting a link does not delete other equivalent links. Automatically
  merging two branches with the same Tag is forbidden. Merging two Tags when
  the substitution would create a cycle is also forbidden. A merge always
  requires an explicit choice.
- **R78:** Each confirmed plan is executed as a single transaction
  (all-or-nothing).
- **R79:** If any rule (R1–R84) is violated or an error occurs, no part of
  the plan is applied.
- **R80:** Structural changes require a preview showing their impact and
  conflicts.
- **R81:** A preview does not modify data and does not count as confirmation.
- **R82:** Upon confirmation, the TransactionManager rechecks references,
  constraints (R1–R84), and the state used for the preview.
- **R83:** If data has changed since the preview, confirmation is rejected.
- **R84:** Concurrent operations cannot bypass constraints (database lock).
  Conflicts cannot be resolved automatically without an explicit user choice.