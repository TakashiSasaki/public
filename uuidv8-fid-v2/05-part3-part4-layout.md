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
