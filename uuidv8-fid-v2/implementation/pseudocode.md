# UUIDv8-FID-v2 Implementation Pseudocode

This pseudocode is derived from existing normative rules in the main specification, registry, and format-specific documents. It does not redefine the specification and does not introduce new normative requirements.

## 1. Extract UUIDv8-FID-v2 Fields

```text
function extract_uuidv8_fid_v2_fields(uuid_bytes):
    octet6 = uuid_bytes[6]
    octet7 = uuid_bytes[7]
    octet8 = uuid_bytes[8]
    octet9 = uuid_bytes[9]

    version               = (octet6 >> 4) & 0x0f
    format_id_hi4         =  octet6       & 0x0f
    format_type           =  format_id_hi4

    variant               = (octet8 >> 6) & 0x03
    part4_reserved_bits   = (octet8 >> 4) & 0x03
    format_id_lo4         =  octet8       & 0x0f
    format_subtype        =  format_id_lo4

    part3_reserved_octet  = octet7
    part4_reserved_octet  = octet9

    format_id             = (format_type << 4) | format_subtype

    return {
        version,
        format_id_hi4,
        format_type,
        variant,
        part4_reserved_bits,
        format_id_lo4,
        format_subtype,
        part3_reserved_octet,
        part4_reserved_octet,
        format_id
    }
```

## 2. Classify Format ID

```text
function classify_format_id(format_id):
    if format_id >= 0x00 and format_id <= 0x0f:
        return "reserved"
    else if format_id == 0x10:
        return "assigned"
    else if format_id >= 0x11 and format_id <= 0xef:
        return "unassigned"
    else if format_id >= 0xf0 and format_id <= 0xff:
        return "reserved"
    else:
        return "unknown"
```

## 3. Validate Basic UUIDv8

```text
function validate_basic_uuidv8(fields):
    if fields.variant == 0b10 and fields.version == 0x8:
        return "pass"
    else:
        return "fail"
```

## 4. Validate UUIDv8-FID-v2 Structural

```text
function validate_uuidv8_fid_v2_structural(fields):
    if fields.variant == 0b10 and fields.version == 0x8 and fields.part4_reserved_bits == 0b00:
        return "pass"
    else:
        return "fail"
```

## 5. Validate Profile

```text
function validate_profile(fields, implementation_supported_format_ids):
    if validate_uuidv8_fid_v2_structural(fields) != "pass":
        return "fail"

    if fields.format_id not in implementation_supported_format_ids:
        return "fail"

    status = classify_format_id(fields.format_id)
    if status != "assigned" and status != "deprecated":
        return "fail"

    return "pass"
```

## 6. Validate Strict

```text
function validate_strict(fields, implementation_supported_format_ids):
    if validate_profile(fields, implementation_supported_format_ids) != "pass":
        return "fail"

    if fields.part3_reserved_octet != 0x00 or fields.part4_reserved_octet != 0x00:
        return "fail"

    return "pass"
```

## 7. Construct UUIDv8-FID-v2

```text
function construct_uuidv8_fid_v2(format_id, part1, part2, part5):
    status = classify_format_id(format_id)

    if status == "reserved":
        fail("Reserved Format IDs cannot be constructed.")

    if status == "unassigned":
        // Explicitly reject unassigned Format IDs unless constructing non-interoperable test fixtures.
        fail("Unassigned Format IDs cannot be constructed for interoperable use.")

    if status == "unknown":
        fail("Unknown Format IDs cannot be constructed.")

    if status == "deprecated":
        fail("Deprecated Format IDs cannot be constructed unless explicitly accepted for compatibility.")

    format_type    = (format_id >> 4) & 0x0f
    format_subtype =  format_id       & 0x0f

    part3_control_octet  = 0x80 | format_type
    part3_reserved_octet = 0x00
    part4_control_octet  = 0x80 | format_subtype
    part4_reserved_octet = 0x00

    uuid_bytes = allocate(16)

    // Part 1 (32 bits)
    uuid_bytes[0..3] = part1

    // Part 2 (16 bits)
    uuid_bytes[4..5] = part2

    // Part 3 (16 bits)
    uuid_bytes[6] = part3_control_octet
    uuid_bytes[7] = part3_reserved_octet

    // Part 4 (16 bits)
    uuid_bytes[8] = part4_control_octet
    uuid_bytes[9] = part4_reserved_octet

    // Part 5 (48 bits)
    uuid_bytes[10..15] = part5

    return uuid_bytes
```

## 8. Construct time48-rand

```text
function construct_time48_rand(rand_a, rand_b, unix_ts_ms):
    format_id = 0x10

    if length(rand_a) > 32 bits:
        fail("rand_a must fit in 32 bits.")

    if length(rand_b) > 16 bits:
        fail("rand_b must fit in 16 bits.")

    if length(unix_ts_ms) > 48 bits:
        fail("unix_ts_ms must fit in 48 bits.")

    // Encode unix_ts_ms in network byte order in Part 5
    part5 = to_network_byte_order(unix_ts_ms, 48 bits)

    // Center form explicitly set by construct_uuidv8_fid_v2: 8100-8000
    return construct_uuidv8_fid_v2(format_id, rand_a, rand_b, part5)
```

## 9. Parse time48-rand

```text
function parse_time48_rand(uuid_bytes):
    fields = extract_uuidv8_fid_v2_fields(uuid_bytes)

    if validate_uuidv8_fid_v2_structural(fields) != "pass":
        fail("UUID is not structurally compatible with UUIDv8-FID-v2.")

    if fields.format_id != 0x10:
        fail("Invalid format_id for time48-rand.")

    if fields.format_type != 0x1:
        fail("Invalid format_type for time48-rand.")

    if fields.format_subtype != 0x0:
        fail("Invalid format_subtype for time48-rand.")

    if fields.part3_reserved_octet != 0x00:
        fail("part3_reserved_octet must be 0x00.")

    if fields.part4_reserved_octet != 0x00:
        fail("part4_reserved_octet must be 0x00.")

    rand_a     = uuid_bytes[0..3]
    rand_b     = uuid_bytes[4..5]
    unix_ts_ms = from_network_byte_order(uuid_bytes[10..15])

    return {
        rand_a,
        rand_b,
        unix_ts_ms
    }
```
