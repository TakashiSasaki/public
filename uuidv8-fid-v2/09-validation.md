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
