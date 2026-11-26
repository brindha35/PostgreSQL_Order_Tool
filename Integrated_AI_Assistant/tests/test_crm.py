
from unittest.mock import patch, Mock

from app.tools import get_customer_details


@patch("app.tools.session.get")
def test_get_customer_success(mock_get):

    mock_response = Mock()

    mock_response.json.return_value = {
        "name": "Priya",
        "plan": "Basic",
        "email": "priya@gmail.com",
        "city": "Bangalore"
    }

    mock_get.return_value = mock_response

    result = get_customer_details(2)

    assert result["name"] == "Priya"
    assert result["plan"] == "Basic"
    assert result["email"] == "priya@gmail.com"


@patch("app.tools.session.get")
def test_get_customer_not_found(mock_get):

    mock_response = Mock()
    mock_response.status_code = 404

    import requests

    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError(response=mock_response)
    )

    mock_get.return_value = mock_response

    result = get_customer_details(99)

    assert result == {"error": "Customer not found"}


@patch("app.tools.session.get")
def test_get_customer_server_error(mock_get):

    mock_response = Mock()
    mock_response.status_code = 500

    import requests

    mock_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError(response=mock_response)
    )

    mock_get.return_value = mock_response

    result = get_customer_details(2)

    assert result == {"error": "CRM server error"}
