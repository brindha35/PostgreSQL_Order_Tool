
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


session = requests.Session()

retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)

session.mount("http://", adapter)


def get_customer_details(customer_id):

    url = f"http://127.0.0.1:8001/customers/{customer_id}"

    try:
        response = session.get(url, timeout=5)

        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            return "Customer not found"

        return "CRM server error"

    except requests.exceptions.Timeout:
        return "CRM request timed out"

    except requests.exceptions.RequestException:
        return "Unable to connect to CRM"

if __name__ == "__main__":

    result = get_customer_details(3)

    print(result)