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
│   ├── Placement                       Tag location; parent_id is self-referential
│   ├── Tagging                         links Object ↔ Placement
│   ├── AttributeNamespace              attribute template
│   ├── AttributeDefinition             attribute type and allowed values
│   └── ObjectAttribute                 attribute value on an Object
│
├── Application Layer                   use cases and orchestration
│   ├── ObjectService                   register, rename, remove
│   ├── LocalFileObjectService          local-file operations and availability
│   ├── TaggingService                  assign, transfer, remove
│   ├── PlacementService                create, move, delete
│   ├── TagService                      create, rename, delete
│   ├── PreviewService                  preview the impact of changes
│   ├── TagPlacementTreeService         build the Placement tree
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
    │   ├── PlacementRepository
    │   ├── TaggingRepository
    │   ├── AttributeNamespaceRepository
    │   ├── AttributeDefinitionRepository
    │   └── ObjectAttributeRepository
    ├── schema.sql                       tables, indexes and triggers
    ├── migrator                         applies schema changes
    └── seed                             creates Untagged and its root Placement

Database                                persistent storage
```

Repository interfaces define how the application accesses stored data;
infrastructure provides their implementations. Application services
coordinate use cases and validation. Database constraints provide additional
integrity checks, and the TransactionManager ensures that writes within a
transaction succeed or fail together.

# Operational Flows

```text
Import a file
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

Create a Placement
└── User → PlacementService.create() →
    validate parent and placement rules → PlacementRepository → Database

Move a Placement
└── User → PreviewService → impact preview →
    user confirmation → PlacementService.move() →
    revalidate state and constraints → PlacementRepository → Database

Delete a Placement
└── User → PlacementService.delete() →
    reject if it has children or assignments → PlacementRepository → Database

Delete a Tag
└── User → TagService.delete() →
    validate its Placements → TagRepository → Database

Rename an Object or a Tag
└── User → ObjectService.rename() / TagService.rename() →
    validate rename → ObjectRepository / TagRepository → Database

Remove an Object from Elevia
└── User → ObjectService.remove() →
    remove the Object and its associations from Elevia →
    repositories → Database
    The original file is not deleted.

View the Placement tree — read-only
└── User → TagPlacementTreeService.get_tree() →
    PlacementRepository.find_all() → tree structure

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