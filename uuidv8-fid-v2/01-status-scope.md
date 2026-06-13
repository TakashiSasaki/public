# 1. Status of This Document

This document defines Version 2 of the **Format-ID UUIDv8 Profile**, abbreviated as **UUIDv8-FID-v2**.

UUIDv8-FID-v2 is an application-defined UUID version 8 profile. It preserves the standard UUID version and variant fields and defines an 8-bit Format ID for identifying application-defined UUIDv8 payload formats.

UUIDv8-FID-v2 is intended for developers implementing UUID generation, parsing, validation, serialization, deserialization, indexing, and library-level interoperability.

This document defines the field format, bit-level structure, and initial Format ID registry for UUIDv8-FID-v2. It does not assign any concrete payload format.

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

The registry chapter defines assignment status and assignment policy for Format ID values. This initial version does not assign any concrete payload format.

Concrete payload layouts and format-specific semantics are still defined by profile-specific documents.
