# Format-ID UUIDv8 Profile Version 2 (UUIDv8-FID-v2) Specification

## 1. Status of This Document

This document defines Version 2 of the **Format-ID UUIDv8 Profile**, abbreviated as **UUIDv8-FID-v2**.

UUIDv8-FID-v2 is an application-defined UUID version 8 profile. It preserves the standard UUID version and variant fields and defines an 8-bit Format ID for identifying application-defined UUIDv8 payload formats.

UUIDv8-FID-v2 is intended for developers implementing UUID generation, parsing, validation, serialization, deserialization, indexing, and library-level interoperability.

This document defines only the field format and bit-level structure of UUIDv8-FID-v2. It does not assign concrete Format ID values.

## 2. Scope

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

This specification does not define:

* the semantics of individual `format_type` values;
* the semantics of individual `format_subtype` values;
* the semantics of individual `format_id` values;
* a registry policy for assigning Format ID values;
* the payload layout of Part 1, Part 2, or Part 5;
* timestamp semantics;
* uniqueness guarantees for any particular Format ID;
* privacy or security properties of any concrete assigned format.

Those items are expected to be defined by a separate UUIDv8-FID-v2 registry or by profile-specific documents.

## 3. Terminology

The key words `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` are to be interpreted as normative requirements.

The following terms are used in this document.

`UUIDv8-FID-v2`
: The Format-ID UUIDv8 Profile Version 2 defined by this document.

`format_id`
: An 8-bit logical identifier composed of `format_type` and `format_subtype`.

`format_type`
: The upper 4 bits of `format_id`. This field identifies a broad payload family. This document defines the field and its location but does not assign concrete values.

`format_subtype`
: The lower 4 bits of `format_id`. This field identifies a concrete payload layout within a `format_type` family. This document defines the field and its location but does not assign concrete values.

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

## 4. UUID String Representation

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

## 5. Bit Numbering

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

## 6. Overall Layout

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

## 7. Part 3 Layout

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

## 8. Part 4 Layout

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

## 9. The Format ID Fields

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

This document does not assign meanings to any `format_type`, `format_subtype`, or `format_id` value.

## 10. Parsing Algorithm

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

## 11. Generation Algorithm

A generator for UUIDv8-FID-v2 SHOULD perform the following steps.

1. Select a `format_type` in the range `0x0..0xf`.
2. Select a `format_subtype` in the range `0x0..0xf`.
3. Compute:

```text
format_id = (format_type << 4) | format_subtype
```

4. Set the UUID version field to `1000`.
5. Set the UUID variant field to `10`.
6. Set `part4_reserved_bits` to `00`.
7. Store `format_type` in bits 52 through 55.
8. Store `format_subtype` in bits 68 through 71.
9. Set `part3_reserved_octet` to `0x00`.
10. Set `part4_reserved_octet` to `0x00`.
11. Populate Part 1, Part 2, and Part 5 according to the registry or profile-specific definition associated with the selected Format ID.

A generator MUST NOT use `part4_reserved_bits`, `part3_reserved_octet`, or `part4_reserved_octet` for application data in this version of the specification.

## 12. Extraction Formulas

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

## 13. Construction Formulas

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

## 14. Validation Levels

Implementations MAY support multiple validation levels.

### 14.1 Basic UUIDv8 Validation

Basic validation checks only:

```text
variant == 0b10
version == 0x8
```

This level determines whether the UUID is structurally compatible with UUID version 8.

### 14.2 UUIDv8-FID-v2 Structural Validation

UUIDv8-FID-v2 structural validation checks:

```text
variant == 0b10
version == 0x8
part4_reserved_bits == 0b00
```

This level determines whether the UUID is structurally compatible with UUIDv8-FID-v2 extraction.

### 14.3 Profile Validation

Profile validation checks:

```text
variant == 0b10
version == 0x8
part4_reserved_bits == 0b00
format_type and format_subtype are known to the implementation
```

This level determines whether the implementation knows how to interpret the UUID payload.

### 14.4 Strict Validation

Strict validation checks:

```text
variant == 0b10
version == 0x8
part4_reserved_bits == 0b00
format_type and format_subtype are known to the implementation
part3_reserved_octet == 0x00
part4_reserved_octet == 0x00
```

This level determines whether the UUID conforms exactly to this version of UUIDv8-FID-v2 and to a known assigned profile.

## 15. Relationship to UUIDv8-FID Version 1

UUIDv8-FID-v2 supersedes UUIDv8-FID Version 1.

UUIDv8-FID Version 1 defined a 10-bit logical `format_id` split into `format_id_hi4` and `format_id_lo6`.

UUIDv8-FID-v2 replaces that field with an 8-bit logical `format_id` composed of `format_type` and `format_subtype`, physically stored as `format_id_hi4` and `format_id_lo4`, and reserves bits 66 through 67.

UUIDv8-FID Version 1 and UUIDv8-FID-v2 are not self-distinguishing from the UUID bit pattern alone. Implementations MUST know which profile version they implement. New implementations SHOULD implement UUIDv8-FID-v2.

## 16. Compatibility Considerations

UUIDv8-FID-v2 values are valid UUID version 8 values when the standard UUID version and variant fields are interpreted according to the UUID specification.

Systems that only check UUID syntax, version, and variant should treat UUIDv8-FID-v2 values as UUIDv8 values.

Systems that require semantic interpretation of the UUID payload need UUIDv8-FID-v2-specific support and a registry or profile-specific definition for the extracted `format_type` and `format_subtype`.

UUIDv8-FID-v2 does not provide compatibility with UUIDv1, UUIDv5, UUIDv7, or UUIDv8-FID Version 1 semantics. A system containing UUIDv1, UUIDv5, UUIDv7, UUIDv8-FID Version 1, and UUIDv8-FID-v2 values SHOULD inspect the UUID version field and use profile-specific parsing rules where applicable.

## 17. Security Considerations

UUIDv8-FID-v2 by itself does not define randomness, timestamp placement, node identifiers, cryptographic hashes, namespace-derived identifiers, counters, or dataset identifiers.

Security and privacy properties depend on the registry or profile-specific definition associated with each `format_type` and `format_subtype` pair.

A format-specific definition SHOULD state whether generated UUIDs reveal timestamps, node identifiers, dataset identifiers, counters, hashes, or other potentially sensitive information.

A format-specific definition SHOULD state whether UUID values are intended to be unpredictable.

## 18. Example: Extracting the Format ID

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

A generated UUIDv8-FID-v2 value with this Format ID has the following center form:

```text
xxxxxxxx-xxxx-8700-8a00-xxxxxxxxxxxx
```

## 19. Summary

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
