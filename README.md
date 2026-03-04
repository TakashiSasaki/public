# static-lunr

A static full-text search system using [Lunr.js](https://lunrjs.com/) with specialized support for Japanese text via [Janome](https://mocobeta.github.io/janome/).

## Overview

This project provides a simple way to implement full-text search on static websites without a backend server. It pre-computes a search index from text and markdown files using Python and serves the results through a lightweight HTML interface.

## Core Features

- **Static Search**: Fast full-text search directly in the browser using a pre-built JSON index.
- **Japanese Support**: Specialized tokenization using Janome to handle Japanese text correctly.
- **Mixed Language**: Support for indexing and searching both Japanese and English content.
- **Zero Backend**: No search server required; all searching happens on the client side.

## Directory Structure

- `index.html`: The main frontend search interface.
- `index-generator/`: Python scripts for generating the Lunr index.
- `lunr_index.js`: The generated search index and document metadata (used by `index.html`).
- `inspect_lunr_index.py`: A utility to inspect the contents and statistics of the generated index.
- `sample-text/`: Example documents for testing the search system.
- `janome-user-dictionary.md`: Documentation on how to use a custom dictionary with Janome.

## Index Generation

The scripts in `index-generator/` are used to build the search index from `.txt` and `.md` files in the current directory.

1.  **`generate_lunr_index.py`**: Basic indexer for English or simple text.
2.  **`generate_lunr_index_japanese.py`**: Uses Janome to tokenize Japanese text for improved search accuracy in Japanese.
3.  **`generate_lunr_index_dual.py`**: A unified indexer that applies both Japanese and English tokenization, best for mixed-language content.

### Usage

Install dependencies:

```bash
pip install lunr janome
```

Run one of the generator scripts (example from project root):

```bash
python index-generator/generate_lunr_index_dual.py
```

This will create or update `lunr_index.js`.

## Search Interface

Opening `index.html` in a browser provides a search box. It loads `lunr_index.js` and uses the Lunr.js library (via CDN) to perform searches. Features include:
- Real-time debounced search.
- Prefix matching support (automatically appends `*` to tokens).
- Highlighted snippets in search results.

## Inspection Utility

The `inspect_lunr_index.py` script allows you to see what terms are actually in your index:

```bash
python inspect_lunr_index.py
```

It outputs term frequencies and basic index metadata, which is useful for debugging tokenization issues.
