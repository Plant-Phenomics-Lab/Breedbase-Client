"""
Unit tests for BrAPIClient._fetch_all_pages

Tests the three response shapes returned by BrAPI:
1. Response with 'data' key: {'data': [...], ...}
2. Response that is already a list: [...]
3. Single resource object: {...}
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add parent directory to path to import client
sys.path.insert(0, str(Path(__file__).parent.parent))

from client import BrAPIClient


@pytest.fixture
def mock_client():
    """Create a mock BrAPIClient for testing"""
    with patch.object(BrAPIClient, 'get_client'), \
         patch.object(BrAPIClient, '_get_valid_endpoints'):
        client = BrAPIClient(
            base_url="https://test.org/brapi/v2",
            username="test_user",
            password="test_pass"
        )
        client.session = Mock()
        return client


def test_fetch_with_data_key_single_page(mock_client):
    """Test response shape: {'data': [...], 'pagination': {...}}"""
    mock_client._make_request = Mock(return_value={
        'result': {
            'data': [
                {'id': '1', 'name': 'Item 1'},
                {'id': '2', 'name': 'Item 2'},
            ],
            'pagination': {
                'currentPage': 0,
                'totalPages': 1
            }
        },
        'metadata': {
            'pagination': {
                'currentPage': 0,
                'totalPages': 1
            }
        }
    })

    result = mock_client._fetch_all_pages('/germplasm')

    assert len(result) == 2
    assert result[0]['id'] == '1'
    assert result[1]['name'] == 'Item 2'
    mock_client._make_request.assert_called_once()


def test_fetch_with_data_key_multiple_pages(mock_client):
    """Test pagination with 'data' key across multiple pages"""
    page_responses = [
        {
            'result': {
                'data': [
                    {'id': '1', 'name': 'Item 1'},
                    {'id': '2', 'name': 'Item 2'},
                ]
            },
            'metadata': {
                'pagination': {
                    'currentPage': 0,
                    'totalPages': 2
                }
            }
        },
        {
            'result': {
                'data': [
                    {'id': '3', 'name': 'Item 3'},
                ]
            },
            'metadata': {
                'pagination': {
                    'currentPage': 1,
                    'totalPages': 2
                }
            }
        }
    ]
    
    mock_client._make_request = Mock(side_effect=page_responses)

    result = mock_client._fetch_all_pages('/germplasm')

    assert len(result) == 3
    assert result[0]['id'] == '1'
    assert result[2]['id'] == '3'
    assert mock_client._make_request.call_count == 2


def test_fetch_with_list_response(mock_client):
    """Test response shape where result is already a list: [...]"""
    mock_client._make_request = Mock(return_value={
        'result': [
            {'id': '1', 'name': 'Item 1'},
            {'id': '2', 'name': 'Item 2'},
        ],
        'metadata': {
            'pagination': {
                'currentPage': 0,
                'totalPages': 1
            }
        }
    })

    result = mock_client._fetch_all_pages('/someservice')

    assert len(result) == 2
    assert result[0]['id'] == '1'
    assert result[1]['id'] == '2'


def test_fetch_with_single_resource_object(mock_client):
    """Test response shape where result is a single dict (resource object)"""
    mock_client._make_request = Mock(return_value={
        'result': {
            'id': '123',
            'name': 'Single Resource',
            'description': 'This is a single object'
        },
        'metadata': {
            'pagination': {
                'currentPage': 0,
                'totalPages': 1
            }
        }
    })

    result = mock_client._fetch_all_pages('/germplasm/123')

    assert len(result) == 1
    assert result[0]['id'] == '123'
    assert result[0]['name'] == 'Single Resource'


def test_fetch_with_empty_data(mock_client):
    """Test response with empty data array"""
    mock_client._make_request = Mock(return_value={
        'result': {
            'data': [],
            'pagination': {
                'currentPage': 0,
                'totalPages': 1
            }
        },
        'metadata': {
            'pagination': {
                'currentPage': 0,
                'totalPages': 1
            }
        }
    })

    result = mock_client._fetch_all_pages('/germplasm')

    assert len(result) == 0
    assert result == []


def test_fetch_with_max_pages_limit(mock_client):
    """Test that max_pages parameter limits fetching"""
    page_responses = [
        {
            'result': {'data': [{'id': str(i)}]},
            'metadata': {'pagination': {'currentPage': i, 'totalPages': 5}}
        }
        for i in range(5)
    ]
    
    mock_client._make_request = Mock(side_effect=page_responses)

    result = mock_client._fetch_all_pages('/germplasm', max_pages=2)

    assert mock_client._make_request.call_count == 2
    assert len(result) == 2


def test_fetch_with_pagesize_parameter(mock_client):
    """Test that pagesize parameter is passed correctly"""
    mock_client._make_request = Mock(return_value={
        'result': {'data': [{'id': '1'}]},
        'metadata': {'pagination': {'currentPage': 0, 'totalPages': 1}}
    })

    mock_client._fetch_all_pages('/germplasm', pagesize=50)

    call_args = mock_client._make_request.call_args
    assert call_args[0][1]['pageSize'] == 50


def test_fetch_with_query_params(mock_client):
    """Test that query parameters are passed through"""
    mock_client._make_request = Mock(return_value={
        'result': {'data': [{'id': '1'}]},
        'metadata': {'pagination': {'currentPage': 0, 'totalPages': 1}}
    })

    params = {'programDbId': '123', 'commonCropName': 'SweetPotato'}
    mock_client._fetch_all_pages('/germplasm', params=params)

    call_args = mock_client._make_request.call_args
    passed_params = call_args[0][1]
    assert passed_params['programDbId'] == '123'
    assert passed_params['commonCropName'] == 'SweetPotato'
    assert passed_params['pageSize'] == 100  # default


def test_fetch_handles_missing_result(mock_client):
    """Test graceful handling when 'result' key is missing"""
    mock_client._make_request = Mock(return_value={})

    result = mock_client._fetch_all_pages('/germplasm')

    assert result == []


def test_fetch_handles_api_error(mock_client):
    """Test graceful handling when _make_request returns empty dict (error)"""
    mock_client._make_request = Mock(return_value={})

    result = mock_client._fetch_all_pages('/germplasm')

    assert result == []
