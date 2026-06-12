# Format-ID UUIDv8 Profile (UUIDv8-FID) Specification, Version 1

## 1. Status of This Document

This document defines the first version of the **Format-ID UUIDv8 Profile**, abbreviated as **UUIDv8-FID**.

UUIDv8-FID is an application-defined UUID version 8 profile. It preserves the standard UUID version and variant fields and introduces a 10-bit logical field named `format_id` for identifying application-defined UUIDv8 formats.

This specification is intended for developers implementing UUID generation, parsing, validation, serialization, deserialization, indexing, and library-level interoperability.

## 2. Scope

UUIDv8-FID defines the bit-level structure of a subset of UUID version 8 values.

This specification defines:

* the placement of the UUID `version` field;
* the placement of the UUID `variant` field;
* a 10-bit logical `format_id` field;
* two reserved octets named `part3_reserved_octet` and `part4_reserved_octet`;
* the relationship between the logical `format_id` and its physical bit fragments.

This specification does not define:

* the semantics of individual `format_id` values;
* the payload layout of Part 1, Part 2, or Part 5;
* timestamp semantics;
* uniqueness guarantees for any particular `format_id`;
* registry policy for assigning `format_id` values.

Those items are expected to be defined by later profile-specific documents or implementation-specific conventions.

## 3. Terminology

The key words `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` are to be interpreted as normative requirements.

The following terms are used in this document.

`UUIDv8-FID`
: The Format-ID UUIDv8 Profile defined by this document.

`format_id`
: A 10-bit logical identifier that identifies an application-defined UUIDv8 format.

`format_id_hi4`
: The upper 4 bits of `format_id`.

`format_id_lo6`
: The lower 6 bits of `format_id`.

`part3_control_octet`
: The octet containing the UUID version field and `format_id_hi4`.

`part3_reserved_octet`
: The low-order octet of Part 3. This octet is reserved for future definition.

`part4_control_octet`
: The octet containing the UUID variant field and `format_id_lo6`.

`part4_reserved_octet`
: The low-order octet of Part 4. This octet is reserved for future definition.

`Part 1` through `Part 5`
: The five hexadecimal groups in the canonical UUID string representation:

```text
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Part1    Part2 Part3 Part4 Part5
```

## 4. UUID String Representation

UUIDv8-FID uses the standard canonical UUID textual representation:

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

UUIDv8-FID does not change the canonical UUID string length, hyphen positions, or hexadecimal encoding.

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

UUIDv8-FID has the following bit layout:

```text
bits    field

0..31   part1
32..47  part2

48..51  version = 1000
52..55  format_id_hi4
56..63  part3_reserved_octet

64..65  variant = 10
66..71  format_id_lo6
72..79  part4_reserved_octet

80..127 part5
```

In canonical UUID string form, the structure can be shown schematically as:

```text
xxxxxxxx-xxxx-8Frr-VFrr-xxxxxxxxxxxx
```

where:

```text
8     is the UUID version nibble for UUID version 8
F     in Part 3 is format_id_hi4
rr    in Part 3 is part3_reserved_octet
V     is a hexadecimal digit whose two most significant bits encode the UUID variant
F     in Part 4 contributes to format_id_lo6
rr    in Part 4 is part4_reserved_octet
```

The schematic notation above is explanatory. The actual value of the first hexadecimal digit of Part 4 depends on both the UUID variant bits and the upper two bits of `format_id_lo6`.

## 7. Part 3 Layout

Part 3 is 16 bits wide and occupies bits 48 through 63.

```text
bits 48..51  version
bits 52..55  format_id_hi4
bits 56..63  part3_reserved_octet
```

The first octet of Part 3 is named `part3_control_octet`.

```text
part3_control_octet = bits 48..55
```

It is composed as follows:

```text
bits 48..51  version = 1000
bits 52..55  format_id_hi4
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
bits 66..71  format_id_lo6
bits 72..79  part4_reserved_octet
```

The first octet of Part 4 is named `part4_control_octet`.

```text
part4_control_octet = bits 64..71
```

It is composed as follows:

```text
bits 64..65  variant = 10
bits 66..71  format_id_lo6
```

The UUID variant field MUST be `10`.

The low-order octet of Part 4 is named `part4_reserved_octet`.

```text
part4_reserved_octet = bits 72..79
```

Generators conforming to this version of the specification MUST set `part4_reserved_octet` to `0x00`.

Parsers conforming to this version of the specification SHOULD ignore `part4_reserved_octet` unless a stricter validation mode is explicitly requested.

## 9. The `format_id` Field

`format_id` is a single 10-bit logical field.

It is physically split across Part 3 and Part 4 because the standard UUID `version` and `variant` fields occupy fixed positions.

```text
format_id_hi4 = bits 52..55
format_id_lo6 = bits 66..71
```

The numeric value of `format_id` is computed as:

```text
format_id = (format_id_hi4 << 6) | format_id_lo6
```

The valid range of `format_id` is:

```text
0x000..0x3ff
```

or equivalently:

```text
0..1023
```

`format_id_hi4` and `format_id_lo6` MUST NOT be interpreted as independent semantic fields unless a later specification explicitly defines such interpretation.

In this version of the specification, `format_id` is a flat 10-bit identifier. Its values are not subdivided into mode, type, class, family, or subtype fields.

## 10. Parsing Algorithm

A parser for UUIDv8-FID SHOULD perform the following steps.

1. Parse the input as a UUID using the standard UUID textual or binary representation.
2. Verify that the UUID variant field is `10`.
3. Verify that the UUID version field is `1000`.
4. Extract `format_id_hi4` from bits 52 through 55.
5. Extract `format_id_lo6` from bits 66 through 71.
6. Compute `format_id` as `(format_id_hi4 << 6) | format_id_lo6`.
7. Extract `part3_reserved_octet` from bits 56 through 63.
8. Extract `part4_reserved_octet` from bits 72 through 79.
9. Interpret the remaining fields according to the specification associated with the extracted `format_id`.

A parser MAY reject UUIDs whose `part3_reserved_octet` or `part4_reserved_octet` is nonzero when operating in strict validation mode.

A parser SHOULD NOT reject such UUIDs by default solely because a reserved octet is nonzero, in order to allow forward-compatible parsing.

## 11. Generation Algorithm

A generator for UUIDv8-FID SHOULD perform the following steps.

1. Select a `format_id` in the range `0x000..0x3ff`.
2. Compute:

```text
format_id_hi4 = (format_id >> 6) & 0x0f
format_id_lo6 = format_id & 0x3f
```

3. Set the UUID version field to `1000`.
4. Set the UUID variant field to `10`.
5. Store `format_id_hi4` in bits 52 through 55.
6. Store `format_id_lo6` in bits 66 through 71.
7. Set `part3_reserved_octet` to `0x00`.
8. Set `part4_reserved_octet` to `0x00`.
9. Populate Part 1, Part 2, and Part 5 according to the format-specific definition associated with `format_id`.

A generator MUST NOT use `part3_reserved_octet` or `part4_reserved_octet` for application data in this version of the specification.

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
part3_control_octet    = octet6
part3_reserved_octet   = octet7
part4_control_octet    = octet8
part4_reserved_octet   = octet9

version                = (octet6 >> 4) & 0x0f
format_id_hi4          =  octet6       & 0x0f

variant                = (octet8 >> 6) & 0x03
format_id_lo6          =  octet8       & 0x3f

format_id              = (format_id_hi4 << 6) | format_id_lo6
```

For UUIDv8-FID:

```text
version MUST be 0x8
variant MUST be 0b10
```

## 13. Construction Formulas

Given a 10-bit `format_id`, the control octets are constructed as follows:

```text
format_id_hi4 = (format_id >> 6) & 0x0f
format_id_lo6 =  format_id       & 0x3f

part3_control_octet = 0x80 | format_id_hi4
part4_control_octet = 0x80 | format_id_lo6
```

The reserved octets are set as follows:

```text
part3_reserved_octet = 0x00
part4_reserved_octet = 0x00
```

The expression `0x80 | format_id_lo6` sets the two most significant bits of `part4_control_octet` to `10`, which is the required UUID variant pattern.

## 14. Validation Levels

Implementations MAY support multiple validation levels.

### 14.1 Basic UUIDv8-FID Validation

Basic validation checks only:

```text
variant == 0b10
version == 0x8
```

This level determines whether the UUID is structurally compatible with UUIDv8-FID extraction.

### 14.2 Profile Validation

Profile validation checks:

```text
variant == 0b10
version == 0x8
format_id is known to the implementation
```

This level determines whether the implementation knows how to interpret the UUID payload.

### 14.3 Strict Validation

Strict validation checks:

```text
variant == 0b10
version == 0x8
format_id is known to the implementation
part3_reserved_octet == 0x00
part4_reserved_octet == 0x00
```

This level determines whether the UUID conforms exactly to this version of UUIDv8-FID.

## 15. `format_id` Assignment Policy

This version of the specification defines the structure of `format_id` but does not define a registry.

Implementations SHOULD treat unknown `format_id` values as opaque UUIDv8-FID values.

Implementations MUST NOT reinterpret unknown `format_id` values using another known format unless explicitly configured to do so.

A future document MAY define a registry of assigned `format_id` values.

## 16. Compatibility Considerations

UUIDv8-FID values are valid UUID version 8 values when the standard UUID version and variant fields are interpreted according to the UUID specification.

Systems that only check UUID syntax, version, and variant should treat UUIDv8-FID values as UUIDv8 values.

Systems that require semantic interpretation of the UUID payload need UUIDv8-FID-specific support.

UUIDv8-FID does not provide compatibility with UUIDv1, UUIDv5, or UUIDv7 semantics. A system containing UUIDv1, UUIDv5, UUIDv7, and UUIDv8-FID values SHOULD inspect the UUID version field before applying version-specific parsing rules.

## 17. Security Considerations

UUIDv8-FID by itself does not define randomness, timestamp placement, node identifiers, cryptographic hashes, or namespace-derived identifiers.

Security and privacy properties depend on the format-specific definition associated with each `format_id`.

A format-specific definition SHOULD state whether generated UUIDs reveal timestamps, node identifiers, dataset identifiers, counters, hashes, or other potentially sensitive information.

A format-specific definition SHOULD state whether UUID values are intended to be unpredictable.

## 18. Example: Extracting `format_id`

Suppose a UUID has the following relevant octets:

```text
octet6 = 0x8a
octet8 = 0x95
```

Then:

```text
version       = 0x8
format_id_hi4 = 0x0a

variant       = 0b10
format_id_lo6 = 0x15
```

Therefore:

```text
format_id = (0x0a << 6) | 0x15
          = 0x295
```

The UUID is structurally a UUIDv8-FID value with `format_id = 0x295`, assuming the complete UUID is otherwise syntactically valid.

## 19. Summary

UUIDv8-FID is a UUID version 8 profile that introduces a single 10-bit logical `format_id` field.

The field is split into two physical fragments:

```text
format_id_hi4: bits 52..55
format_id_lo6: bits 66..71
```

The profile also defines two reserved octets:

```text
part3_reserved_octet: bits 56..63
part4_reserved_octet: bits 72..79
```

The core layout is:

```text
bits  48..51   version = 1000
bits  52..55   format_id_hi4
bits  56..63   part3_reserved_octet

bits  64..65   variant = 10
bits  66..71   format_id_lo6
bits  72..79   part4_reserved_octet
```

The logical field is reconstructed as:

```text
format_id = (format_id_hi4 << 6) | format_id_lo6
```
