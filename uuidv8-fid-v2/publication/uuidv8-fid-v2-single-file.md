This is generated dry-run output assembled from the split UUIDv8-FID-v2 source files. The canonical specification remains the split files under uuidv8-fid-v2/.

<!-- Source: uuidv8-fid-v2/01-status-scope.md -->

# 1. Status of This Document

This document defines Version 2 of the **Format-ID UUIDv8 Profile**, abbreviated as **UUIDv8-FID-v2**.

UUIDv8-FID-v2 is an application-defined UUID version 8 profile. It preserves the standard UUID version and variant fields and defines an 8-bit Format ID for identifying application-defined UUIDv8 payload formats.

UUIDv8-FID-v2 is intended for developers implementing UUID generation, parsing, validation, serialization, deserialization, indexing, and library-level interoperability.

This document defines the field format, bit-level structure, initial Format ID registry, and initial assigned payload format for UUIDv8-FID-v2.

# 2. Scope

UUIDv8-FID-v2 defines the bit-level structure of a subset of UUID version 8 values.

This specification defines:

* the placement of the UUID `version` field;
* the placement of the UUID `variant` field;
* an 8-bit logical `format_id` field;
* the physical field fragments `format_id_hi4` and `format_id_lo4`;
* the semantic field names `format_type` and `format_subtype`;
* two reserved bits named `part4_reserved_bits`;
* two reserved octets named `part3_reserved_octet` and `part4_reserved_octet`;
* extraction, construction, and validation rules for UUIDv8-FID-v2 values.

This specification defines the UUIDv8-FID-v2 field format and includes the initial UUIDv8-FID-v2 Format ID registry.

This specification does not define:

* the semantics of individual `format_type` values;
* the semantics of individual `format_subtype` values;
* the semantics of individual `format_id` values;
* the payload layout of Part 1, Part 2, or Part 5;
* timestamp semantics;
* uniqueness guarantees for any particular Format ID;
* privacy or security properties of any concrete assigned format.

The field-format sections define the bit-level structure, extraction, construction, and validation rules for UUIDv8-FID-v2 values.

The registry chapter defines assignment status and assignment policy for Format ID values. This initial version assigns `format_id = 0x10` as the first concrete UUIDv8-FID-v2 payload format.

Concrete payload layouts and format-specific semantics are still defined by profile-specific documents.


<!-- Source: uuidv8-fid-v2/02-terminology.md -->

# 3. Terminology

The key words `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` are to be interpreted as normative requirements.

The following terms are used in this document.

`UUIDv8-FID-v2`
: The Format-ID UUIDv8 Profile Version 2 defined by this document.

`format_id`
: An 8-bit logical identifier composed of `format_type` and `format_subtype`.

`format_type`
: The upper 4 bits of `format_id`. This field identifies a broad payload family. This terminology section defines the field and its location. Concrete assignments are defined by the registry chapter and referenced format-specific documents.

`format_subtype`
: The lower 4 bits of `format_id`. This field identifies a concrete payload layout within a `format_type` family. This terminology section defines the field and its location. Concrete assignments are defined by the registry chapter and referenced format-specific documents.

`format_id_hi4`
: The physical 4-bit field fragment occupying bits 52 through 55. Semantically, this field is `format_type`.

`format_id_lo4`
: The physical 4-bit field fragment occupying bits 68 through 71. Semantically, this field is `format_subtype`.

`part3_control_octet`
: The octet containing the UUID version field and `format_id_hi4`.

`part3_reserved_octet`
: The low-order octet of Part 3. This octet is reserved for future definition.

`part4_control_octet`
: The octet containing the UUID variant field, `part4_reserved_bits`, and `format_id_lo4`.

`part4_reserved_bits`
: The two bits occupying bits 66 through 67. These bits are reserved and are set to zero in UUIDv8-FID-v2.

`part4_reserved_octet`
: The low-order octet of Part 4. This octet is reserved for future definition.

`Part 1` through `Part 5`
: The five hexadecimal groups in the canonical UUID string representation:

```text
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Part1    Part2 Part3 Part4 Part5
```


<!-- Source: uuidv8-fid-v2/03-string-representation.md -->

# 4. UUID String Representation

UUIDv8-FID-v2 uses the standard canonical UUID textual representation:

```text
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

where each `x` is a lowercase or uppercase hexadecimal digit. Implementations SHOULD emit lowercase hexadecimal digits, but parsers MAY accept uppercase hexadecimal digits.

The five parts are:

```text
Part1: 32 bits,  8 hex digits
Part2: 16 bits,  4 hex digits
Part3: 16 bits,  4 hex digits
Part4: 16 bits,  4 hex digits
Part5: 48 bits, 12 hex digits
```

UUIDv8-FID-v2 does not change the canonical UUID string length, hyphen positions, or hexadecimal encoding.

In canonical UUID string form, the UUIDv8-FID-v2 control structure can be shown schematically as:

```text
xxxxxxxx-xxxx-8Trr-8Srr-xxxxxxxxxxxx
```

where:

```text
8   in Part 3 is the UUID version nibble for UUID version 8
T   in Part 3 is format_type, physically stored as format_id_hi4
rr  in Part 3 is part3_reserved_octet
8   in Part 4 is the hexadecimal digit produced by variant = 10 and part4_reserved_bits = 00
S   in Part 4 is format_subtype, physically stored as format_id_lo4
rr  in Part 4 is part4_reserved_octet
```

Generators conforming to this version of the specification set the reserved octets to zero. Generated UUIDv8-FID-v2 values therefore have the following center form:

```text
xxxxxxxx-xxxx-8T00-8S00-xxxxxxxxxxxx
```


<!-- Source: uuidv8-fid-v2/04-bit-layout.md -->

# 5. Bit Numbering

This document numbers bits from 0 to 127, in network byte order, from the most significant bit of the UUID to the least significant bit of the UUID.

Octets are numbered from 0 to 15.

```text
Octet 0  contains bits   0..7
Octet 1  contains bits   8..15
...
Octet 15 contains bits 120..127
```

The canonical UUID parts correspond to octets as follows:

```text
Part1: octets  0..3
Part2: octets  4..5
Part3: octets  6..7
Part4: octets  8..9
Part5: octets 10..15
```

# 6. Overall Layout

UUIDv8-FID-v2 has the following bit layout:

```text
bits    field

0..31   part1
32..47  part2

48..51  version = 1000
52..55  format_id_hi4 = format_type
56..63  part3_reserved_octet

64..65  variant = 10
66..67  part4_reserved_bits = 00
68..71  format_id_lo4 = format_subtype
72..79  part4_reserved_octet

80..127 part5
```

The logical Format ID is computed as:

```text
format_id = (format_type << 4) | format_subtype
```

Equivalently:

```text
format_id = (format_id_hi4 << 4) | format_id_lo4
```

The valid numeric range of `format_id` is:

```text
0x00..0xff
```

or equivalently:

```text
0..255
```


<!-- Source: uuidv8-fid-v2/05-part3-part4-layout.md -->

# 7. Part 3 Layout

Part 3 is 16 bits wide and occupies bits 48 through 63.

```text
bits 48..51  version
bits 52..55  format_id_hi4 = format_type
bits 56..63  part3_reserved_octet
```

The first octet of Part 3 is named `part3_control_octet`.

```text
part3_control_octet = bits 48..55
```

It is composed as follows:

```text
bits 48..51  version = 1000
bits 52..55  format_id_hi4 = format_type
```

The UUID version field MUST be `1000`, indicating UUID version 8.

The low-order octet of Part 3 is named `part3_reserved_octet`.

```text
part3_reserved_octet = bits 56..63
```

Generators conforming to this version of the specification MUST set `part3_reserved_octet` to `0x00`.

Parsers conforming to this version of the specification SHOULD ignore `part3_reserved_octet` unless a stricter validation mode is explicitly requested.

# 8. Part 4 Layout

Part 4 is 16 bits wide and occupies bits 64 through 79.

```text
bits 64..65  variant
bits 66..67  part4_reserved_bits
bits 68..71  format_id_lo4 = format_subtype
bits 72..79  part4_reserved_octet
```

The first octet of Part 4 is named `part4_control_octet`.

```text
part4_control_octet = bits 64..71
```

It is composed as follows:

```text
bits 64..65  variant = 10
bits 66..67  part4_reserved_bits = 00
bits 68..71  format_id_lo4 = format_subtype
```

The UUID variant field MUST be `10`.

The `part4_reserved_bits` field MUST be `00` for UUIDv8-FID-v2 structural validity.

The low-order octet of Part 4 is named `part4_reserved_octet`.

```text
part4_reserved_octet = bits 72..79
```

Generators conforming to this version of the specification MUST set `part4_reserved_octet` to `0x00`.

Parsers conforming to this version of the specification SHOULD ignore `part4_reserved_octet` unless a stricter validation mode is explicitly requested.


<!-- Source: uuidv8-fid-v2/06-format-id-fields.md -->

# 9. The Format ID Fields

UUIDv8-FID-v2 defines an 8-bit logical field named `format_id`.

The Format ID is composed of two semantic nibbles:

```text
format_type    = bits 52..55
format_subtype = bits 68..71
```

The same physical fields are named:

```text
format_id_hi4 = bits 52..55
format_id_lo4 = bits 68..71
```

The semantic mapping is:

```text
format_type    = format_id_hi4
format_subtype = format_id_lo4
```

The numeric value of `format_id` is computed as:

```text
format_id = (format_type << 4) | format_subtype
```

An implementation MAY inspect `format_type` alone for coarse dispatch, classification, filtering, indexing policy, or privacy policy, if such behavior is defined by a registry or profile-specific document.

An implementation MUST NOT fully parse or generate a UUIDv8-FID-v2 payload based only on `format_type` unless the corresponding `format_type` specification explicitly defines a single layout for all of its subtypes.

This field-format section does not itself assign meanings to `format_type`, `format_subtype`, or `format_id` values. Concrete assignments are defined by the registry chapter and referenced format-specific documents.


<!-- Source: uuidv8-fid-v2/07-parsing-generation.md -->

# 10. Parsing Algorithm

A parser for UUIDv8-FID-v2 SHOULD perform the following steps.

1. Parse the input as a UUID using the standard UUID textual or binary representation.
2. Verify that the UUID variant field is `10`.
3. Verify that the UUID version field is `1000`.
4. Verify that `part4_reserved_bits` is `00` for UUIDv8-FID-v2 structural validation.
5. Extract `format_id_hi4` from bits 52 through 55.
6. Extract `format_id_lo4` from bits 68 through 71.
7. Interpret `format_id_hi4` as `format_type`.
8. Interpret `format_id_lo4` as `format_subtype`.
9. Compute `format_id` as `(format_type << 4) | format_subtype`.
10. Extract `part3_reserved_octet` from bits 56 through 63.
11. Extract `part4_reserved_octet` from bits 72 through 79.
12. Interpret the remaining fields according to the registry or profile-specific specification associated with the extracted Format ID.

A parser MAY reject UUIDs whose `part3_reserved_octet` or `part4_reserved_octet` is nonzero when operating in strict validation mode.

A parser SHOULD NOT reject such UUIDs by default solely because a reserved octet is nonzero, in order to allow forward-compatible parsing.

A parser SHOULD reject UUIDs whose `part4_reserved_bits` are nonzero when validating UUIDv8-FID-v2 structural conformance.

# 11. Generation Algorithm

A generator for a concrete UUIDv8-FID-v2 payload format SHOULD perform the following steps.

1. Select a `format_id` that is assigned by the UUIDv8-FID-v2 registry or by a referenced profile-specific specification.
2. Verify that the selected `format_id` is not reserved, unassigned, or deprecated unless the generator explicitly implements the referenced specification that permits such generation.
3. Derive:

```text
format_type    = (format_id >> 4) & 0x0f
format_subtype =  format_id       & 0x0f
```

4. Set the UUID version field to `1000`.
5. Set the UUID variant field to `10`.
6. Set `part4_reserved_bits` to `00`.
7. Store `format_type` in bits 52 through 55.
8. Store `format_subtype` in bits 68 through 71.
9. Set `part3_reserved_octet` to `0x00`.
10. Set `part4_reserved_octet` to `0x00`.
11. Populate Part 1, Part 2, and Part 5 according to the registry entry or profile-specific definition associated with the selected Format ID.

A generator MUST NOT generate a UUIDv8-FID-v2 value using a reserved Format ID value or reserved Format ID range unless a future specification explicitly changes its status.

A generator SHOULD NOT generate an unassigned Format ID as an interoperable UUIDv8-FID-v2 payload format.

A generator SHOULD NOT generate deprecated formats unless required for compatibility with an existing system and explicitly documented by the referenced specification.

A generator MUST NOT use `part4_reserved_bits`, `part3_reserved_octet`, or `part4_reserved_octet` for application data in this version of the specification.


<!-- Source: uuidv8-fid-v2/08-extraction-construction.md -->

# 12. Extraction Formulas

For implementations using octet-oriented access, the following formulas define extraction.

Let:

```text
octet6 = UUID octet 6
octet7 = UUID octet 7
octet8 = UUID octet 8
octet9 = UUID octet 9
```

Then:

```text
part3_control_octet   = octet6
part3_reserved_octet  = octet7
part4_control_octet   = octet8
part4_reserved_octet  = octet9

version               = (octet6 >> 4) & 0x0f
format_id_hi4         =  octet6       & 0x0f
format_type           =  format_id_hi4

variant               = (octet8 >> 6) & 0x03
part4_reserved_bits   = (octet8 >> 4) & 0x03
format_id_lo4         =  octet8       & 0x0f
format_subtype        =  format_id_lo4

format_id             = (format_type << 4) | format_subtype
```

For UUIDv8-FID-v2:

```text
version MUST be 0x8
variant MUST be 0b10
part4_reserved_bits MUST be 0b00
```

# 13. Construction Formulas

Given `format_type` and `format_subtype`, the control octets are constructed as follows:

```text
format_id_hi4 = format_type    & 0x0f
format_id_lo4 = format_subtype & 0x0f

part3_control_octet = 0x80 | format_id_hi4
part4_control_octet = 0x80 | format_id_lo4
```

The reserved fields are set as follows:

```text
part4_reserved_bits   = 0b00
part3_reserved_octet  = 0x00
part4_reserved_octet  = 0x00
```

The expression `0x80 | format_id_lo4` sets the two most significant bits of `part4_control_octet` to `10`, sets bits 66 through 67 to `00`, and stores `format_id_lo4` in the low-order nibble.


<!-- Source: uuidv8-fid-v2/09-validation.md -->

# 14. Validation Levels

Implementations MAY support multiple validation levels.

## 14.1 Basic UUIDv8 Validation

Basic validation checks only:

```text
variant == 0b10
version == 0x8
```

This level determines whether the UUID is structurally compatible with UUID version 8.

## 14.2 UUIDv8-FID-v2 Structural Validation

UUIDv8-FID-v2 structural validation checks:

```text
variant == 0b10
version == 0x8
part4_reserved_bits == 0b00
```

This level determines whether the UUID is structurally compatible with UUIDv8-FID-v2 extraction.

## 14.3 Profile Validation

Profile validation checks:

```text
variant == 0b10
version == 0x8
part4_reserved_bits == 0b00
format_id is known to the implementation
format_id is assigned, or deprecated and explicitly accepted for compatibility
format_id is not reserved
```

This level determines whether the implementation knows how to interpret the UUID payload according to a registry entry or profile-specific specification.

Unknown, unassigned, and reserved Format ID values MAY still be extracted and reported, but they do not pass profile validation.

## 14.4 Strict Validation

Strict validation checks:

```text
variant == 0b10
version == 0x8
part4_reserved_bits == 0b00
format_id is known to the implementation
format_id is assigned, or deprecated and explicitly accepted for compatibility
format_id is not reserved
part3_reserved_octet == 0x00
part4_reserved_octet == 0x00
```

This level determines whether the UUID conforms exactly to this version of UUIDv8-FID-v2, relies only on assigned or explicitly accepted formats, uses no reserved values, and ensures all reserved octets are zero.

## 14.5 Conformance Test Vectors

Derived conformance test vectors illustrating these validation levels are provided in `conformance/structural-test-vectors.md` and its machine-readable companion `conformance/structural-test-vectors.json`.


<!-- Source: uuidv8-fid-v2/11-compatibility-security.md -->

# 15. Relationship to UUIDv8-FID Version 1

UUIDv8-FID-v2 supersedes UUIDv8-FID Version 1.

UUIDv8-FID Version 1 defined a 10-bit logical `format_id` split into `format_id_hi4` and `format_id_lo6`.

UUIDv8-FID-v2 replaces that field with an 8-bit logical `format_id` composed of `format_type` and `format_subtype`, physically stored as `format_id_hi4` and `format_id_lo4`, and reserves bits 66 through 67.

UUIDv8-FID Version 1 and UUIDv8-FID-v2 are not self-distinguishing from the UUID bit pattern alone. Implementations MUST know which profile version they implement. New implementations SHOULD implement UUIDv8-FID-v2.

# 16. Compatibility Considerations

UUIDv8-FID-v2 values are valid UUID version 8 values when the standard UUID version and variant fields are interpreted according to the UUID specification.

Systems that only check UUID syntax, version, and variant should treat UUIDv8-FID-v2 values as UUIDv8 values.

Systems that require semantic interpretation of the UUID payload need UUIDv8-FID-v2-specific support and a registry or profile-specific definition for the extracted `format_type` and `format_subtype`.

UUIDv8-FID-v2 does not provide compatibility with UUIDv1, UUIDv5, UUIDv7, or UUIDv8-FID Version 1 semantics. A system containing UUIDv1, UUIDv5, UUIDv7, UUIDv8-FID Version 1, and UUIDv8-FID-v2 values SHOULD inspect the UUID version field and use profile-specific parsing rules where applicable.

# 17. Security Considerations

UUIDv8-FID-v2 by itself does not define randomness, timestamp placement, node identifiers, cryptographic hashes, namespace-derived identifiers, counters, or dataset identifiers.

Security and privacy properties depend on the registry or profile-specific definition associated with each `format_type` and `format_subtype` pair.

A format-specific definition SHOULD state whether generated UUIDs reveal timestamps, node identifiers, dataset identifiers, counters, hashes, or other potentially sensitive information.

A format-specific definition SHOULD state whether UUID values are intended to be unpredictable.


<!-- Source: uuidv8-fid-v2/12-examples-summary.md -->

# 18. Example: Extracting the Format ID

Suppose a UUID has the following relevant octets:

```text
octet6 = 0x87
octet8 = 0x8a
```

Then:

```text
version             = 0x8
format_id_hi4       = 0x7
format_type         = 0x7

variant             = 0b10
part4_reserved_bits = 0b00
format_id_lo4       = 0x0a
format_subtype      = 0x0a
```

Therefore:

```text
format_id = (0x7 << 4) | 0x0a
          = 0x7a
```

The UUID is structurally a UUIDv8-FID-v2 value with `format_type = 0x7`, `format_subtype = 0x0a`, and `format_id = 0x7a`, assuming the complete UUID is otherwise syntactically valid.

A structurally valid UUIDv8-FID-v2 value carrying this unassigned Format ID would have the following center form:

```text
xxxxxxxx-xxxx-8700-8a00-xxxxxxxxxxxx
```

This example demonstrates extraction and structural layout only; it does not assign `format_id = 0x7a`.

The first assigned UUIDv8-FID-v2 payload format is `format_id = 0x10`, defined in `formats/10-time48-rand.md`.

Deterministic construction and parsing test vectors for the first assigned format are provided in `formats/10-time48-rand.md`.

Structural conformance test vectors covering validation edge cases and unassigned ranges are provided in `conformance/structural-test-vectors.md`.

Derived implementation guidance and pseudocode are provided in `implementation/pseudocode.md` and `implementation/implementation-checklist.md`.

# 19. Summary

UUIDv8-FID-v2 is a UUID version 8 profile that introduces an 8-bit logical Format ID.

The Format ID is composed of two semantic nibbles:

```text
format_type:    bits 52..55
format_subtype: bits 68..71
```

The same physical fields are named:

```text
format_id_hi4: bits 52..55
format_id_lo4: bits 68..71
```

The profile also defines reserved fields:

```text
part4_reserved_bits:  bits 66..67
part3_reserved_octet: bits 56..63
part4_reserved_octet: bits 72..79
```

The core layout is:

```text
bits  48..51   version = 1000
bits  52..55   format_id_hi4 = format_type
bits  56..63   part3_reserved_octet

bits  64..65   variant = 10
bits  66..67   part4_reserved_bits = 00
bits  68..71   format_id_lo4 = format_subtype
bits  72..79   part4_reserved_octet
```

The logical Format ID is reconstructed as:

```text
format_id = (format_type << 4) | format_subtype
```

Generated UUIDv8-FID-v2 values have the following center form:

```text
xxxxxxxx-xxxx-8T00-8S00-xxxxxxxxxxxx
```


<!-- Source: uuidv8-fid-v2/20-registry.md -->

# 20. Format ID Registry and Assignment Policy

## 20.1 Overview and Scope

This chapter defines the registry for **UUIDv8-FID-v2 Format Type and Subtype assignments**, previously maintained as the separate **UUIDv8-FID-v2 Registry**.

The field-format sections define the bit-level structure of UUIDv8-FID-v2 values. This registry chapter defines concrete assignments for `format_type`, `format_subtype`, and the combined `format_id` value.

This initial registry defines the initial registry structure and assigns the first concrete payload format, `format_id = 0x10`, while leaving `0x11..0xef` available for future assignment.

UUIDv8-FID-v2 defines an 8-bit Format ID composed of two semantic nibbles:

```text
format_type    = bits 52..55
format_subtype = bits 68..71
```

The combined numeric identifier is:

```text
format_id = (format_type << 4) | format_subtype
```

The canonical center form of a generated UUIDv8-FID-v2 value is:

```text
xxxxxxxx-xxxx-8T00-8S00-xxxxxxxxxxxx
```

where `T` is `format_type` and `S` is `format_subtype`.

This registry assigns meanings to selected `format_type` and `format_subtype` values. The field-format sections remain valid independently of this registry.

This registry defines:

* assigned `format_type` values;
* assigned `format_subtype` values within each `format_type`;
* combined `format_id` values;
* reserved `format_id` ranges;
* names for assigned formats;
* references to profile-specific payload-layout specifications;
* assignment status for each value or range.

This registry does not redefine:

* the UUID version field;
* the UUID variant field;
* the physical placement of `format_type` or `format_subtype`;
* the UUIDv8-FID-v2 reserved bits or reserved octets;
* the extraction and construction formulas for UUIDv8-FID-v2.

Those items are defined by the UUIDv8-FID-v2 field-format sections.

## 20.2 Terminology

The key words `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` are to be interpreted as normative requirements.

`UUIDv8-FID-v2 Registry`
: The assignments and policy defined in this chapter.

`format_type`
: The upper 4 bits of the UUIDv8-FID-v2 Format ID. A `format_type` identifies a broad payload family.

`format_subtype`
: The lower 4 bits of the UUIDv8-FID-v2 Format ID. A `format_subtype` identifies a concrete payload layout within a `format_type` family.

`format_id`
: The combined 8-bit identifier equal to `(format_type << 4) | format_subtype`.

`assigned`
: A registry entry whose semantics and payload layout are defined by a referenced specification.

`reserved`
: A registry entry or range that MUST NOT be generated unless a future specification changes its status.

`unassigned`
: A registry entry that has not yet been assigned.

`deprecated`
: A registry entry that remains recognizable for compatibility but SHOULD NOT be generated by new implementations.

## 20.3 Registry Model

The registry is hierarchical.

A `format_type` value identifies a broad payload family.

A `format_subtype` value identifies a concrete payload layout within that family.

The combined `format_id` is the canonical numeric identifier for a concrete UUIDv8-FID-v2 format.

Implementations MAY inspect `format_type` alone for coarse dispatch, classification, filtering, indexing policy, or privacy policy.

Implementations MUST NOT fully parse or generate a UUIDv8-FID-v2 payload based only on `format_type` unless the corresponding `format_type` entry explicitly defines a single layout for all of its subtypes.

## 20.4 Assignment Requirements

A concrete assignment SHOULD specify:

* `format_type`;
* `format_subtype`;
* combined `format_id`;
* symbolic name;
* status;
* reference document;
* payload layout of Part 1, Part 2, and Part 5;
* byte order and integer interpretation;
* timestamp epoch, unit, and rollover behavior, if timestamps are used;
* randomness, counter, node-id, dataset-id, hash, or namespace requirements, if any;
* uniqueness assumptions;
* privacy and predictability considerations;
* canonical test vectors.

A new `format_id` SHOULD be assigned only when the binary payload layout or normative interpretation changes.

A new `format_subtype` SHOULD NOT be assigned merely to name an application domain, object class, database table, or dataset.

Application-specific object types SHOULD normally be encoded inside the payload or in application metadata, not by assigning new UUIDv8-FID-v2 Format IDs.

## 20.5 Registry Table Format

The registry table uses the following columns.

| Column | Meaning |
|---|---|
| `format_type` | Upper 4-bit semantic field |
| `format_subtype` | Lower 4-bit semantic field |
| `format_id` | Combined 8-bit value |
| `Name` | Short symbolic name |
| `Status` | `reserved`, `assigned`, `unassigned`, or `deprecated` |
| `Reference` | Specification defining the payload layout |
| `Notes` | Non-normative summary |

## 20.6 Format Type Registry

This section assigns or reserves `format_type` values.

This initial version assigns `format_type = 0x1` as the initial time-carrying payload family. Values `0x2..0xe` remain unassigned until separate profile-specific decisions are made.

| format_type | Name | Status | Reference | Notes |
|---:|---|---|---|---|
| `0x0` | Reserved | reserved | This document | Reserved for control, null, registry-internal, meta-format, or future registry use. All Format ID values `0x00..0x0f` are reserved unless a future specification explicitly assigns one or more values in this range. |
| `0x1` | time48 | assigned | `formats/10-time48-rand.md` | Time-carrying payload family. Initial subtype `0x0` is assigned as `time48-rand`. |
| `0x2` | Unassigned | unassigned |  | Available for future assignment. |
| `0x3` | Unassigned | unassigned |  | Available for future assignment. |
| `0x4` | Unassigned | unassigned |  | Available for future assignment. |
| `0x5` | Unassigned | unassigned |  | Available for future assignment. |
| `0x6` | Unassigned | unassigned |  | Available for future assignment. |
| `0x7` | Unassigned | unassigned |  | Available for future assignment. |
| `0x8` | Unassigned | unassigned |  | Available for future assignment. |
| `0x9` | Unassigned | unassigned |  | Available for future assignment. |
| `0xa` | Unassigned | unassigned |  | Available for future assignment. |
| `0xb` | Unassigned | unassigned |  | Available for future assignment. |
| `0xc` | Unassigned | unassigned |  | Available for future assignment. |
| `0xd` | Unassigned | unassigned |  | Available for future assignment. |
| `0xe` | Unassigned | unassigned |  | Available for future assignment. |
| `0xf` | Reserved | reserved | This document | Reserved for escape, diagnostics, extended-format signaling, or future extension mechanisms. All Format ID values `0xf0..0xff` are reserved unless a future specification explicitly assigns one or more values in this range. |

## 20.7 Format ID Registry

This section assigns concrete `format_id` values and reserved `format_id` ranges.

A `format_id` value is concrete only when its payload layout and normative interpretation are assigned by this registry or by a referenced profile-specific document.

This initial registry assigns `format_id = 0x10` as the first concrete UUIDv8-FID-v2 payload format.

### 20.7.1 Reserved Format ID Ranges

The following Format ID ranges are reserved:

| Format ID range | Status | Reference | Notes |
|---:|---|---|---|
| `0x00..0x0f` | reserved | This document | Reserved for null, control, registry-internal, meta-format, or future registry use. Generators MUST NOT generate values in this range unless a future specification assigns one or more values in this range. |
| `0xf0..0xff` | reserved | This document | Reserved for escape, diagnostics, extended-format signaling, or future extension mechanisms. Generators MUST NOT generate values in this range unless a future specification assigns one or more values in this range. |

The reserved ranges above intentionally correspond to `format_id_hi4 = 0x0` and `format_id_hi4 = 0xf`. This preserves extension space if a future specification assigns additional structure or hierarchical interpretation to the high-order and low-order nibbles of the Format ID.

### 20.7.2 Assignable Format ID Range

The following Format ID range is available for future assignment:

| Format ID range | Status | Reference | Notes |
|---:|---|---|---|
| `0x11..0xef` | unassigned | — | Available for future assignment by this registry or by referenced profile-specific documents. |

Unassigned Format ID values are available for future assignment, but they are not concrete payload formats until assigned by this registry or by a referenced profile-specific specification.

A new `format_id` SHOULD be assigned only when the binary payload layout or normative interpretation changes. A new Format ID SHOULD NOT be assigned merely to name an application domain, object class, database table, dataset, or deployment-specific category.

### 20.7.3 Individual Format ID Assignments

Individual assigned, deprecated, or specially reserved Format ID values MAY be listed in this section in future versions of this registry.

Format-specific payload layout specifications SHOULD be placed under `formats/` and referenced from this registry.

The following individual Format ID values are assigned:

| format_type | format_subtype | format_id | Name | Status | Reference | Notes |
|---:|---:|---:|---|---|---|---|
| `0x1` | `0x0` | `0x10` | `time48-rand` | assigned | `formats/10-time48-rand.md` | Part 5 contains a 48-bit Unix epoch millisecond timestamp; Part 1 and Part 2 contain 48 bits of random or profile-defined payload. |

All Format ID values in `0x11..0xef` are unassigned unless listed in a future version of this registry or in a referenced profile-specific document.

## 20.8 Unknown Values

Implementations SHOULD treat unknown `format_id` values as opaque UUIDv8-FID-v2 values.

Implementations MUST NOT reinterpret an unknown `format_id` value using another known format unless explicitly configured to do so.

Implementations MAY expose the extracted `format_type`, `format_subtype`, and `format_id` to callers even when the concrete payload layout is unknown.

## 20.9 Reserved Values

Reserved values and reserved ranges MUST NOT be generated.

Parsers MAY recognize reserved values and reserved ranges and report them distinctly from unassigned values.

A future version of this registry MAY change a reserved value or reserved range to assigned status if doing so is explicitly documented.

## 20.10 Deprecation

A deprecated entry remains part of the registry for recognition and migration.

New generators SHOULD NOT generate deprecated formats.

Parsers MAY continue to support deprecated formats for compatibility.

A deprecated entry SHOULD include migration guidance where possible.

## 20.11 Security and Privacy Considerations

This registry does not by itself define payload layouts, randomness, timestamps, node identifiers, dataset identifiers, hashes, or namespace-derived identifiers.

Each concrete assignment SHOULD document whether generated UUIDs reveal timestamps, node identifiers, dataset identifiers, counters, hashes, or other potentially sensitive information.

Each concrete assignment SHOULD document whether UUID values are intended to be unpredictable.

A `format_type` value MAY provide coarse privacy or indexing signals, but security-sensitive behavior SHOULD be based on the complete `format_id` and the referenced profile-specific specification.

## 20.12 Summary

The UUIDv8-FID-v2 Registry assigns meanings to `format_type`, `format_subtype`, and combined `format_id` values.

UUIDv8-FID-v2 field layout:

```text
format_type    = bits 52..55
format_subtype = bits 68..71
format_id      = (format_type << 4) | format_subtype
```

Generated UUIDv8-FID-v2 values have the following center form:

```text
xxxxxxxx-xxxx-8T00-8S00-xxxxxxxxxxxx
```

This initial registry reserves the Format ID ranges `0x00..0x0f` and `0xf0..0xff`, assigns `format_id = 0x10` as `time48-rand`, and leaves `0x11..0xef` to future registry updates or profile-specific documents.


<!-- Source: uuidv8-fid-v2/formats/10-time48-rand.md -->

# UUIDv8-FID-v2 Format 0x10: time48-rand

This document defines the UUIDv8-FID-v2 payload format assigned to `format_id = 0x10`.

## 1. Status

Status: Assigned.

This format is assigned by the UUIDv8-FID-v2 registry.

## 2. Format ID

```text
format_type    = 0x1
format_subtype = 0x0
format_id      = 0x10
```

## 3. Name

time48-rand

## 4. Payload Layout

The UUIDv8-FID-v2 control fields are defined by the main specification and MUST NOT be redefined by this format.

This format defines the payload fields as follows:

```text
bits    field

0..31    rand_a
32..47   rand_b

48..51   version = 1000
52..55   format_id_hi4 = format_type = 0x1
56..63   part3_reserved_octet = 0x00

64..65   variant = 10
66..67   part4_reserved_bits = 00
68..71   format_id_lo4 = format_subtype = 0x0
72..79   part4_reserved_octet = 0x00

80..127  unix_ts_ms
```

The canonical center form of generated values for this format is:

```text
xxxxxxxx-xxxx-8100-8000-xxxxxxxxxxxx
```

## 5. Byte Order and Integer Interpretation

`unix_ts_ms` is a 48-bit unsigned integer encoded in network byte order.

`rand_a` and `rand_b` are interpreted as opaque bit strings unless a profile-specific specification defines a stricter interpretation.

## 6. Timestamp Semantics

`unix_ts_ms` is the number of milliseconds elapsed since the Unix epoch:

```text
1970-01-01T00:00:00Z
```

The timestamp unit is milliseconds.

The timestamp field has width 48 bits.

This timestamp placement is intentionally compatible with the 48-bit Unix epoch millisecond timestamp used by UUID version 7, but it is placed in Part 5 rather than in Part 1 and Part 2.

## 7. Randomness, Counter, Node, Dataset, Hash, or Namespace Fields

`rand_a` and `rand_b` together provide 48 payload bits outside the UUIDv8-FID-v2 control fields and timestamp field.

Generators SHOULD fill `rand_a` and `rand_b` with cryptographically strong random or pseudorandom bits unless a profile-specific specification defines a counter, node identifier, dataset identifier, hash, namespace-derived value, or other structured interpretation.

If a structured interpretation is used for `rand_a` or `rand_b`, that interpretation MUST be documented by the profile-specific specification.

## 8. Generation Requirements

A generator for this format MUST:

1. use `format_id = 0x10`;
2. set `format_type = 0x1`;
3. set `format_subtype = 0x0`;
4. set the UUID version field to `1000`;
5. set the UUID variant field to `10`;
6. set `part4_reserved_bits` to `00`;
7. set `part3_reserved_octet` to `0x00`;
8. set `part4_reserved_octet` to `0x00`;
9. encode the current or specified Unix epoch millisecond timestamp in `unix_ts_ms`;
10. populate `rand_a` and `rand_b` according to Section 7.

A generator SHOULD NOT generate more than one UUID with the same `unix_ts_ms`, `rand_a`, and `rand_b` tuple.

## 9. Parsing Requirements

A parser for this format MUST first validate that the UUID is structurally compatible with UUIDv8-FID-v2.

A parser for this format MUST verify:

```text
format_id == 0x10
format_type == 0x1
format_subtype == 0x0
```

A parser MAY extract `unix_ts_ms`, `rand_a`, and `rand_b` after structural validation succeeds.

## 10. Validation Requirements

A value conforms to this format when:

```text
variant == 0b10
version == 0x8
part4_reserved_bits == 0b00
format_type == 0x1
format_subtype == 0x0
format_id == 0x10
part3_reserved_octet == 0x00
part4_reserved_octet == 0x00
```

## 11. Uniqueness Assumptions

This format does not by itself guarantee global uniqueness.

Uniqueness depends on the timestamp source, the quality of the random or pseudorandom generation of `rand_a` and `rand_b`, and any profile-specific interpretation of those fields.

## 12. Security and Privacy Considerations

This format reveals a 48-bit Unix epoch millisecond timestamp.

UUID values generated with this format SHOULD NOT be assumed to be unpredictable unless `rand_a` and `rand_b` are generated with sufficient entropy for the application’s threat model.

If `rand_a` or `rand_b` contains node identifiers, dataset identifiers, counters, hashes, or namespace-derived values, the profile-specific specification MUST document the associated privacy and predictability implications.

## 13. Test Vectors

The following test vectors are deterministic examples for construction and parsing.

These vectors are not recommendations for random-number generation. In particular, all-zero or all-one random fields are included only as boundary examples.

### 13.1 Unix Epoch Boundary

Input fields:

```text
rand_a      = 0x00000000
rand_b      = 0x0000
unix_ts_ms  = 0x000000000000
```

Expected UUID:

```text
00000000-0000-8100-8000-000000000000
```

Extracted fields:

```text
format_type    = 0x1
format_subtype = 0x0
format_id      = 0x10
unix_ts_ms     = 0x000000000000
```

### 13.2 Fixed Timestamp and Random Payload

Input fields:

```text
rand_a      = 0x12345678
rand_b      = 0x9abc
unix_ts_ms  = 0x01856aa0c800
```

The timestamp value `0x01856aa0c800` is decimal `1672531200000`, corresponding to `2023-01-01T00:00:00Z`.

Expected UUID:

```text
12345678-9abc-8100-8000-01856aa0c800
```

Extracted fields:

```text
format_type    = 0x1
format_subtype = 0x0
format_id      = 0x10
unix_ts_ms     = 0x01856aa0c800
```

### 13.3 Maximum Field Boundary

Input fields:

```text
rand_a      = 0xffffffff
rand_b      = 0xffff
unix_ts_ms  = 0xffffffffffff
```

Expected UUID:

```text
ffffffff-ffff-8100-8000-ffffffffffff
```

Extracted fields:

```text
format_type    = 0x1
format_subtype = 0x0
format_id      = 0x10
unix_ts_ms     = 0xffffffffffff
```

## 14. Registry Entry

| format_type | format_subtype | format_id | Name | Status | Reference | Notes |
|---|---|---|---|---|---|---|
| `0x1` | `0x0` | `0x10` | `time48-rand` | assigned | This document | Part 5 contains a 48-bit Unix epoch millisecond timestamp; Part 1 and Part 2 contain 48 bits of random or profile-defined payload. |
