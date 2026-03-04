# File: generate_lunr_index_japanese.py
# This script reads all .txt and .md files in the current directory,
# uses Janome to tokenize Japanese text, builds a Lunr index, and writes the
# index and document lookup to lunr_index.js.
# Ensure you have installed the required packages:
#   pip install lunr janome

import os
import json
from janome.tokenizer import Tokenizer
from lunr import lunr

# Initialize the Janome tokenizer
japanese_tokenizer = Tokenizer()

def tokenize_japanese(text):
    """
    Tokenize Japanese text using Janome.
    For each token, use the base form if available (or surface form otherwise),
    then join tokens with a space.
    """
    tokens = []
    for token in japanese_tokenizer.tokenize(text):
        base = token.base_form
        if base == "*":  # If no base form is available, use the surface form.
            base = token.surface
        tokens.append(base)
    # Join tokens with spaces so Lunr treats them as separate tokens.
    return " ".join(tokens)

# Lists for document objects and a lookup for document metadata.
documents = []
lookup = {}

file_count = 0
print("Starting Japanese index generation...")

# Iterate over all .txt and .md files in the current directory.
for filename in os.listdir('.'):
    if filename.endswith('.txt') or filename.endswith('.md'):
        file_count += 1
        print(f"Processing file {file_count}: {filename}")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        # Tokenize the content with Janome.
        tokenized_content = tokenize_japanese(content)
        # Use the filename (without extension) as the document ID and title.
        doc_id = os.path.splitext(filename)[0]
        documents.append({
            'id': doc_id,
            'title': doc_id,
            'body': tokenized_content
        })
        # Create a lookup entry; adjust summary length as needed.
        summary = content[:100] + "..." if len(content) > 100 else content
        lookup[doc_id] = {
            'title': doc_id,
            'url': filename,  # This can be modified to point to an HTML version if desired.
            'summary': summary
        }

print(f"Total files processed: {file_count}")
print(f"Total documents to index: {len(documents)}")

# Build the Lunr index with the documents.
print("Building the Lunr index for Japanese documents...")
idx = lunr(ref='id', fields=['title', 'body'], documents=documents)
print("Lunr index built successfully.")

# Serialize the index using the serialize() method.
index_json = json.dumps(idx.serialize())
lookup_json = json.dumps(lookup)

# Create the JavaScript file content with global variables.
js_content = f"var prebuiltIndexData = {index_json};\nvar prebuiltDocuments = {lookup_json};\n"

# Write the output to lunr_index.js.
with open('lunr_index.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("lunr_index.js has been generated successfully.")
