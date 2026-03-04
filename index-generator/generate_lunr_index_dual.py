# File: generate_lunr_index_dual.py
# This script reads all .txt and .md files in the current directory,
# applies dual tokenization (using Janome for Japanese and a simple whitespace-based tokenizer for English),
# builds a unified Lunr index that supports mixed-language documents,
# and writes the index and document lookup to lunr_index.js.
# The output JSON is minified to reduce file size.
#
# Required packages: pip install lunr janome

import os
import json
from janome.tokenizer import Tokenizer
from lunr import lunr

# Initialize Janome tokenizer for Japanese text.
japanese_tokenizer = Tokenizer()

def tokenize_japanese(text):
    """
    Tokenize Japanese text using Janome.
    For each token, use the base form if available (or the surface form if not),
    then return a space-separated string of tokens.
    """
    tokens = []
    for token in japanese_tokenizer.tokenize(text):
        base = token.base_form
        if base == "*":  # If no base form is available, use the surface form.
            base = token.surface
        tokens.append(base)
    return " ".join(tokens)

def tokenize_english(text):
    """
    Tokenize English text by converting to lowercase and splitting on whitespace.
    Returns a normalized space-separated string of tokens.
    """
    return " ".join(text.lower().split())

def dual_tokenize(text):
    """
    Apply both the Japanese and English tokenizers to the text and merge the results.
    This ensures that for documents containing mixed Japanese and English,
    tokens from both languages are included in the index.
    """
    tokens_jp = tokenize_japanese(text)
    tokens_en = tokenize_english(text)
    # Merge token streams (simple concatenation with a space separator).
    return tokens_jp + " " + tokens_en

def main():
    documents = []
    lookup = {}
    file_count = 0

    print("Starting dual tokenization index generation (Japanese + English)...")

    # Process all .txt and .md files in the current directory.
    for filename in os.listdir('.'):
        if filename.endswith('.txt') or filename.endswith('.md'):
            file_count += 1
            print(f"Processing file {file_count}: {filename}")
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue

            # Use dual tokenization: apply both Japanese and English tokenizers.
            tokenized_content = dual_tokenize(content)
            # Use the filename (without extension) as the document ID and title.
            doc_id = os.path.splitext(filename)[0]
            documents.append({
                'id': doc_id,
                'title': doc_id,
                'body': tokenized_content
            })
            # Create a lookup entry with a summary (first 100 characters).
            summary = content[:100] + "..." if len(content) > 100 else content
            lookup[doc_id] = {
                'title': doc_id,
                'url': filename,  # Modify if the URL should point to an HTML version.
                'summary': summary
            }
    
    print(f"Total files processed: {file_count}")
    print(f"Total documents to index: {len(documents)}")

    # Build the unified Lunr index.
    print("Building the unified Lunr index using dual tokenization...")
    idx = lunr(ref='id', fields=['title', 'body'], documents=documents)
    print("Lunr index built successfully.")

    # Serialize the index and print details.
    index_data = idx.serialize()
    num_terms = len(index_data.get('invertedIndex', {}))
    fields_indexed = index_data.get('fields', [])
    print("Index Details:")
    print(f"  Number of terms: {num_terms}")
    print(f"  Indexed fields: {fields_indexed}")

    # Minify JSON output to reduce file size.
    index_json = json.dumps(index_data, separators=(',', ':'), ensure_ascii=False)
    lookup_json = json.dumps(lookup, separators=(',', ':'), ensure_ascii=False)
    js_content = f"var prebuiltIndexData={index_json};\nvar prebuiltDocuments={lookup_json};\n"

    # Write the output to lunr_index.js.
    with open('lunr_index.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print("lunr_index.js has been generated successfully.")

if __name__ == "__main__":
    main()
