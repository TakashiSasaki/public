# UUIDv8-FID-v2 Implementation Checklist

This checklist provides implementation guidance derived from existing normative rules in the specification.

## 1. Parser Implementation

* [ ] parse standard UUID textual or binary form;
* [ ] extract octets 6, 7, 8, and 9;
* [ ] verify version and variant;
* [ ] compute `format_type`, `format_subtype`, and `format_id`;
* [ ] distinguish structural validation from profile validation;
* [ ] expose unknown or unassigned values as opaque values when appropriate;
* [ ] reject or flag reserved Format IDs according to validation level.

## 2. Generator Implementation

* [ ] only generate assigned Format IDs;
* [ ] do not generate reserved or unassigned Format IDs as interoperable UUIDv8-FID-v2 values;
* [ ] set `version = 1000`;
* [ ] set `variant = 10`;
* [ ] set `part4_reserved_bits = 00`;
* [ ] set `part3_reserved_octet = 0x00`;
* [ ] set `part4_reserved_octet = 0x00`;
* [ ] populate Part 1, Part 2, and Part 5 according to the selected assigned format.

## 3. time48-rand Implementation

* [ ] use `format_id = 0x10`;
* [ ] use center form `8100-8000`;
* [ ] encode `unix_ts_ms` as a 48-bit unsigned Unix epoch millisecond timestamp in network byte order;
* [ ] treat `rand_a` and `rand_b` as opaque unless a profile-specific specification defines stricter interpretation;
* [ ] ensure `rand_a`, `rand_b`, and `unix_ts_ms` fit their field widths;
* [ ] test using the deterministic vectors in `formats/10-time48-rand.md`.

## 4. Validation Testing

* [ ] run the structural conformance vectors in `conformance/structural-test-vectors.md`;
* [ ] run the machine-readable vectors in `conformance/structural-test-vectors.json`;
* [ ] verify boundary behavior for unassigned, reserved, invalid version, invalid variant, invalid `part4_reserved_bits`, and nonzero reserved octets.

## 5. Registry Handling

* [ ] recognize only `0x10` as assigned in the current registry;
* [ ] treat `0x11..0xef` as unassigned;
* [ ] treat `0x00..0x0f` and `0xf0..0xff` as reserved;
* [ ] do not interpret unknown Format IDs as another known format unless explicitly configured.
