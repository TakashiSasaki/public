# File: generate_lunr_index.py
# This script reads all .txt and .md files in the current directory,
# builds a Lunr index, and writes the index and document lookup to lunr_index.js

import os
import json
from lunr import lunr  # Ensure you have installed lunr via: pip install lunr

# List to hold document objects for indexing
documents = []
# Dictionary for a lookup of document metadata (for displaying titles and summaries)
lookup = {}

# Iterate over all .txt and .md files in the current directory
for filename in os.listdir('.'):
    if filename.endswith('.txt') or filename.endswith('.md'):
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        # Use the filename (without extension) as the document ID and title
        doc_id = os.path.splitext(filename)[0]
        documents.append({
            'id': doc_id,
            'title': doc_id,
            'body': content
        })
        # Create a lookup entry; adjust summary length as needed
        lookup[doc_id] = {
            'title': doc_id,
            'url': filename,  # Could be a relative path or a corresponding HTML page URL
            'summary': content[:100] + "..." if len(content) > 100 else content
        }

# Build the Lunr index with the documents
idx = lunr(ref='id', fields=['title', 'body'], documents=documents)

# Serialize the index using the correct method
index_json = json.dumps(idx.serialize())
lookup_json = json.dumps(lookup)

# Create the JavaScript file content
js_content = f"var prebuiltIndexData = {index_json};\nvar prebuiltDocuments = {lookup_json};\n"

# Write the output to lunr_index.js
with open('lunr_index.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("lunr_index.js has been generated successfully.")
