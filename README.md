# Elevia

Elevia is an **Intelligence Augmentation** project that explores how to organize and visualize information in ways that follow the **flow of human thought**. Its goal is to help people manage large amounts of information and reason about more than they can hold in **working memory** at once.

Elevia aims to support knowledge management in different contexts, from personal files to large research projects.

The project draws on research into **cognitive processes** to explore different ways of representing information. Linear text is one such way; **visual and spatial representations** can complement it by making relationships, structures, and contexts easier to grasp. The goal is to amplify understanding and reasoning by drawing on different human cognitive abilities.

Elevia aims to make information easy to **find, connect, and compare** without losing its context. It seeks to help people move between the big picture and the details, recognize relationships and contradictions, and build syntheses grounded in the available evidence. **Judgment, decisions and critical thinking remain with the person.**


# The Modern Problem

Humans build **general knowledge of the world** through experience and learning. The brain can learn about and reason through many different problems, but addressing a specific one requires **information that we do not always possess or recall**.

In 2026, we have access to a volume of content that is growing faster than our ability to examine it. The **bottleneck** is identifying what is relevant, evaluating it, and using it to address a concrete question.

Someone researching a possible cure for diabetes, for example, must **compare many studies**, understand the conditions under which results were obtained, and recognize contradictions. Articles, notes, and data may be scattered across different places; retracing the work each time takes time and can cause useful details to be overlooked.

Different kinds of contributions can also relate to the same topic: a social media comment might contain an interesting observation, while a scientific article might provide evidence to examine it. Comparing them requires attention to their **sources and reliability**, without treating all sources as equally credible.

The goal is to seek a **“centroid”** that aligns as closely as possible with the available evidence: a **reasoned synthesis** that considers relevant contributions without assuming that truth is the average of opinions.


# Principles

1. **Amplify, not replace:** Elevia supports human understanding and reasoning. Judgment, decisions, and critical thinking remain with the person.

2. **Follow the flow of thought:** Information should be organized and explored in ways inspired by how people recall and connect ideas.

3. **Use multiple representations:** Text, visual, and spatial representations can complement one another, making information and relationships easier to understand.

4. **Preserve context:** Information should remain connected to its sources and surrounding context, so it can be found, compared, and evaluated.

5. **Support different scales:** Elevia should help people manage knowledge in contexts ranging from personal files to large research projects.


# Initial Phase

Development focuses on the logical organization of resources through objects, tags, and attributes.
The goal is to make resources easy to find through deterministic searches based on explicit criteria.

## Content Organization

| Component      | Responsibility                                                                                         |
| -------------- | ------------------------------------------------------------------------------------------------------ |
| Object         | Represents a resource with an independent, unique identity.                                            |
| Tag Registry   | Stores the identities and unique names of tags.                                                        |
| Tag Placements | Represent the contextual locations of tags, each with a stable identity.                               |
| Tagging        | Links objects to placements while preserving their full context.                                       |
| Tag Tree       | Displays the structure of tag placements.                                                              |
| Attributes     | Describe structured properties of objects that can be used as search criteria and value-based filters. |

### Object

Each file, document, or resource is represented by an abstract `Object`. Assignments to placements allow it to be found from different contexts without creating copies. An object can be assigned to multiple placements of the same tag or of different tags.

### Tag and Placement Structure

​```
Tag
├── Stable identity of a concept
└── Can be reused across multiple placements

Placement
├── Stable identity of a contextual location
├── References exactly one Tag
├── Has one parent placement, or none if it is a root
└── Forms part of a tree structure with multiple roots

Tagging
└── Unique pair: Object + placement

Using the same Tag in two contexts
├── Create two distinct placements
└── The Tag and its objects are not duplicated
​```

### Attributes

**Attributes** describe structured properties associated with a resource, such as year, author, format, or amount. Each resource can have different attributes depending on its type and the information available.

Attributes can be used as search criteria and filters. For example, `photo.year = 2025` indicates the year associated with a photographic resource and makes it possible to search for resources whose attribute has the value `2025`.

#### Namespace

A **namespace** groups attributes within a context and helps distinguish properties that may share the same name but have different meanings. For example, `photo.year` and `invoice.year` belong to different contexts: the former may indicate the year of a photograph, while the latter may indicate the year of an invoice.

In the descriptive notation `namespace.key = value`:

- `namespace` identifies the attribute’s context;
- `key` identifies the property;
- `value` contains the information associated with the resource.

**Attributes** are independent of the **Tags** and **Placements** to which a resource is assigned. They can be used in global searches or in searches limited to a specific branch.

## Controlled Vocabulary

The **controlled vocabulary** contains the Tags available for organizing resources. Defining Tags before using them helps keep their names and meanings consistent over time.

**Attributes** are organized through a metadata schema, which describes the available properties and the kinds of information they can contain. For example, a property may represent a year, a text, or a status; some properties can have multiple values or be limited to predefined choices.

**Namespaces** group properties by context. For example, `work.status` may describe the status of a work-related resource. The `work` namespace is independent of the `Work` Tag: the former organizes attributes, while the latter helps place and find resources.

Attributes belong to the object and describe it independently of its Placements. This means that a resource retains its characteristics even when explored from different contexts.

The schema also makes metadata more reliable in searches: it distinguishes missing information from a present value, such as `0` or an empty string, and allows each value to be interpreted according to its meaning.

## Maintenance

Elevia helps users keep their organization consistent through validation, suggested corrections, and tools for reviewing structural changes.

Maintenance features include:

- **Validation:** detect invalid structures, such as duplicate placements and cycles.
- **Tag cleanup:** identify similar names, unused Tags, and placements without assignments, then suggest corrections.
- **Impact preview:** show how a structural change may affect objects, paths, and queries before confirmation.
- **Undo and snapshots:** allow users to reverse operations or restore a saved structure after larger changes.
- **Health dashboard:** display issues and suggested maintenance actions.

The rules governing assignments, deletion, and transactions are described in the [Business Rules](docs/core/BUSINESS%20RULES.md).

## Overview Diagram

```text

├── Controlled Vocabulary
│   └── Tag Registry
│       ├── Work        [T1]
│       ├── Interests   [T2]
│       ├── Ferrari     [T3]
│       ├── Contracts   [T4]
│       └── Photographs [T5]
│
└── Metadata Registry
    ├── work
    │   ├── status: ENUM   → draft / approved / archived
    │   └── project: TEXT  → free value
    ├── photo
    │   └── year: NUMBER   → free value
    └── color: TEXT        → free value, no namespace

Tag Placements
│
├── Work [T1, P1]
│   └── Ferrari [T3, P2]
│       └── Contracts [T4, P3]
│
├── Interests [T2, P4]
│   └── Ferrari [T3, P5]                 ← same Tag, different Placement
│       ├── Contracts [T4, P6]           ← explicitly added here
│       └── Photographs [T5, P7]         ← present only in this context
│
├── Ferrari [T3, P8]                     ← root Placement
├── Contracts [T4, P9]                   ← root Placement
└── Photographs [T5, P10]                ← root Placement

Objects and Tagging                      ← at least one Placement per Object
│
├── Professional agreement [obj-001]
│   └── P3: Work → Ferrari → Contracts
│
├── Model car purchase agreement [obj-002]
│   └── P6: Interests → Ferrari → Contracts
│
└── Photo at Monza [obj-003]
    ├── P7: Interests → Ferrari → Photographs
    ├── Attribute: photo.year = 2026

Explicit search                          ← includes descendant Placements
│
├── ANYWHERE: Ferrari [T3]
│   └── obj-001, obj-002, obj-003
│
├── THIS BRANCH: Work → Ferrari [P2]
│   └── obj-001
│
├── THIS BRANCH: Interests → Ferrari [P5]
│   └── obj-002, obj-003
│
└── ANYWHERE: Contracts [T4]
    └── obj-001, obj-002

Attribute filter                         ← independent of Tags and Placements
│
└── Condition: photo.year = 2026
    ├── Applied globally or within a selected branch
    └── Global result: Photo at Monza [obj-003], returned once
```


# Advanced Phase

The following features are planned for future development:

- **File-type plugins:** allow plugins to be created for different file formats, each with its own tools for reading, displaying, and managing content. For example, a Photoshop plugin could handle Photoshop files.

- **Shared knowledge:** information extracted by plugins can be organized in the Elevia Core, making it possible to connect and compare content from different file formats.

- **Information extraction and normalization:** use AI to extract information from files and organize it into consistent formats.

- **Statistics and data mining:** analyze extracted information to discover patterns, relationships, and trends across resources

- **Natural language understanding:** help users interact with and explore information using natural language.

- **Semantic exploration:** find and connect information based on meaning.

- **Cognitive augmentation:** support cognition by engaging different cognitive abilities in parallel. For example, visual and spatial representations can complement text-based reasoning.