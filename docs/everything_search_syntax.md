# Everything Search Syntax Guide

This document provides a comprehensive reference for the "Everything" search syntax, based on the official documentation.

## Table of Contents

1. [Operators](#operators)
2. [Wildcards](#wildcards)
3. [Macros](#macros)
4. [Modifiers](#modifiers)
5. [Functions](#functions)
6. [Function Syntax](#function-syntax)
7. [Size Syntax and Constants](#size-syntax-and-constants)
8. [Date Syntax and Constants](#date-syntax-and-constants)
9. [Attribute Constants](#attribute-constants)
10. [Advanced Features](#advanced-features)

---

## Operators

Used to combine or negate search terms.

| Operator | Description | Example |
| :--- | :--- | :--- |
| `space` | AND | `foo bar` (Contains both foo AND bar) |
| `|` | OR | `jpg|png` (Contains jpg OR png) |
| `!` | NOT | `!foo` (Does NOT contain foo) |
| `< >` | Grouping | `<jpg|png> !foo` |
| `" "` | Exact phrase | `"program files"` |

---

## Wildcards

Used to match patterns in filenames.
*Note: Wildcards match the WHOLE filename unless "Match whole filename when using wildcards" is disabled in options.*

| Wildcard | Description |
| :--- | :--- |
| `*` | Matches zero or more characters. |
| `?` | Matches exactly one character. |

---

## Macros

Shortcuts for common file types or special characters.

| Macro | Description |
| :--- | :--- |
| `audio:` | Search for audio files. |
| `zip:` | Search for compressed files. |
| `doc:` | Search for document files. |
| `exe:` | Search for executable files. |
| `pic:` | Search for picture files. |
| `video:` | Search for video files. |
| `quot:` | Literal double quote `"` |
| `apos:` | Literal apostrophe `'` |
| `amp:` | Literal ampersand `&` |
| `lt:` | Literal less than `<` |
| `gt:` | Literal greater than `>` |
| `#<n>:` | Literal unicode character `<n>` (decimal). |
| `#x<n>:` | Literal unicode character `<n>` (hexadecimal). |

---

## Modifiers

Modifiers change **how** the search term immediately following them is interpreted.

| Modifier | Description |
| :--- | :--- |
| `case:` / `nocase:` | Enable/Disable case sensitivity. |
| `wholeword:` / `ww:` | Match whole words only. |
| `path:` / `nopath:` | Match against full path and filename vs filename only. |
| `regex:` / `noregex:` | Enable/Disable Regular Expressions. |
| `wfn:` / `exact:` | Match the whole filename (no partial matches). |
| `diacritics:` | Match accent marks. |
| `file:` | Match files only. |
| `folder:` | Match folders only. |
| `ascii:` / `utf8:` | Enable/Disable fast ASCII case comparisons. |
| `wildcards:` | Force enable wildcards. |

---

## Functions

Functions filter files based on specific **properties** or **metadata**. They generally take arguments.

### Common Functions

| Function | Description |
| :--- | :--- |
| `size:<size>` | Search by file size (e.g., `size:>10mb`). |
| `ext:<list>` | Search by extension (semicolon delimited). |
| `child:<filename>` | Folders containing a specific child file. |
| `empty:` | Search for empty folders. |
| `root:` | Search for files/folders in the root of a drive. |
| `parent:<path>` | Search within a specific parent path. |
| `dupe:` | Find duplicated filenames. |
| `depth:<count>` | Search by folder depth. |

### Date Functions

| Function | Short | Description |
| :--- | :--- | :--- |
| `datecreated:<date>` | `dc:` | Date Created. |
| `datemodified:<date>` | `dm:` | Date Modified. |
| `dateaccessed:<date>` | `da:` | Date Accessed. |
| `recentchange:<date>` | `rc:` | Recently changed date. |
| `daterun:<date>` | `dr:` | Date run. |

### Content Functions (Slow)

| Function | Description |
| :--- | :--- |
| `content:<text>` | Search file content. |
| `utf8content:<text>` | Treat content as UTF-8. |

### Image Functions

| Function | Description |
| :--- | :--- |
| `width:<pixels>` | Image width. |
| `height:<pixels>` | Image height. |
| `dimensions:<w>x<h>` | Width x Height. |
| `orientation:<type>` | `landscape` or `portrait`. |

---

## Function Syntax

How to specify values for functions.

| Syntax | Meaning | Example |
| :--- | :--- | :--- |
| `func:value` | Equal to. | `size:10mb` |
| `func:>value` | Greater than. | `size:>10mb` |
| `func:>=value` | Greater than or equal. | `len:>=10` |
| `func:<value` | Less than. | `count:<5` |
| `func:start..end` | Range (inclusive). | `year:2000..2005` |
| `func:start-end` | Range. | `size:1mb-5mb` |

---

## Size Syntax and Constants

### Syntax
`size[kb|mb|gb]`

### Constants
| Constant | Range |
| :--- | :--- |
| `empty` | 0 bytes |
| `tiny` | 0 - 10 KB |
| `small` | 10 KB - 100 KB |
| `medium` | 100 KB - 1 MB |
| `large` | 1 MB - 16 MB |
| `huge` | 16 MB - 128 MB |
| `gigantic` | > 128 MB |
| `unknown` | Unknown size |

---

## Date Syntax and Constants

### Syntax
- `year` (2025)
- `month/year` (12/2025)
- `day/month/year` (depends on locale)
- ISO8601: `YYYY-MM-DDThh:mm:ss`

### Constants
| Constant | Description |
| :--- | :--- |
| `today` | Current day. |
| `yesterday` | Previous day. |
| `thisweek` | Current week. |
| `lastmonth` | Previous month. |
| `past<x><years>` | Range (e.g., `past5mins`). |
| `january`... | Months. |
| `sunday`... | Days. |

---

## Attribute Constants

Used with `attrib:<attributes>`.

| Char | Attribute |
| :--- | :--- |
| `A` | Archive |
| `C` | Compressed |
| `D` | Directory |
| `H` | Hidden |
| `R` | Read only |
| `S` | System |
| `E` | Encrypted |
| `T` | Temporary |
| `N` | Normal |

---

## Advanced Features

### Regex
Regex overrides standard syntax.
- Enabled via `regex:` modifier or menu.
- `|` must be escaped as `"|"` if used inside regex in some contexts.

### ID3 Tags (Slow)
- `artist:`, `album:`, `title:`, `genre:`, `year:`, `track:`
