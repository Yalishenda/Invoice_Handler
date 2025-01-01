import requests
import datetime
from config import notion_token, database_id
from reservation_model import *


headers = {
    "Authorization": "Bearer " + notion_token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}


def get_pages(amount=100):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"

    payload = {"page_size": amount}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    import json
    with open('db.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)  # indent=4?
    results = data['results']
    return results


def create_page(data: dict):
    create_url = "https://api.notion.com/v1/pages"

    payload = {"parent": {"database_id": database_id}, "properties": data}

    res = requests.post(create_url, headers=headers, json=payload)
    print(res.status_code)
    return res


pages = get_pages(200)
reservations = []
bads = []

for page in pages:
    booking = read_booking(page)
    if booking.total_w_vat is not None:
        reservations.append(booking)
    else:
        print(booking.__repr__())
        bads.append(booking)

print(f'Added {len(reservations)} from total {len(pages)} pages')
for bad in bads:
    print(bad.url)
