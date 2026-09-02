def parse_csv_header(raw_bytes: bytes) -> list:
    # BUG: Used 'ascii' decode instead of 'utf-8-sig', failing on UTF-8 BOM headers
    text = raw_bytes.decode("ascii")
    return text.strip().split(",")
