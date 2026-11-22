# Elevia

Elevia is an **Intelligence Augmentation** project that explores how to organize and visualize information in ways that follow the **flow of human thought**. Its goal is to help people manage large amounts of information and reason about more than they can hold in **working memory** at once.

Elevia aims to support knowledge management in different contexts, from personal files to large research projects.

The project draws on research into **cognitive processes** to explore different ways of representing information. Linear text is one such way; **visual and spatial representations** can complement it by making relationships, structures, and contexts easier to grasp. The goal is to amplify understanding and reasoning by drawing on different human cognitive abilities.

Elevia aims to make information easy to **find, connect, and compare** without losing its context. It seeks to help people move between the big picture and the details, recognize relationships and contradictions, and build syntheses grounded in the available evidence. **Judgment, decisions and critical thinking remain with the person.**


# The Modern Problem

Humans build **general knowledge** of the world through experience and learning. The brain can learn about and reason through many different problems, but addressing a specific problem requires knowledge and information that we may not possess or be able to recall.

In 2026, the growing complexity of the world requires us to address problems that span disciplines, from medicine to engineering. Elevia aims to amplify human cognitive abilities by building on the brain’s existing mechanisms for learning and reasoning. It seeks to help individuals tackle increasingly complex problems without necessarily needing specialist knowledge in every field.

To do this, Elevia aims to engage and integrate different cognitive processes by combining ways of representing knowledge. For example, bringing together written language, concept maps, visual connections, and spatial representations can support understanding, memory, and reasoning by engaging different brain networks in complementary ways.

This amplification has limits, however. Elevia could help someone understand complex medical problems, but it would not make them a surgeon. Some skills require **practical training** that engages brain circuits, such as those in the motor cortex, which cognitive support alone cannot adequately develop.

At the same time, the amount of content available to us is growing faster than our ability to examine it. The real bottleneck is identifying relevant information, evaluating it, and turning it into knowledge that can be applied to concrete problems.

Someone researching a potential cure for diabetes, for example, must compare numerous studies, understand the conditions under which their results were obtained, and identify any contradictions. Articles, notes, and data may be spread across different sources; retracing previous work each time takes time and can lead to important details being overlooked.


# Principles

1. **Amplify, not replace:** Elevia supports human understanding and reasoning. Judgment, decisions, and critical thinking remain with the person.

2. **Follow the flow of thought:** Information should be organized and explored in ways inspired by how people recall and connect ideas.

3. **Use multiple representations:** Text, visual, and spatial representations can complement one another, making information and relationships easier to understand.

4. **Preserve context:** Information should remain connected to its sources and surrounding context, so it can be found, compared, and evaluated.

5. **Support different scales:** Elevia should help people manage knowledge in contexts ranging from personal files to large research projects.


# Documentation

## Core

- [Core Architecture](docs/core/CORE_ARCHITECTURE.md): layers, services, and application entry points.
- [Business Rules](docs/core/BUSINESS_RULES.md): rules governing the model and planned file imports.
- [Database Schema](docs/core/DATABASE_SCHEMA.md): database entities, fields, and relationships.
- [Query](docs/core/QUERY.md): syntax and behavior of read-only searches.

## CLI

- [CLI Commands](docs/cli/CLI_COMMANDS.md): commands for managing and searching resources.
- [Migration Assistant](docs/cli/MIGRATION_LLM.md): use an LLM to propose a tag structure and generate commands for a folder of files.


# Initial Phase

Development focuses on the logical organization of resources through objects, tags, and attributes.
The goal is to make resources easy to find through **deterministic searches** based on explicit criteria.

## Content Organization

| Component    | Responsibility                                                                                         |
| ------------ | ------------------------------------------------------------------------------------------------------ |
| Object       | Represents a resource with an independent, unique identity.                                            |
| Tag Registry | Stores the identities and unique names of tags.                                                        |
| Tag Branches | Represent the contextual locations of tags, each with a stable identity.                               |
| Tagging      | Links objects to branches while preserving their full context.                                         |
| Tag Tree     | Displays the structure of tag branches.                                                                |
| Attributes   | Describe structured properties of objects that can be used as search criteria and value-based filters. |

### Object

`Object` is an abstract base for resources. For now, Elevia creates objects only by importing files. Each object has a unique ID and a required name used as a label; different objects can have the same name. Assignments to branches allow an object to be found from different contexts **without creating copies**. An object can be assigned to multiple branches of the same tag or of different tags.

Import registers a **reference to the original external file**, without copying, moving, or modifying it. Users continue working on that file. Elevia checks for changes while reading and does not use results from a read detected as inconsistent. Removing an object does not delete the file.

### Tag and Branch Structure

```text
Tag
├── Stable identity of a concept
└── Can be reused across multiple branches

Branch
├── Stable identity of a contextual location
├── References exactly one Tag
├── Has one parent branch, or none if it is a root
└── Forms part of a tree structure with multiple roots

Tagging
└── Unique pair: Object + branch

Using the same Tag in two contexts
├── Create two distinct branches
└── The Tag and its objects are not duplicated
```
​
### Attributes

**Attributes** describe structured properties associated with a resource, such as year, author, format, or amount. Each resource can have different attributes depending on its type and the information available.

Attributes can be used as search criteria and filters. For example, `photo.year = 2025` indicates the year associated with a photographic resource and makes it possible to search for resources whose attribute has the value `2025`.

#### Namespace

A **namespace** groups attributes within a context and helps distinguish properties that may share the same name but have different meanings. For example, `photo.year` and `invoice.year` belong to different contexts: the former may indicate the year of a photograph, while the latter may indicate the year of an invoice.

In the descriptive notation `namespace.key = value`:

- `namespace` identifies the attribute’s context;
- `key` identifies the property;
- `value` contains the information associated with the resource.

**Attributes** are independent of the **Tags** and **Branches** to which a resource is assigned. They can be used in global searches or in searches limited to a specific branch.

## Controlled Vocabulary

The **controlled vocabulary** contains the Tags available for organizing resources. Defining Tags before using them helps keep their names and meanings consistent over time.

**Attributes** are organized through a metadata schema, which describes the available properties and the kinds of information they can contain. For example, a property may represent a year, a text, or a status; some properties can have multiple values or be limited to predefined choices.

**Namespaces** group properties by context. For example, `work.status` may describe the status of a work-related resource. The `work` namespace is independent of the `Work` Tag: the former organizes attributes, while the latter helps place and find resources.

Attributes belong to the object and describe it independently of its Branches. This means that a resource retains its characteristics even when explored from different contexts.

The schema also makes metadata more reliable in searches: it distinguishes missing information from a present value, such as `0` or an empty string, and allows each value to be interpreted according to its meaning.

## Maintenance

Elevia helps users keep their organization consistent through validation, suggested corrections, and tools for reviewing structural changes.

Maintenance features include:

- **Validation:** detect invalid structures, such as duplicate branches and cycles.
- **Tag cleanup:** identify similar names, unused Tags, and branches without assignments, then suggest corrections.
- **Impact preview:** show how a structural change may affect objects, paths, and queries before confirmation.
- **Undo and snapshots:** allow users to reverse operations or restore a saved structure after larger changes.
- **Health dashboard:** display issues and suggested maintenance actions.

The rules governing assignments, deletion, and transactions are described in the [Business Rules](docs/core/BUSINESS_RULES.md).

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

Tag Branches
│
├── Work [T1, B1]
│   └── Ferrari [T3, B2]
│       └── Contracts [T4, B3]
│
├── Interests [T2, B4]
│   └── Ferrari [T3, B5]                 ← same Tag, different Branch
│       ├── Contracts [T4, B6]           ← explicitly added here
│       └── Photographs [T5, B7]         ← present only in this context
│
├── Ferrari [T3, B8]                     ← root Branch
├── Contracts [T4, B9]                   ← root Branch
└── Photographs [T5, B10]                ← root Branch

Objects and Tagging                      ← at least one Branch per Object
│
├── Professional agreement [obj-001]
│   └── B3: Work → Ferrari → Contracts
│
├── Model car purchase agreement [obj-002]
│   └── B6: Interests → Ferrari → Contracts
│
└── Photo at Monza [obj-003]
    ├── B7: Interests → Ferrari → Photographs
    ├── Attribute: photo.year = 2026

Explicit Search                          ← includes descendant Branches
│
├── tag:Ferrari                          ← Ferrari in any branch
│   └── obj-001, obj-002, obj-003
│
├── tag:Ferrari.Contracts                ← matching branch under any root
│   └── obj-001, obj-002
│
├── tag:Work.Ferrari                     ← matching branch under Work
│   └── obj-001
│
├── tag:Interests.Ferrari                ← matching branch under Interests
│   └── obj-002, obj-003
│
└── tag:Contracts                        ← Contracts in any branch
    └── obj-001, obj-002

Attribute filter                         ← independent of Tags and Branches
│
├── photo.year = 2026
│   └── obj-003
│
└── (tag:Interests.Ferrari) AND (photo.year = 2026)
    └── obj-003
```


# Advanced Phase

The advanced phase of Elevia aims to realize the vision described at the beginning of this README.

This vision is based on the idea that, in our time, people need to develop skills across different fields, from medicine to engineering. This becomes possible by investing first in **general knowledge and skills** that can be applied across contexts.

Elevia helps people make better use of this knowledge and gradually develop specialized knowledge, whether medical, engineering, or otherwise. Its contribution remains within the limits of what software can offer.

To achieve these goals, the advanced phase develops in two directions:

- **Amplify human thought:** help people understand information, explore connections, and address complex problems without reasoning for them.

- **Amplify the ability to act:** provide an executor capable of performing deterministic tasks. The user remains in control and confirms the result before it is applied, in accordance with Elevia's principles.

## New Features

The advanced phase also extends Elevia's capabilities in the interface used to manage and find resources.

- **Natural language understanding:** allow users to interact with Elevia in their own words, for example through a query.

- **Content analysis:** extract information from supported files and divide their content into parts, or chunks, linked to the original resource. These parts can be used to search and explore content.

- **Data extraction and normalization:** organize information such as text and numerical values into structured, consistent formats ready for use.

- **Actions:** execute and combine operations on data and resources in processes triggered by events, conditions, or schedules. These processes do not necessarily require AI.

- **File format plugins:** allow Elevia to recognize and handle different formats, presenting an interface suited to each format's content.

## Space

Space is an advanced Elevia environment for **exploring knowledge and supporting reasoning**. It can offer a workspace similar to a whiteboard, where users arrange and connect content as they reason. It contributes to the goal of **amplifying human thought** and makes the initial phase's features available.

Unlike the initial interface, which focuses on managing and finding resources, Space provides a place to gather content, observe connections, and work with information through different representations.

### Intelligent UI

The Intelligent UI offers users an intelligent interface with representations and interactive tools.

Its goal is to support comprehension and reasoning through forms that engage complementary cognitive abilities and different areas of the brain. Visual representations, spatial layout, and colors can make relationships and structures more immediately apparent than a lengthy description, while giving users freedom to explore and imagine. These forms can engage multiple areas of the brain at the same time.

For example, when reading about a place, a map or an image can make its layout easier to grasp than a plain-text description alone. Intelligent UI aims to bring that visual and spatial context alongside text, so users can understand and explore information through both.

### Insight Engine

The Insight Engine makes relevant content accessible and guides users through its connections. It can consider deterministic criteria, semantic proximity, and relationships between content.

Exploration is guided by **context masks**. Each mask expresses a topic, a purpose, or a constraint, such as a time period. Multiple masks can be active at once: together they generate the **Attention Beam**, which represents the user's current focus.

A query can create a context mask, which the user can refine alongside the others. An **exact search** can also return the requested matches without starting a broader exploration.

Based on the Attention Beam, the **Relevance Field** temporarily changes the proximity and relevance of content. For example, when exploring Ferrari car production, `Maranello` may be close to production content. When exploring Ferrari fuel consumption, other content and paths may become more relevant.

**Activation Spread** follows connections between content to reach items indirectly connected to the focus. The Relevance Field favors some paths over others, and activation decreases at each step, or **hop**.

To prevent uncontrolled propagation, the user defines an **exploration budget** that limits its extent. Content reached through propagation remains distinguishable from content that directly satisfies deterministic criteria.

Exploration temporarily changes the perspective on content **without automatically altering the permanent structure** of the archive.
