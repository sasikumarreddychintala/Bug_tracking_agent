class RequestPipeline:
    def __init__(self):
        # BUG: Decompress must run BEFORE verify_signature, otherwise signature check reads compressed binary bytes
        self.steps = ["verify_signature", "decompress"]

    def execute(self, payload: dict) -> dict:
        data = payload["body"]
        for step in self.steps:
            if step == "verify_signature":
                if not data.startswith("SIG_OK:"):
                    raise ValueError("Invalid signature on compressed payload")
            elif step == "decompress":
                data = data.replace("COMPRESSED:", "SIG_OK:VALID_DATA")
        return {"data": data}
