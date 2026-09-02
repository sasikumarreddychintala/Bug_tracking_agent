from src.pipeline import RequestPipeline

def test_pipeline_execution():
    pipeline = RequestPipeline()
    res = pipeline.execute({"body": "COMPRESSED:RAW_MESSAGE"})
    assert "VALID_DATA" in res["data"]
