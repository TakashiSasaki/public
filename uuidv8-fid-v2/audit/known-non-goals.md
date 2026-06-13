# UUIDv8-FID-v2 Known Non-Goals

This document records intentional non-goals for the current version of the specification to guide future reviews.

## 1. No new Format ID assignment in this stride

- Do not assign `0x11`.
- Do not assign `0x7a`.
- Do not allocate additional `format_type` families.

## 2. No change to UUID core semantics

- Do not redefine UUID version or variant.
- Do not change canonical UUID string representation.
- Do not change the five standard UUID parts.

## 3. No use of reserved fields for application payload

- Do not use `part4_reserved_bits` for application data.
- Do not use `part3_reserved_octet` for application data.
- Do not use `part4_reserved_octet` for application data.

## 4. No uniqueness guarantee beyond format-specific assumptions

- UUIDv8-FID-v2 itself does not guarantee global uniqueness.
- `time48-rand` uniqueness depends on timestamp source, random/pseudorandom quality, and any profile-specific interpretation of `rand_a` and `rand_b`.

## 5. No requirement for a particular implementation language

- Implementation guidance remains language-neutral.
- Conformance vectors should be usable by multiple implementations.
