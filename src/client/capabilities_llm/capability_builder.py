import pandas as pd
import json
from pathlib import Path
from client.capabilities_llm.type import LLMCapabilities, LLMEndpointCapability
from client.client import BrapiClient

class LLMCapabilityBuilder:
    @classmethod
    def from_server(cls, client: BrapiClient, server_name: str) -> LLMCapabilities:
        serverinfo = client.fetch_serverinfo()
        result = serverinfo.get('result', {})
        calls = result.get('calls', []) or []
        
        # Read metadata
        metadata_path = Path(__file__).parent.parent / 'data' / 'metadata.csv'
        metadata = pd.read_csv(metadata_path)
        
        caps = LLMCapabilities(server_name=server_name)
        
        for call in calls:
            path = call.get('service')
            if not path:
                continue
                
            methods = set(call.get('methods') or [])
            data_types = call.get('dataTypes') or []
            
            # Find in metadata
            row = metadata.loc[metadata['service'] == path]
            if row.empty:
                continue
                
            row = row.iloc[0]
            tool_type = row.get('tool')
            is_sub_service = bool(row.get('is_sub_service', False))
            description = row.get('description')
            dictionary_loc = row.get('dictionary_loc')
            
            input_schema = None
            if pd.notna(dictionary_loc):
                try:
                    # dictionary_loc might be a string representation of a dict or just a string
                    # If it's a string that looks like json/dict, parse it? 
                    # The original code just passed it through. 
                    # But here we want to be careful.
                    # Let's assume it's a string or dict.
                    input_schema = dictionary_loc
                except:
                    pass

            ep = LLMEndpointCapability(
                path=path,
                methods=methods,
                data_types=data_types,
                module=row.get('category', '').lower() if pd.notna(row.get('category')) else None,
                description=description if pd.notna(description) else None,
                input_schema=input_schema,
                is_sub_service=is_sub_service,
                tool_type=tool_type
            )
            
            if tool_type == 'get':
                caps.get[path] = ep
            elif tool_type == 'search':
                caps.search[path] = ep
            elif tool_type == 'image':
                caps.images[path] = ep
                
        return caps
