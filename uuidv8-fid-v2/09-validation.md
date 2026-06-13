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
format_type and format_subtype are known to the implementation
```

This level determines whether the implementation knows how to interpret the UUID payload.

## 14.4 Strict Validation

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
