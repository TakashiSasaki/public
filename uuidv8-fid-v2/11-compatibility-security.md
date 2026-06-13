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
