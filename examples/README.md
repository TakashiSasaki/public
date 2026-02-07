# Examples Directory

This directory contains example files demonstrating the usage of get-a-grip tools and schemas.

## Current Files

- **`example.efu`** - Example Everything File List (EFU) format file
- **`example.jsonld`** - Example JSON-LD output

## Planned Structure

This directory will be organized in the future to provide clear examples for different use cases:

```
examples/
├── filelist/          # File list processing examples
├── probe/             # File probing examples
├── dirtree/           # Directory tree examples
└── quickstart/        # Getting started examples
```

## Usage

These examples can be used to:

1. **Learn the tools** - See how different tools work with sample data
2. **Test functionality** - Verify that tools produce expected output
3. **Quick start** - Copy and modify for your own use cases

## File Formats

### EFU (Everything File List)

The `.efu` format is used by the Everything search tool. Example files show how get-a-grip processes this format.

### JSON-LD

JSON-LD (JSON for Linking Data) is used for structured output that follows the get-a-grip schema definitions.

## Related Directories

- **`schema/`** - Schema definitions for JSON-LD output
- **`tests/`** - Test files (for automated testing)
- **`reports/`** - Generated reports and validation results

## Contributing Examples

When adding new examples:

1. Include a descriptive filename
2. Add comments or documentation explaining the example
3. Provide both input and expected output when applicable
4. Update this README to list the new example
