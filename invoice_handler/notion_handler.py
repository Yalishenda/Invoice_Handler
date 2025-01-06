import requests
from datetime import datetime
import pandas as pd
from invoice_handler.config import notion_token, database_id
import invoice_handler.log_functions as log

headers = {
    "Authorization": "Bearer " + notion_token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


def get_pages():
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    all_results = []
    has_more = True
    start_cursor = None

    while has_more:
        payload = {"page_size": 100}
        if start_cursor:
            payload["start_cursor"] = start_cursor

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        if 'results' in data:
            all_results.extend(data['results'])
        else:
            print(f"Error: {data}")
            break

        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor", None)

    # Save the entire data to a JSON file for reference
    import json
    with open('db.json', 'w', encoding='utf8') as f:
        json.dump(all_results, f, ensure_ascii=False)

    return all_results


def create_page(data: dict):
    create_url = "https://api.notion.com/v1/pages"

    payload = {"parent": {"database_id": database_id}, "properties": data}

    res = requests.post(create_url, headers=headers, json=payload)
    print(res.status_code)
    return res


def safe_get(dictionary, *keys):
    """Safely access nested keys in a dictionary, returning None if any key is missing."""
    current = dictionary
    for key in keys:
        if current is None or not isinstance(current, dict):
            return None
        current = current.get(key, None)
    return current


def page_to_dict(page: dict) -> dict:
    """Convert a single Notion page to a dictionary."""
    try:
        return {
            'page_id': page.get('id', None),
            'url': page.get('url', None),
            'booking_num': page['properties']['booking_num']['title'][0]['text']['content'].strip(),
            'faculty': safe_get(page, 'properties', 'faculty', 'select', 'name'),
            'order_limit': safe_get(page, 'properties', 'order_limit', 'number'),
            'res_date': (
                datetime.fromisoformat(safe_get(page, 'properties', 'date', 'date', 'start'))
                if safe_get(page, 'properties', 'date', 'date', 'start') else None
            ),
            'total_w_vat': safe_get(page, 'properties', 'total_with_vat', 'number'),
            'status': safe_get(page, 'properties', 'status', 'status', 'name'),
            'invoice_num': str(safe_get(page, 'properties', 'invoice_num', 'number')),
        }
    except Exception as e:
        print(f"Error processing page: {e}")
        return {
            'page_id': None,
            'url': None,
            'booking_num': None,
            'faculty': None,
            'order_limit': None,
            'res_date': None,
            'total_w_vat': None,
            'status': None,
            'invoice_num': None,
        }


def pages_to_df(pages: list) -> pd.DataFrame:
    """Convert a list of Notion pages into a DataFrame."""
    data = [page_to_dict(page) for page in pages]
    return pd.DataFrame(data)


def load_data():
    pages = get_pages()
    df = pages_to_df(pages)
    return df


def update_page_status(page: dict, new_status: str = 'paid'):
    """
    Updates the status of a page in the Notion database and logs the change.

    Args:
        page (dict): Dictionary containing page information.
        new_status (str): The new status to set for the page.

    Log Entry:
        booking_num, invoice_num, previous_status, current_status, page_url
    """
    update_url = f"https://api.notion.com/v1/pages/{page['page_id']}"

    previous_status = page.get('status', None)
    payload = {
        "properties": {
            "status": {
                "status": {"name": new_status}
            }
        }
    }

    response = requests.patch(update_url, headers=headers, json=payload)

    if response.status_code == 200:
        print(f"Page {page['booking_num']} status updated to '{new_status}'.")

        # Log the status update
        log_entry = {
            "booking_num": page.get('booking_num', None),
            "invoice_num": page.get('invoice_num', None),
            "previous_status": previous_status,
            "current_status": new_status,
            "page_url": page.get('url', None),
            "timestamp": datetime.now().isoformat()
        }
        log.write_log("status_updates", log_entry)

    else:
        print(f"Failed to update page {page['page_id']}. Status code: {response.status_code}, Response: {response.text}")


"""

# Example usage
pages = get_pages()
df = pages_to_df(pages)

# Display the DataFrame to the user
# print(df[['booking_num', 'status', 'total_w_vat', 'invoice_num']].sample(n=10))
# random_page = df[['page_id', 'booking_num', 'status']].sample(n=1)
# print(random_page)
# page_id = '7241cd2b-bd26-40c2-b2ef-b6f6bd832005'
# status = 'paid'

print(type(df.loc[111]))
print(df.loc[111])
page_dict = page_to_dict(pages[111])
print(page_dict)

update_page_status(df.loc[111])

"""