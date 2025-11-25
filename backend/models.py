from typing import List, Dict, Optional

from pydantic import BaseModel


class TestCase(BaseModel):
    test_id: str
    feature: str
    scenario: str
    preconditions: List[str]
    steps: List[str]
    test_data: Dict[str, str]
    expected_result: str
    grounded_in: List[str]


class TestCaseQuery(BaseModel):
    query: str


class SeleniumRequest(BaseModel):
    test_id: str


class BuildKBStatus(BaseModel):
    success: bool
    message: str
