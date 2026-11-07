# DATABASE RELATIONSHIP SCHEMA

  
```text
Object
├── id                 bigint      PK, auto increment, not null
├── name               string      not null
├── object_type        string      not null: LOCAL_FILE | GENERIC_OBJECT
├── created_at         timestamp   not null
├── updated_at         timestamp   not null
│
├── Local File Object              0 or 1 per Object
│   ├── object_id      bigint      PK, FK → Object.id, not null
│   ├── is_available   boolean     not null
│   ├── file_path      text        not null
│   ├── normalized_path text       not null
│   ├── file_size      bigint      not null
│   ├── modified_at    timestamp   not null
│   └── file_extension string      not null
│
├── Tagging                        0 or more assignments
│   ├── id             bigint      PK, auto increment, not null
│   ├── object_id      bigint      FK → Object.id, not null
│   ├── placement_id   bigint      FK → Placement.id, not null
│   └── created_at     timestamp   not null
│
└── Object Attribute               0 or more attributes
    ├── id             bigint      PK, auto increment, not null
    ├── object_id      bigint      FK → Object.id, not null
    ├── definition_id  bigint      FK → Attribute Definition.id, nullable
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
    └── Placement                  0 or more placements of the Tag
        ├── id         bigint      PK, auto increment, not null
        ├── tag_id     bigint      FK → Tag.id, not null
        ├── parent_id  bigint      FK → Placement.id, nullable
        ├── created_at timestamp   not null
        ├── parent                 0 or 1 parent Placement
        ├── children               0 or more child Placements
        └── taggings               0 or more assignments to Objects


Attribute Registry
└── Attribute Namespace
    ├── id             bigint      PK, auto increment, not null
    ├── name           string      unique, not null, case insensitive
    ├── description    text        nullable
    ├── created_at     timestamp   not null
    │
    └── Attribute Definition       0 or more definitions
        ├── id             bigint  PK, auto increment, not null
        ├── namespace_id   bigint  FK → Attribute Namespace.id, not null
        ├── key            string  not null
        ├── value_type     string  not null: TEXT | NUMBER | DATE | BOOLEAN | ENUM
        ├── allowed_values text    nullable, JSON array for ENUM
        ├── description    text    nullable
        ├── created_at     timestamp not null
        └── object_attributes      0 or more attributes using the definition
```

## Database Constraints (Schema Level)

- **Primary keys:** `OBJECT.id`, `TAG.id`, `PLACEMENT.id`, `TAGGING.id`,
  `ATTRIBUTE_NAMESPACE.id`, `ATTRIBUTE_DEFINITION.id`, `OBJECT_ATTRIBUTE.id`
  — auto-increment, NOT NULL; IDs may be reused after `delete()` (internal to the Core).

- **Foreign keys with referential integrity:** references to nonexistent rows are rejected.
  - `LOCAL_FILE_OBJECT.object_id` → `OBJECT.id` (PK and FK, 1:1)
  - `PLACEMENT.tag_id` → `TAG.id` (NOT NULL)
  - `PLACEMENT.parent_id` → `PLACEMENT.id` (NULLABLE; NULL = root; at most one parent)
  - `TAGGING.object_id` → `OBJECT.id` (NOT NULL)
  - `TAGGING.placement_id` → `PLACEMENT.id` (NOT NULL)
  - `ATTRIBUTE_DEFINITION.namespace_id` → `ATTRIBUTE_NAMESPACE.id` (NOT NULL)
  - `OBJECT_ATTRIBUTE.object_id` → `OBJECT.id` (NOT NULL)
  - `OBJECT_ATTRIBUTE.definition_id` → `ATTRIBUTE_DEFINITION.id`
    (NULLABLE; NULL = free attribute)

- **UNIQUE:**
  - `TAG.name` — NOT NULL, case insensitive
  - `PLACEMENT (tag_id, parent_id)` — at most one Placement per Tag under the same parent
  - `PLACEMENT (tag_id) WHERE parent_id IS NULL` — at most one root Placement per Tag
  - `TAGGING (object_id, placement_id)` — an Object can appear at most once in a Placement
  - `ATTRIBUTE_NAMESPACE.name` — NOT NULL, case insensitive
  - `ATTRIBUTE_DEFINITION (namespace_id, key)` — each key can appear at most once per namespace
  - `OBJECT_ATTRIBUTE (object_id, namespace, key)` — at most one value per object and key
    (NULL namespace = free attribute)

- **NOT NULL:** all schema fields except `TAG.description`, `PLACEMENT.parent_id`,
  `ATTRIBUTE_NAMESPACE.description`, `ATTRIBUTE_DEFINITION.allowed_values`,
  `ATTRIBUTE_DEFINITION.description`, `OBJECT_ATTRIBUTE.definition_id`, and
  `OBJECT_ATTRIBUTE.namespace`.

- **ENUM:**
  - `OBJECT.object_type` (LOCAL_FILE, GENERIC_OBJECT)
  - `ATTRIBUTE_DEFINITION.value_type` (TEXT, NUMBER, DATE, BOOLEAN, ENUM)
  - `OBJECT_ATTRIBUTE.value_type` (TEXT, NUMBER, DATE, BOOLEAN, ENUM)

- **Indexes:**
  - `PLACEMENT(parent_id)` for path reconstruction
  - `TAGGING(placement_id)` for filtering assignments
  - `OBJECT_ATTRIBUTE(object_id)` for listing an Object's attributes
  - `OBJECT_ATTRIBUTE(namespace, key, value)` for filtering queries
  - `OBJECT_ATTRIBUTE(key)` for searching by key, including free attributes

- **Triggers:**
  - `TAG.is_system = 1` → renaming and deletion rejected at the database level
  - Automatic `updated_at` updates on `OBJECT` and `TAG`
