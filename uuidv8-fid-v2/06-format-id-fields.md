# 9. The Format ID Fields

UUIDv8-FID-v2 defines an 8-bit logical field named `format_id`.

The Format ID is composed of two semantic nibbles:

```text
format_type    = bits 52..55
format_subtype = bits 68..71
```

The same physical fields are named:

```text
format_id_hi4 = bits 52..55
format_id_lo4 = bits 68..71
```

The semantic mapping is:

```text
format_type    = format_id_hi4
format_subtype = format_id_lo4
```

The numeric value of `format_id` is computed as:

```text
format_id = (format_type << 4) | format_subtype
```

An implementation MAY inspect `format_type` alone for coarse dispatch, classification, filtering, indexing policy, or privacy policy, if such behavior is defined by a registry or profile-specific document.

An implementation MUST NOT fully parse or generate a UUIDv8-FID-v2 payload based only on `format_type` unless the corresponding `format_type` specification explicitly defines a single layout for all of its subtypes.

This document does not assign meanings to any `format_type`, `format_subtype`, or `format_id` value.
