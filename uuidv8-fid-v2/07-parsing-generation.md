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
