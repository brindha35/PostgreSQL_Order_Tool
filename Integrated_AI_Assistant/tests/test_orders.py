
from unittest.mock import patch, MagicMock

from orders.tools import get_order_status, get_customer_orders


@patch("orders.tools.get_connection")
def test_get_order_status_success(mock_connection):

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = (
        101, 1, "Shipped", None
    )

    result = get_order_status(101)

    assert result["order_id"] == 101
    assert result["customer_id"] == 1
    assert result["status"] == "Shipped"

    mock_conn.close.assert_called_once()


@patch("orders.tools.get_connection")
def test_get_order_status_not_found(mock_connection):

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchone.return_value = None

    result = get_order_status(999)

    assert result == {"error": "Order not found"}

    mock_conn.close.assert_called_once()


@patch("orders.tools.get_connection")
def test_get_customer_orders(mock_connection):

    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.fetchall.return_value = [
        (101, 1, None, "Shipped"),
        (102, 1, None, "Processing")
    ]

    result = get_customer_orders(1)

    assert len(result) == 2
    assert result[0]["order_id"] == 101
    assert result[0]["status"] == "Shipped"
    assert result[1]["status"] == "Processing"

    mock_conn.close.assert_called_once()
