# UUIDv8-FID-v2 Format 0x10: time48-rand

This document defines the UUIDv8-FID-v2 payload format assigned to `format_id = 0x10`.

## 1. Status

Status: Assigned.

This format is assigned by the UUIDv8-FID-v2 registry.

## 2. Format ID

```text
format_type    = 0x1
format_subtype = 0x0
format_id      = 0x10
```

## 3. Name

time48-rand

## 4. Payload Layout

The UUIDv8-FID-v2 control fields are defined by the main specification and MUST NOT be redefined by this format.

This format defines the payload fields as follows:

```text
bits    field

0..31    rand_a
32..47   rand_b

48..51   version = 1000
52..55   format_id_hi4 = format_type = 0x1
56..63   part3_reserved_octet = 0x00

64..65   variant = 10
66..67   part4_reserved_bits = 00
68..71   format_id_lo4 = format_subtype = 0x0
72..79   part4_reserved_octet = 0x00

80..127  unix_ts_ms
```

The canonical center form of generated values for this format is:

`xxxxxxxx-xxxx-8100-8000-xxxxxxxxxxxx`

## 5. Byte Order and Integer Interpretation

`unix_ts_ms` is a 48-bit unsigned integer encoded in network byte order.

`rand_a` and `rand_b` are interpreted as opaque bit strings unless a profile-specific specification defines a stricter interpretation.

## 6. Timestamp Semantics

`unix_ts_ms` is the number of milliseconds elapsed since the Unix epoch:

`1970-01-01T00:00:00Z`

The timestamp unit is milliseconds.

The timestamp field has width 48 bits.

This timestamp placement is intentionally compatible with the 48-bit Unix epoch millisecond timestamp used by UUID version 7, but it is placed in Part 5 rather than in Part 1 and Part 2.

## 7. Randomness, Counter, Node, Dataset, Hash, or Namespace Fields

`rand_a` and `rand_b` together provide 48 payload bits outside the UUIDv8-FID-v2 control fields and timestamp field.

Generators SHOULD fill `rand_a` and `rand_b` with cryptographically strong random or pseudorandom bits unless a profile-specific specification defines a counter, node identifier, dataset identifier, hash, namespace-derived value, or other structured interpretation.

If a structured interpretation is used for `rand_a` or `rand_b`, that interpretation MUST be documented by the profile-specific specification.

## 8. Generation Requirements

A generator for this format MUST:

1. use `format_id = 0x10`;
2. set `format_type = 0x1`;
3. set `format_subtype = 0x0`;
4. set the UUID version field to `1000`;
5. set the UUID variant field to `10`;
6. set `part4_reserved_bits` to `00`;
7. set `part3_reserved_octet` to `0x00`;
8. set `part4_reserved_octet` to `0x00`;
9. encode the current or specified Unix epoch millisecond timestamp in `unix_ts_ms`;
10. populate `rand_a` and `rand_b` according to Section 7.

A generator SHOULD NOT generate more than one UUID with the same `unix_ts_ms`, `rand_a`, and `rand_b` tuple.

## 9. Parsing Requirements

A parser for this format MUST first validate that the UUID is structurally compatible with UUIDv8-FID-v2.

A parser for this format MUST verify:

```text
format_id == 0x10
format_type == 0x1
format_subtype == 0x0
```

A parser MAY extract `unix_ts_ms`, `rand_a`, and `rand_b` after structural validation succeeds.

## 10. Validation Requirements

A value conforms to this format when:

```text
variant == 0b10
version == 0x8
part4_reserved_bits == 0b00
format_type == 0x1
format_subtype == 0x0
format_id == 0x10
part3_reserved_octet == 0x00
part4_reserved_octet == 0x00
```

## 11. Uniqueness Assumptions

This format does not by itself guarantee global uniqueness.

Uniqueness depends on the timestamp source, the quality of the random or pseudorandom generation of `rand_a` and `rand_b`, and any profile-specific interpretation of those fields.

## 12. Security and Privacy Considerations

This format reveals a 48-bit Unix epoch millisecond timestamp.

UUID values generated with this format SHOULD NOT be assumed to be unpredictable unless `rand_a` and `rand_b` are generated with sufficient entropy for the application’s threat model.

If `rand_a` or `rand_b` contains node identifiers, dataset identifiers, counters, hashes, or namespace-derived values, the profile-specific specification MUST document the associated privacy and predictability implications.

## 13. Test Vectors

TBD.

## 14. Registry Entry

| format_type | format_subtype | format_id | Name | Status | Reference | Notes |
|---|---|---|---|---|---|---|
| `0x1` | `0x0` | `0x10` | `time48-rand` | assigned | This document | Part 5 contains a 48-bit Unix epoch millisecond timestamp; Part 1 and Part 2 contain 48 bits of random or profile-defined payload. |
