# UUIDv8-FID-v2 Structural Conformance Test Vectors

This document contains derived conformance material for implementers to verify parsing, extraction, and validation behavior. It does not introduce new normative requirements and does not assign any new Format ID. The test vectors are explicitly derived from the existing normative rules in the specification.

## Validation Outcomes Summary

| Case | Description | UUID | Format ID status | Basic UUIDv8 | UUIDv8-FID-v2 structural | Profile | Strict | Generation |
| ---- | ----------- | ---- | ---------------- | ------------ | ------------------------ | ------- | ------ | ---------- |
| A | Assigned `time48-rand` | `00000000-0000-8100-8000-000000000000` | assigned `0x10` | pass | pass | pass if `time48-rand` is supported | pass | yes |
| B | Unassigned but structurally valid | `00000000-0000-8700-8a00-000000000000` | unassigned `0x7a` | pass | pass | fail unless a future specification assigns and the implementation supports `0x7a` | fail in the current registry | no |
| C | Reserved low range | `00000000-0000-8000-8000-000000000000` | reserved `0x00` | pass | pass | fail because `0x00` is reserved | fail because `0x00` is reserved | no |
| D | Reserved high range | `00000000-0000-8f00-8000-000000000000` | reserved `0xf0` | pass | pass | fail because `0xf0` is reserved | fail because `0xf0` is reserved | no |
| E | Invalid UUID version | `00000000-0000-7100-8000-000000000000` | n/a | fail | fail | fail | fail | no |
| F | Invalid UUID variant | `00000000-0000-8100-c000-000000000000` | n/a | fail | fail | fail | fail | no |
| G | Invalid reserved bits in Part 4 | `00000000-0000-8100-b000-000000000000` | n/a | pass | fail | fail | fail | no |
| H | Nonzero `part3_reserved_octet` | `00000000-0000-8101-8000-000000000000` | assigned `0x10` | pass | pass | pass if the implementation supports `format_id = 0x10` and does not apply strict reserved-octet policy at the profile-validation level | fail | no |
| I | Nonzero `part4_reserved_octet` | `00000000-0000-8100-8001-000000000000` | assigned `0x10` | pass | pass | pass if the implementation supports `format_id = 0x10` and does not apply strict reserved-octet policy at the profile-validation level | fail | no |

## Detailed Extracted Fields

### Case A: Assigned valid `time48-rand` center

```text
version              = 0x8
variant              = 0b10
part4_reserved_bits  = 0b00
format_type          = 0x1
format_subtype       = 0x0
format_id            = 0x10
part3_reserved_octet = 0x00
part4_reserved_octet = 0x00
```

### Case B: Unassigned but structurally valid Format ID

```text
version              = 0x8
variant              = 0b10
part4_reserved_bits  = 0b00
format_type          = 0x7
format_subtype       = 0x0a
format_id            = 0x7a
part3_reserved_octet = 0x00
part4_reserved_octet = 0x00
```

*Note: This is an extraction example only. It does not assign `format_id = 0x7a`.*

### Case C: Reserved low range, structurally valid but not generatable

```text
version              = 0x8
variant              = 0b10
part4_reserved_bits  = 0b00
format_type          = 0x0
format_subtype       = 0x0
format_id            = 0x00
part3_reserved_octet = 0x00
part4_reserved_octet = 0x00
```

### Case D: Reserved high range, structurally valid but not generatable

```text
version              = 0x8
variant              = 0b10
part4_reserved_bits  = 0b00
format_type          = 0xf
format_subtype       = 0x0
format_id            = 0xf0
part3_reserved_octet = 0x00
part4_reserved_octet = 0x00
```

### Case E: Invalid UUID version

```text
version              = 0x7
```

### Case F: Invalid UUID variant

```text
variant              = 0b11
```

### Case G: Invalid UUIDv8-FID-v2 reserved bits in Part 4

```text
version              = 0x8
variant              = 0b10
part4_reserved_bits  = 0b11
```

### Case H: Nonzero `part3_reserved_octet`

```text
version              = 0x8
variant              = 0b10
part4_reserved_bits  = 0b00
format_type          = 0x1
format_subtype       = 0x0
format_id            = 0x10
part3_reserved_octet = 0x01
part4_reserved_octet = 0x00
```

### Case I: Nonzero `part4_reserved_octet`

```text
version              = 0x8
variant              = 0b10
part4_reserved_bits  = 0b00
format_type          = 0x1
format_subtype       = 0x0
format_id            = 0x10
part3_reserved_octet = 0x00
part4_reserved_octet = 0x01
```

## Validation Notes

* **Structural validation vs. profile validation**: Structural validation is not the same as profile validation. A UUID may be structurally sound according to UUIDv8-FID-v2 rules but fail to align with known formats in a specific profile.
* **Unknown/unassigned Format IDs**: Unknown and unassigned Format IDs can be extracted but do not pass profile validation.
* **Reserved Format IDs**: Reserved Format IDs are structurally extractable but must not be generated.
* **Nonzero reserved octets**: Nonzero reserved octets are allowed to be parsed in forward-compatible mode but fail strict validation.
* **`part4_reserved_bits` vs. reserved octets**: `part4_reserved_bits` differs from the reserved octets. Nonzero `part4_reserved_bits` fails UUIDv8-FID-v2 structural validation.
