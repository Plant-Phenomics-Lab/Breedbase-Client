from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional

@dataclass
class LLMEndpointCapability:
    path: str
    methods: Set[str]
    data_types: List[str]
    module: Optional[str] = None
    description: Optional[str] = None
    input_schema: Dict = None
    is_sub_service: bool = False
    tool_type: Optional[str] = None

@dataclass
class LLMCapabilities:
    server_name: str = ""
    get: Dict[str, LLMEndpointCapability] = field(default_factory=dict)
    search: Dict[str, LLMEndpointCapability] = field(default_factory=dict)
    images: Dict[str, LLMEndpointCapability] = field(default_factory=dict)
