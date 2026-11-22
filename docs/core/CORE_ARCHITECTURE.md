# CORE ARCHITECTURE

Elevia Core uses a layered architecture with application services. The CLI
and desktop application act as entry points; they invoke services rather than
accessing the database directly.

`Object` is an abstract base for resource types. The current scope creates only
`LocalFileObject` instances through file import; generic objects are not a
separately creatable type. An object's ID identifies it; its required name is
a label that may be shared by multiple objects.

```text
External Actors
├── User
│   ├── CLI
│   └── Desktop application
└── FileSystem                          external source of file state

Elevia Core
├── Domain Layer                        domain entities and rules
│   ├── Object                          abstract resource
│   │   └── LocalFileObject             Object representing a local file
│   ├── Tag                             identity of a concept
│   ├── Branch                       Tag location; parent_id is self-referential
│   ├── Tagging                         links Object ↔ Branch
│   ├── AttributeNamespace              attribute template
│   ├── AttributeDefinition             attribute type and allowed values
│   └── ObjectAttribute                 attribute value on an Object
│
├── Application Layer                   use cases and orchestration
│   ├── ObjectService                   register, rename, remove
│   ├── LocalFileObjectService          local-file operations and availability
│   ├── TaggingService                  assign, transfer, remove
│   ├── BranchService                create, move, delete
│   ├── TagService                      create, rename, delete
│   ├── PreviewService                  preview the impact of changes
│   ├── TagBranchTreeService         build the Branch tree
│   ├── AttributeNamespaceService       manage namespaces
│   ├── ObjectNamespaceService          assign namespaces to objects
│   ├── AttributeDefinitionService      manage attribute definitions
│   ├── ObjectAttributeService          set, unset and show defined attributes
│   ├── QueryService                    execute read-only searches
│   └── QueryParser                     parse Tag and attribute conditions
│
└── Infrastructure Layer                technical implementations
    ├── TransactionManager              manage atomic database transactions
    ├── LocalFileAvailableCheck          check local-file availability
    ├── Repository implementations
    │   ├── ObjectRepository
    │   ├── LocalFileObjectRepository
    │   ├── TagRepository
    │   ├── BranchRepository
    │   ├── TaggingRepository
    │   ├── AttributeNamespaceRepository
    │   ├── ObjectNamespaceRepository
    │   ├── AttributeDefinitionRepository
    │   └── ObjectAttributeRepository
    ├── schema.sql                       tables, indexes and triggers
    ├── migrator                         applies schema changes
    └── seed                             creates Untagged and its root Branch

Database                                persistent storage
```

Repository interfaces define how the application accesses stored data;
infrastructure provides their implementations. Application services
coordinate use cases and validation. Database constraints provide additional
integrity checks, and the TransactionManager ensures that writes within a
transaction succeed or fail together.

## File Import and Reading

Import registers a path to the original external file, without creating a copy.
The user continues editing that file; removing the Object does not delete it.
If a file becomes inaccessible, its Object remains searchable and is marked
unavailable.

When reading a file, Elevia checks for concurrent changes. If a change is
detected during the read, it discards the result and retries or reports an
error. The detection mechanism and retry policy are not yet specified; a check
alone cannot guarantee that every concurrent change will be detected.

# Operational Flows

```text
Register an external file (current flow)
└── User → import_cmd →
    LocalFileObjectService.register() →
    validate and create Object + LocalFileObject + Tagging atomically →
    repositories → Database

Add a Tag to an Object
└── User → TaggingService.assign() →
    validate assignment → TaggingRepository → Database

Transfer an Object to another context
└── User → TaggingService.transfer() →
    validate source and destination → TaggingRepository → Database

Remove an Object from a context
└── User → TaggingService.remove() →
    if removing the last Tagging, assign the Object to Untagged →
    TaggingRepository → Database

Create a Branch
└── User → BranchService.create() →
    validate parent and branch rules → BranchRepository → Database

Move a Branch in Desktop
└── User → PreviewService → impact preview →
    user confirmation → BranchService.move() →
    revalidate state and constraints → BranchRepository → Database

Move a Branch in CLI
└── User → BranchService.move() →
    validate state and constraints → BranchRepository → Database
    No preview or confirmation; validation and transaction checks still apply.

Delete a Branch
└── User → BranchService.delete() →
    reject if it has children or assignments → BranchRepository → Database

Delete a Tag
└── User → TagService.delete() →
    validate its Branches → TagRepository → Database

Rename an Object or a Tag
└── User → ObjectService.rename() / TagService.rename() →
    validate rename → ObjectRepository / TagRepository → Database

Remove an Object from Elevia
└── User → ObjectService.remove() →
    remove the Object and its associations from Elevia →
    repositories → Database
    The original file is not deleted.

View the Branch tree — read-only
└── User → TagBranchTreeService.get_tree() →
    BranchRepository.find_all() → tree structure

Search Objects — read-only
└── User → QueryService.search(expression) →
    QueryParser → generated SQL → Database → results

Check file availability
└── LocalFileAvailableCheck → compare registered paths with the filesystem →
    LocalFileObjectService.mark_available() / mark_unavailable() →
    LocalFileObjectRepository → Database

Create an attribute namespace
└── User → AttributeNamespaceService.create() →
    validate namespace → AttributeNamespaceRepository → Database

Define an attribute, with or without a namespace
└── User → AttributeDefinitionService.create() →
    validate the definition and its type → AttributeDefinitionRepository → Database
    If a namespace is used, it must already exist.

Assign a namespace to an Object
└── User → ObjectNamespaceService.assign() →
    validate Object and namespace → ObjectNamespaceRepository → Database
    The complete namespace is assigned; its values default to NULL and may be supplied later.

Set a namespaced attribute value
└── User → ObjectAttributeService.set() →
    check namespace assignment, find definition and validate type and value →
    ObjectAttributeRepository → Database

Assign a free attribute
└── User → ObjectAttributeService.set() →
    find definition and validate type and value →
    ObjectAttributeRepository → Database
    The definition and its type must exist before assignment.

Remove an attribute from an Object
└── User → ObjectAttributeService.unset() →
    remove the stored value → ObjectAttributeRepository → Database
    The applicable attribute returns to NULL; its definition and namespace assignment remain.

Delete a namespace
└── User → AttributeNamespaceService.delete() →
    delete its definitions and values → AttributeNamespaceRepository → Database

Delete an attribute definition
└── User → AttributeDefinitionService.delete() →
    delete values that use it → AttributeDefinitionRepository → Database
```
