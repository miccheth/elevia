# CORE ARCHITECTURE

Elevia Core uses a layered architecture with application services. The CLI
and desktop application act as entry points; they invoke services rather than
accessing the database directly.

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
│   ├── AttributeDefinitionService      manage attribute definitions
│   ├── ObjectAttributeService          set, unset, show and infer types
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

## Planned File Import

The current local-file flow registers a path to an external file. The planned
import flow will copy the file into Elevia as a snapshot without moving or
modifying the original. Later changes to the original will not automatically
change the snapshot.

When an Object is removed, the user will be asked whether to delete its
imported copy. The copy will be retained unless the user confirms deletion;
the original file will remain untouched. Storage and recovery of retained
copies, and the transition for existing external references, are not yet
defined.

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

Move a Branch
└── User → PreviewService → impact preview →
    user confirmation → BranchService.move() →
    revalidate state and constraints → BranchRepository → Database

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

Define an attribute in a namespace
└── User → AttributeDefinitionService.create() →
    validate definition → AttributeDefinitionRepository → Database

Assign a namespaced attribute
└── User → ObjectAttributeService.set() →
    find definition and validate type and value →
    ObjectAttributeRepository → Database

Assign a free attribute
└── User → ObjectAttributeService.set() →
    infer type and validate value → ObjectAttributeRepository → Database

Remove an attribute from an Object
└── User → ObjectAttributeService.unset() →
    ObjectAttributeRepository → Database

Delete a namespace
└── User → AttributeNamespaceService.delete() →
    delete its definitions and values → AttributeNamespaceRepository → Database

Delete an attribute definition
└── User → AttributeDefinitionService.delete() →
    delete values that use it → AttributeDefinitionRepository → Database
```
