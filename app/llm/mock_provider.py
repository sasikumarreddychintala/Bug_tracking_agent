import re
import logging
from typing import Type, TypeVar, Optional, Any, Dict
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)

class MockProvider(BaseLLMProvider):
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return "Deterministic evidence-based investigation finding."

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        max_retries: int = 2,
    ) -> T:
        model_name = response_model.__name__
        case_id = None
        for cid in [f"BUG-00{i}" for i in range(1, 10)] + ["BUG-010"]:
            if cid in prompt:
                case_id = cid
                break

        data = self._get_mock_data(model_name, case_id, prompt)
        return response_model.model_validate(data)

    def _get_mock_data(self, model_name: str, case_id: Optional[str], prompt: str) -> Dict[str, Any]:
        # Handle pre-configured fixture cases
        if case_id:
            return self._get_fixture_mock_data(model_name, case_id, prompt)
        
        # Dynamic handling for custom external repositories (e.g. py-bugger)
        return self._get_dynamic_repo_data(model_name, prompt)

    def _get_dynamic_repo_data(self, model_name: str, prompt: str) -> Dict[str, Any]:
        # Extract files from prompt
        found_files = re.findall(r'([a-zA-Z0-9_\-/\\]+\.py)', prompt)
        clean_files = [f.replace("\\", "/") for f in found_files if not f.endswith("mock_provider.py") and not f.endswith("test_runner.py")]
        primary_file = clean_files[0] if clean_files else "src/main.py"
        secondary_file = clean_files[1] if len(clean_files) > 1 else primary_file

        # Extract line numbers if present
        lines_match = re.search(r'line (\d+)', prompt)
        crash_line = int(lines_match.group(1)) if lines_match else 10

        if model_name == "BaselineDiagnosis":
            return {
                "case_id": "CUSTOM-CASE",
                "suspected_file": primary_file,
                "suspected_line": crash_line,
                "diagnosis": f"Single-shot inspection suspects exception at {primary_file}:{crash_line}",
                "confidence": 0.45
            }

        elif model_name == "BugUnderstandingOutput":
            return {
                "symptoms": [
                    f"Test failure or unhandled exception observed in {primary_file}",
                    "Processing halted with non-zero exit status",
                    "Unexpected behavior under test scenario"
                ],
                "known_facts": [
                    f"Target repository contains files including {primary_file}",
                    "Test execution triggers defect",
                    "Observable stack trace references code coordinates"
                ],
                "unknowns": [
                    "Whether error originates from caller logic or target function",
                    "Precondition validation status"
                ],
                "entry_points": [
                    primary_file,
                    secondary_file
                ],
                "investigation_questions": [
                    f"What is the caller execution path reaching {primary_file}?",
                    "What inputs violate expected invariants?"
                ]
            }

        elif model_name == "HypothesesOutput":
            return {
                "hypotheses": [
                    {
                        "id": "H1",
                        "statement": f"Missing precondition validation or argument handling in {primary_file} causes downstream failure.",
                        "suspected_locations": [f"{primary_file}:{crash_line}"],
                        "supporting_evidence": ["EV-001", "EV-002"],
                        "contradicting_evidence": [],
                        "missing_evidence": ["Sandboxed reproduction output"],
                        "proposed_experiments": ["pytest"],
                        "confidence": 0.90,
                        "status": "open"
                    },
                    {
                        "id": "H2",
                        "statement": f"Exception at {secondary_file} is a symptom of unexpected argument state.",
                        "suspected_locations": [f"{secondary_file}:1"],
                        "supporting_evidence": ["EV-001"],
                        "contradicting_evidence": ["EV-002"],
                        "missing_evidence": [],
                        "proposed_experiments": ["pytest"],
                        "confidence": 0.35,
                        "status": "open"
                    }
                ]
            }

        elif model_name == "VerificationsOutput":
            return {
                "verifications": [
                    {
                        "hypothesis_id": "H1",
                        "decision": "SUPPORTED",
                        "reasoning": f"Code analysis and sandboxed execution confirm defect mechanism in {primary_file}.",
                        "is_upstream_cause": True,
                        "is_symptom_only": False,
                        "evidence_ids": ["EV-001", "EV-002"],
                        "experiment_ids": ["EXP-1"]
                    },
                    {
                        "hypothesis_id": "H2",
                        "decision": "WEAKENED",
                        "reasoning": "H2 describes a downstream symptom rather than the root cause.",
                        "is_upstream_cause": False,
                        "is_symptom_only": True,
                        "evidence_ids": ["EV-001"],
                        "experiment_ids": ["EXP-1"]
                    }
                ]
            }
        return {}

    def _get_fixture_mock_data(self, model_name: str, case_id: str, prompt: str) -> Dict[str, Any]:
        if model_name == "BaselineDiagnosis":
            symptom_map = {
                "BUG-001": {"file": "src/pricing.py", "line": 4, "desc": "ZeroDivisionError in calculate_unit_price formula."},
                "BUG-002": {"file": "src/user_service.py", "line": 11, "desc": "AssertionError in user role assignment check."},
                "BUG-003": {"file": "src/discount.py", "line": 4, "desc": "Discount calculation returns 0 for tier 0."},
                "BUG-004": {"file": "src/user_profile.py", "line": 6, "desc": "AttributeError on auth_data object in user_profile."},
                "BUG-005": {"file": "src/api_handler.py", "line": 8, "desc": "KeyError thrown during order lookup handler."},
                "BUG-006": {"file": "src/pipeline.py", "line": 11, "desc": "ValueError signature check fails on payload body."},
                "BUG-007": {"file": "src/config_loader.py", "line": 7, "desc": "Server port assertion mismatch."},
                "BUG-008": {"file": "src/csv_parser.py", "line": 4, "desc": "UnicodeDecodeError reading raw CSV bytes."},
                "BUG-009": {"file": "src/gateway.py", "line": 15, "desc": "TimeoutError in gateway retry loop."},
                "BUG-010": {"file": "src/task_worker.py", "line": 10, "desc": "Task status assertion mismatch."}
            }
            entry = symptom_map.get(case_id, {"file": "src/pricing.py", "line": 4, "desc": "Generic exception."})
            return {
                "case_id": case_id,
                "suspected_file": entry["file"],
                "suspected_line": entry["line"],
                "diagnosis": entry["desc"],
                "confidence": 0.45
            }

        elif model_name == "BugUnderstandingOutput":
            entry_map = {
                "BUG-001": "src/cart.py",
                "BUG-002": "src/cache_manager.py",
                "BUG-003": "src/discount.py",
                "BUG-004": "src/auth_service.py",
                "BUG-005": "src/order_processor.py",
                "BUG-006": "src/pipeline.py",
                "BUG-007": "src/config_loader.py",
                "BUG-008": "src/csv_parser.py",
                "BUG-009": "src/gateway.py",
                "BUG-010": "src/task_worker.py"
            }
            return {
                "symptoms": [
                    f"Runtime failure triggered in {case_id}",
                    "Unhandled exception during processing",
                    "Operation halted with error status"
                ],
                "known_facts": [
                    f"Failure reproduced under test scenario for {case_id}",
                    "Stack trace identifies crash site",
                    "Reproduction command triggers the defect"
                ],
                "unknowns": [
                    "Where invalid state was introduced upstream",
                    "Whether input validation was bypassed",
                    "Which callers invoke the affected component"
                ],
                "entry_points": [
                    entry_map.get(case_id, "src/")
                ],
                "investigation_questions": [
                    "What is the full caller path to the exception?",
                    "Is the exception site the upstream cause or symptom?",
                    "What experiment proves the true root cause?"
                ]
            }

        elif model_name == "HypothesesOutput":
            case_hypo_map = {
                "BUG-001": {
                    "h1": ("Missing input validation in cart.py allows quantity=0 to be forwarded to calculate_price().", ["src/cart.py:8-12"], 0.92),
                    "h2": ("The pricing calculation in pricing.py is defective and should handle zero division locally.", ["src/pricing.py:2-5"], 0.35),
                    "h3": ("The test harness in test_cart.py is improperly configured.", ["tests/test_cart.py:1-15"], 0.1)
                },
                "BUG-002": {
                    "h1": ("UserCache.get_default_roles in cache_manager.py returns mutable list reference instead of a copy.", ["src/cache_manager.py:6-8"], 0.90),
                    "h2": ("UserService is improperly constructing user response dictionaries.", ["src/user_service.py:5-10"], 0.30),
                    "h3": ("Test fixture state is bleeding between test runner instances.", ["tests/test_cache.py:1-15"], 0.1)
                },
                "BUG-003": {
                    "h1": ("Boundary comparison condition in discount.py uses <= 0 instead of < 0 for loyalty tier.", ["src/discount.py:3-5"], 0.91),
                    "h2": ("Order processor is applying discount calculations twice.", ["src/order.py:4-6"], 0.28),
                    "h3": ("Floating point precision rounding error in discount formula.", ["src/discount.py:6-9"], 0.15)
                },
                "BUG-004": {
                    "h1": ("verify_token in auth_service.py catches broad Exception and swallows error by returning None.", ["src/auth_service.py:7-9"], 0.93),
                    "h2": ("user_profile.py is failing to handle missing keys in dictionary.", ["src/user_profile.py:4-7"], 0.32),
                    "h3": ("Network timeout between auth service and database.", ["src/auth_service.py:1-4"], 0.10)
                },
                "BUG-005": {
                    "h1": ("OrderProcessor.find_order in order_processor.py performs lookup without casting string ID to integer.", ["src/order_processor.py:6-8"], 0.89),
                    "h2": ("API handler is sending corrupted JSON payload body.", ["src/api_handler.py:4-9"], 0.31),
                    "h3": ("Database table records for orders are unseeded.", ["src/order_processor.py:1-5"], 0.12)
                },
                "BUG-006": {
                    "h1": ("Pipeline execution ordering in pipeline.py verifies signature before decompression step.", ["src/pipeline.py:4-6"], 0.92),
                    "h2": ("Signature verification algorithm is failing on valid signatures.", ["src/pipeline.py:9-12"], 0.30),
                    "h3": ("Decompression utility is corrupting binary stream.", ["src/pipeline.py:12-15"], 0.14)
                },
                "BUG-007": {
                    "h1": ("ServerConfig in config_loader.py prioritizes default environment variable over explicit custom_port argument.", ["src/config_loader.py:6-8"], 0.90),
                    "h2": ("Environment variable parser fails to convert port to integer.", ["src/config_loader.py:5-6"], 0.25),
                    "h3": ("Operating system port binding permission failure.", ["tests/test_config.py:1-10"], 0.10)
                },
                "BUG-008": {
                    "h1": ("parse_csv_header in csv_parser.py decodes with strict ascii instead of utf-8 or utf-8-sig.", ["src/csv_parser.py:3-5"], 0.94),
                    "h2": ("CSV delimiter splitting logic is missing newline stripping.", ["src/csv_parser.py:5-6"], 0.22),
                    "h3": ("File stream buffer is truncating early.", ["src/csv_parser.py:1-3"], 0.10)
                },
                "BUG-009": {
                    "h1": ("ApiGateway retry loop in gateway.py retries 401 unauthorized responses until triggering misleading TimeoutError.", ["src/gateway.py:11-16"], 0.91),
                    "h2": ("AuthClient upstream service is experiencing network latency.", ["src/auth_client.py:2-6"], 0.35),
                    "h3": ("Gateway timeout threshold is configured too low.", ["src/gateway.py:14-16"], 0.20)
                },
                "BUG-010": {
                    "h1": ("TaskWorker.process_task in task_worker.py omits return statement in failure branch, falling through to COMPLETED.", ["src/task_worker.py:8-11"], 0.95),
                    "h2": ("Task worker dictionary is suffering from asynchronous thread corruption.", ["src/task_worker.py:3-5"], 0.25),
                    "h3": ("Status getter method returns stale cached value.", ["src/task_worker.py:12-14"], 0.10)
                }
            }
            spec = case_hypo_map.get(case_id, case_hypo_map["BUG-001"])
            return {
                "hypotheses": [
                    {
                        "id": "H1",
                        "statement": spec["h1"][0],
                        "suspected_locations": spec["h1"][1],
                        "supporting_evidence": ["EV-001", "EV-002"],
                        "contradicting_evidence": [],
                        "missing_evidence": ["Controlled reproduction output"],
                        "proposed_experiments": ["pytest"],
                        "confidence": spec["h1"][2],
                        "status": "open"
                    },
                    {
                        "id": "H2",
                        "statement": spec["h2"][0],
                        "suspected_locations": spec["h2"][1],
                        "supporting_evidence": ["EV-001"],
                        "contradicting_evidence": ["EV-002"],
                        "missing_evidence": [],
                        "proposed_experiments": ["pytest"],
                        "confidence": spec["h2"][2],
                        "status": "open"
                    },
                    {
                        "id": "H3",
                        "statement": spec["h3"][0],
                        "suspected_locations": spec["h3"][1],
                        "supporting_evidence": [],
                        "contradicting_evidence": ["EV-001", "EV-002"],
                        "missing_evidence": [],
                        "proposed_experiments": ["pytest"],
                        "confidence": spec["h3"][2],
                        "status": "open"
                    }
                ]
            }

        elif model_name == "VerificationsOutput":
            return {
                "verifications": [
                    {
                        "hypothesis_id": "H1",
                        "decision": "SUPPORTED",
                        "reasoning": f"Code analysis and sandboxed experiment confirm H1 as the true upstream root cause for {case_id}.",
                        "is_upstream_cause": True,
                        "is_symptom_only": False,
                        "evidence_ids": ["EV-001", "EV-002", "EV-003"],
                        "experiment_ids": ["EXP-1"]
                    },
                    {
                        "hypothesis_id": "H2",
                        "decision": "WEAKENED",
                        "reasoning": f"H2 describes the downstream symptom crash site, not the upstream root cause for {case_id}.",
                        "is_upstream_cause": False,
                        "is_symptom_only": True,
                        "evidence_ids": ["EV-001"],
                        "experiment_ids": ["EXP-1"]
                    },
                    {
                        "hypothesis_id": "H3",
                        "decision": "REJECTED",
                        "reasoning": f"H3 is contradicted by reproduction output and source code inspection for {case_id}.",
                        "is_upstream_cause": False,
                        "is_symptom_only": False,
                        "evidence_ids": ["EV-001", "EV-003"],
                        "experiment_ids": ["EXP-1"]
                    }
                ]
            }
        return {}
