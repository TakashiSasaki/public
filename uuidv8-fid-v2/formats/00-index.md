# UUIDv8-FID-v2 Format Specifications

This directory is reserved for concrete UUIDv8-FID-v2 Format ID specifications.

A concrete payload format becomes assigned only when:

1. the Format ID is listed as assigned in `../20-registry.md`; and
2. a referenced format-specific specification defines the payload layout and normative interpretation.

This directory does not itself assign any Format ID.

## Current Assignments

The following concrete UUIDv8-FID-v2 payload formats are assigned:

| Format ID | Name | Specification |
|---:|---|---|
| `0x10` | `time48-rand` | `10-time48-rand.md` |

## Reserved and Unassigned Space

The UUIDv8-FID-v2 registry currently defines:

```text
0x00..0x0f  reserved
0x10..0xef  unassigned / available for future assignment
0xf0..0xff  reserved
```

Future format-specific documents SHOULD be named by Format ID and short symbolic name, for example:

`10-example-name.md`

The example above is illustrative only and does not assign "format_id = 0x10".
