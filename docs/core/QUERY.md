# QUERY

Explicit, read-only search. No TransactionManager, preview, or lock. A query
does not modify data or produce side effects.

The syntax supports two types of conditions: `tag:path` and
`namespace.key = value` (or `key = value` for free attributes). Conditions
can be combined using the logical operators `AND`, `OR`, and `NOT`.

## Syntax

```ebnf
query = or_expr ;

or_expr = and_expr , { "OR" , and_expr } ;
and_expr = term , { "AND" , term } ;
term = [ "NOT" ] , atom ;
atom = "(" , query , ")" | condition ;

condition = tag_condition | attr_condition ;

tag_condition = "tag:" , tag_value ;
tag_value = "*" | name , { "." , name } ;

attr_condition = attr_path , operator , value ;
attr_path = [ name , "." ] , name ;
operator = "=" | "!=" | ">" | "<" | ">=" | "<=" ;

value = string | number | date | boolean ;

name = word | '"' , text , '"' ;
string = '"' , text , '"' ;
number = [ "-" ] , digit , { digit } , [ "." , digit , { digit } ] ;
date = '"' , YYYY-MM-DD , '"' ;
boolean = "true" | "false" ;
```

## Attribute Value Types

Query conditions use the attribute's `value_type` to interpret and validate
the supplied value.

| Attribute type | Query value | Example |
| --- | --- | --- |
| `TEXT` | Quoted string | `title = "Report"` |
| `NUMBER` | Integer or decimal number | `photo.year = 2025` |
| `DATE` | Quoted date in `YYYY-MM-DD` format | `work.deadline < "2025-12-31"` |
| `BOOLEAN` | `true` or `false` | `published = true` |
| `ENUM` | Quoted value from the definition's `allowed_values` | `work.status = "approved"` |

The attribute type distinguishes a date from a text value: both are
written in quotes. A value incompatible with the attribute type produces
an explicit error.

The operators `>` , `<`, `>=`, and `<=` are allowed only for `NUMBER`
and `DATE`. Equality and inequality use `=` and `!=`.

## Style

Write a single condition without parentheses. When combining conditions,
the examples below place each condition in parentheses, with the operator
between them. Parentheses are optional where the grammar does not require
them.

```text
tag:Ferrari
tag:*
tag:Passioni.Ferrari.Fotografie
photo.year = 2025
work.status = "approved"
colore = "rosso"

(tag:Ferrari) AND (tag:Fotografie)
(tag:Ferrari) OR (tag:Passioni)
NOT (tag:Fotografie)
(tag:Ferrari) AND NOT (tag:Fotografie)
((tag:Ferrari) OR (tag:Passioni)) AND (tag:Contratti)
(tag:Ferrari) AND (photo.year = 2025)
(photo.year >= 2020) AND (photo.year <= 2025)
(tag:Contratti) AND (work.status = "approved")
```

## Semantics

`tag:X.Y.Z` matches Objects with a Tagging on a Placement whose path contains
the Tags `X`, `Y`, and `Z` consecutively. The path may continue beyond `Z`,
so Objects assigned to descendant Placements also match.

| Condition | Returns |
| --- | --- |
| `tag:*` | All registered Objects, including those in `Untagged` |
| `tag:Ferrari` | Objects assigned to Ferrari in any branch, including descendants |
| `tag:Ferrari.Fotografie` | Objects in the Ferrari → Fotografie branch under any root |
| `tag:Passioni.Ferrari.Fotografie` | Objects in the same branch, but only under Passioni |
| `tag:Lavoro.Ferrari.Contratti` | Objects in the work contracts branch |

Attribute conditions such as `namespace.key = value` or `key = value` for
free attributes match Objects that have the specified attribute and value.
The operators `>`, `<`, `>=`, and `<=` are allowed only for attributes of
type `NUMBER` or `DATE`.

| Condition | Returns |
| --- | --- |
| `photo.year = 2025` | Objects with `photo.year` equal to 2025 |
| `work.status = "approved"` | Objects with `work.status` equal to "approved" |
| `finance.amount >= 1000` | Objects with `finance.amount` greater than or equal to 1000 |
| `work.deadline < "2025-12-31"` | Objects with `work.deadline` before December 31, 2025 |
| `colore = "rosso"` | Objects with the free attribute `colore` equal to "rosso" |
| `anno = 2025` | Objects with the free attribute `anno` equal to 2025 |

Using the data from the README:

```text
tag:Ferrari → obj-001, obj-002, obj-003
tag:Ferrari.Contratti → obj-001, obj-002
tag:Lavoro.Ferrari.Contratti → obj-001
(tag:Ferrari) AND (tag:Contratti) → obj-001, obj-002
(tag:Ferrari) AND NOT (tag:Fotografie) → obj-001, obj-002
(tag:Passioni.Ferrari) AND NOT (tag:Contratti) → obj-003
photo.year = 2025 → obj-003 (if obj-003 has photo.year = 2025)
(tag:Ferrari) AND (photo.year = 2025) → obj-003
```

