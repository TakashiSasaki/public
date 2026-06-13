# UUIDv8-FID-v2 Format Specification Template

This file is a template for future concrete UUIDv8-FID-v2 Format ID specifications.

Using this template does not assign a Format ID. A Format ID is assigned only when the registry in `../20-registry.md` lists the value as assigned and references the completed format-specific specification.

## 1. Status

Status: Template only; not an assigned format.

## 2. Format ID

```text
format_type    = 0x?
format_subtype = 0x?
format_id      = 0x??
```

## 3. Name

Short symbolic name:

TBD

## 4. Payload Layout

Specify the normative interpretation of:

Part 1: bits  0..31
Part 2: bits 32..47
Part 5: bits 80..127

The UUIDv8-FID-v2 control fields are defined by the main specification and MUST NOT be redefined here:

```text
bits 48..51  version = 1000
bits 52..55  format_id_hi4 = format_type
bits 56..63  part3_reserved_octet
bits 64..65  variant = 10
bits 66..67  part4_reserved_bits = 00
bits 68..71  format_id_lo4 = format_subtype
bits 72..79  part4_reserved_octet
```

## 5. Byte Order and Integer Interpretation

TBD.

## 6. Timestamp Semantics

State whether the format contains a timestamp.

If a timestamp is used, specify:

- epoch;
- unit;
- bit width;
- rollover behavior;
- ordering properties.

## 7. Randomness, Counter, Node, Dataset, Hash, or Namespace Fields

Specify any randomness, counter, node-id, dataset-id, hash, namespace-derived, or application-specific fields.

## 8. Generation Requirements

TBD.

## 9. Parsing Requirements

TBD.

## 10. Validation Requirements

TBD.

## 11. Uniqueness Assumptions

TBD.

## 12. Security and Privacy Considerations

State whether generated UUIDs reveal timestamps, node identifiers, dataset identifiers, counters, hashes, or other potentially sensitive information.

State whether UUID values are intended to be unpredictable.

## 13. Test Vectors

TBD.

## 14. Registry Entry

When this template is used for an assigned format, add or update the corresponding registry entry in `../20-registry.md`.

Example table shape:

| format_type | format_subtype | format_id | Name | Status   | Reference     | Notes |
| ----------- | -------------- | --------- | ---- | -------- | ------------- | ----- |
| `0x?`       | `0x?`          | `0x??`    | TBD  | assigned | This document | TBD   |
