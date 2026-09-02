from src.csv_parser import parse_csv_header

def test_utf8_bom_header():
    bom_data = b"\xef\xbb\xbfid,name,email"
    headers = parse_csv_header(bom_data)
    assert headers[0] == "id"
