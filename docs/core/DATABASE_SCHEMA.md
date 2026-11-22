# DATABASE RELATIONSHIP SCHEMA

This schema describes the external-file model. Import records a reference to
the original file; it does not create a managed copy.

`Object` is the abstract base for resource types. The current scope supports
only file objects; a generic base is not a separately creatable object type.

```text
Object
├── id                 bigint      PK, auto increment, not null
├── name               string      not null
├── object_type        string      not null: LOCAL_FILE
├── created_at         timestamp   not null
├── updated_at         timestamp   not null
│
├── Local File Object              exactly 1 per current Object
│   ├── object_id      bigint      PK, FK → Object.id, not null
│   ├── is_available   boolean     not null
│   ├── file_path      text        not null
│   ├── normalized_path text       not null
│   ├── file_size      bigint      not null
│   ├── modified_at    timestamp   not null
│   └── file_extension string      not null
│
├── Object Namespace               0 or more namespace assignments
│   ├── object_id      bigint      FK → Object.id, not null
│   └── namespace_id   bigint      FK → Attribute Namespace.id, not null
│
├── Tagging                        0 or more assignments
│   ├── id             bigint      PK, auto increment, not null
│   ├── object_id      bigint      FK → Object.id, not null
│   ├── branch_id   bigint      FK → Branch.id, not null
│   └── created_at     timestamp   not null
│
└── Object Attribute               0 or more attributes
    ├── id             bigint      PK, auto increment, not null
    ├── object_id      bigint      FK → Object.id, not null
    ├── definition_id  bigint      FK → Attribute Definition.id, not null
    ├── namespace      string      denormalized copy, nullable
    ├── key            string      not null
    ├── value          text        not null
    ├── value_type     string      not null: TEXT | NUMBER | DATE | BOOLEAN | ENUM
    └── created_at     timestamp   not null


Tag Registry
└── Tag                            identity of the Tag
    ├── id             bigint      PK, auto increment, not null
    ├── name           string      unique, not null, case insensitive
    ├── description    text        nullable
    ├── is_system      boolean     not null, default 0
    ├── created_at     timestamp   not null
    ├── updated_at     timestamp   not null
    │
    └── Branch                  0 or more branches of the Tag
        ├── id         bigint      PK, auto increment, not null
        ├── tag_id     bigint      FK → Tag.id, not null
        ├── parent_id  bigint      FK → Branch.id, nullable
        ├── created_at timestamp   not null
        ├── parent                 0 or 1 parent Branch
        ├── children               0 or more child Branches
        └── taggings               0 or more assignments to Objects


Attribute Registry
├── Attribute Namespace
    ├── id             bigint      PK, auto increment, not null
    ├── name           string      unique, not null, case insensitive
    ├── description    text        nullable
    ├── created_at     timestamp   not null
    │
└── Attribute Definition           0 or more definitions
    ├── id             bigint      PK, auto increment, not null
    ├── namespace_id   bigint      FK → Attribute Namespace.id, nullable
    ├── key            string      not null
    ├── value_type     string      not null: TEXT | NUMBER | DATE | BOOLEAN | ENUM
    ├── enum_value_type string     nullable: TEXT | NUMBER | DATE | BOOLEAN for ENUM
    ├── allowed_values text        nullable, JSON array matching enum_value_type
    ├── description    text        nullable
    ├── created_at     timestamp   not null
    └── object_attributes          0 or more attributes using the definition
```

An applicable attribute with no stored `Object Attribute` row has the default
value NULL. Explicitly setting NULL or unsetting a value removes its value row;
the attribute definition and any namespace assignment remain. A stored row
represents a non-NULL value. This does not make an unassigned namespace
applicable to an Object.

## Database Constraints (Schema Level)

- **Primary keys:** `OBJECT.id`, `TAG.id`, `BRANCH.id`, `TAGGING.id`,
  `ATTRIBUTE_NAMESPACE.id`, `ATTRIBUTE_DEFINITION.id`, `OBJECT_ATTRIBUTE.id`
  — auto-increment, NOT NULL; IDs may be reused after `delete()` (internal to the Core).

- **Foreign keys with referential integrity:** references to nonexistent rows are rejected.
  - `LOCAL_FILE_OBJECT.object_id` → `OBJECT.id` (PK and FK, 1:1)
  - `BRANCH.tag_id` → `TAG.id` (NOT NULL)
  - `BRANCH.parent_id` → `BRANCH.id` (NULLABLE; NULL = root; at most one parent)
  - `TAGGING.object_id` → `OBJECT.id` (NOT NULL)
  - `TAGGING.branch_id` → `BRANCH.id` (NOT NULL)
  - `ATTRIBUTE_DEFINITION.namespace_id` → `ATTRIBUTE_NAMESPACE.id` (NULLABLE; NULL = no namespace)
  - `OBJECT_ATTRIBUTE.object_id` → `OBJECT.id` (NOT NULL)
  - `OBJECT_NAMESPACE.object_id` → `OBJECT.id` (NOT NULL)
  - `OBJECT_NAMESPACE.namespace_id` → `ATTRIBUTE_NAMESPACE.id` (NOT NULL)
  - `OBJECT_ATTRIBUTE.definition_id` → `ATTRIBUTE_DEFINITION.id`
    (NOT NULL; all attributes use a definition)

- **UNIQUE:**
  - `TAG.name` — NOT NULL, case insensitive
  - `BRANCH (tag_id, parent_id)` — at most one Branch per Tag under the same parent
  - `BRANCH (tag_id) WHERE parent_id IS NULL` — at most one root Branch per Tag
  - `TAGGING (object_id, branch_id)` — an Object can appear at most once in a Branch
  - `OBJECT_NAMESPACE (object_id, namespace_id)` — a namespace can be assigned at most once per Object
  - `ATTRIBUTE_NAMESPACE.name` — NOT NULL, case insensitive
  - `ATTRIBUTE_DEFINITION (namespace_id, key) WHERE namespace_id IS NOT NULL` — each key can appear at most once per namespace
  - `ATTRIBUTE_DEFINITION (key) WHERE namespace_id IS NULL` — each key can appear at most once without a namespace
  - `OBJECT_ATTRIBUTE (object_id, namespace, key) WHERE namespace IS NOT NULL` — at most one value per object and namespaced key
  - `OBJECT_ATTRIBUTE (object_id, key) WHERE namespace IS NULL` — at most one value per object and key without a namespace

- **NOT NULL:** all schema fields except `TAG.description`, `BRANCH.parent_id`,
  `ATTRIBUTE_NAMESPACE.description`, `ATTRIBUTE_DEFINITION.namespace_id`,
  `ATTRIBUTE_DEFINITION.enum_value_type`, `ATTRIBUTE_DEFINITION.allowed_values`,
  `ATTRIBUTE_DEFINITION.description`, and
  `OBJECT_ATTRIBUTE.namespace`.

- **ENUM:**
  - `OBJECT.object_type` (LOCAL_FILE; additional types are future extensions)
  - `ATTRIBUTE_DEFINITION.value_type` (TEXT, NUMBER, DATE, BOOLEAN, ENUM)
  - `ATTRIBUTE_DEFINITION.enum_value_type` (TEXT, NUMBER, DATE, BOOLEAN, or NULL)
  - `OBJECT_ATTRIBUTE.value_type` (TEXT, NUMBER, DATE, BOOLEAN, ENUM)

- **Enum definitions:** `enum_value_type` and a non-empty `allowed_values`
  array are required for `ENUM` definitions and must be NULL for other types.
  All allowed values must match the declared primitive type.

- **Indexes:**
  - `BRANCH(parent_id)` for path reconstruction
  - `TAGGING(branch_id)` for filtering assignments
  - `OBJECT_ATTRIBUTE(object_id)` for listing an Object's attributes
  - `OBJECT_ATTRIBUTE(namespace, key, value)` for filtering queries
  - `OBJECT_ATTRIBUTE(key)` for searching by key, including free attributes

- **Triggers:**
  - `TAG.is_system = 1` → renaming and deletion rejected at the database level
  - Automatic `updated_at` updates on `OBJECT` and `TAG`
