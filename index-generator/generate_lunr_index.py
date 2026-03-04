# File: generate_lunr_index.py
# This script reads all .txt and .md files in the current directory,
# builds a Lunr index, and writes the index and document lookup to lunr_index.js.
# It also prints progress information and details about the generated index.

import os
import json
from lunr import lunr  # Ensure you have installed lunr via: pip install lunr

# Lists to hold document objects for indexing and a lookup for document metadata
documents = []
lookup = {}

# Counter for processed files
file_count = 0

print("Starting index generation...")

# Iterate over all .txt and .md files in the current directory
for filename in os.listdir('.'):
    if filename.endswith('.txt') or filename.endswith('.md'):
        file_count += 1
        print(f"Processing file {file_count}: {filename}")
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
            'url': filename,  # This can be modified to point to an HTML version if needed
            'summary': content[:100] + "..." if len(content) > 100 else content
        }

print(f"Total files processed: {file_count}")
print(f"Total documents to index: {len(documents)}")

# Build the Lunr index with the documents
print("Building the Lunr index...")
idx = lunr(ref='id', fields=['title', 'body'], documents=documents)
print("Lunr index built successfully.")

# Serialize the index and print detailed information about it
index_data = idx.serialize()
num_terms = len(index_data.get('invertedIndex', {}))
fields_indexed = index_data.get('fields', [])
print("Index Details:")
print(f"  Number of terms in the index: {num_terms}")
print(f"  Fields indexed: {fields_indexed}")

# Serialize the index and lookup dictionary to JSON
index_json = json.dumps(index_data)
lookup_json = json.dumps(lookup)

# Create the JavaScript file content with the global variables
js_content = f"var prebuiltIndexData = {index_json};\nvar prebuiltDocuments = {lookup_json};\n"

# Write the output to lunr_index.js
with open('lunr_index.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("lunr_index.js has been generated successfully.")
