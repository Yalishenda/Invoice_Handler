import json
import os
from datetime import datetime

# Log file paths
LOG_FILES = {
    "status_updates": "invoice_handler/logs/status_updates.json",
    "payments": "invoice_handler/logs/payments.json",
    "emails": "invoice_handler/logs/emails.json",
    "sessions": "invoice_handler/logs/sessions.json",
}


# Initialize log files if they don't exist
def initialize_logs():
    for log_name, file_path in LOG_FILES.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                json.dump([], file)


# Read all entries from a specific log
def read_log(log_name):
    with open(LOG_FILES[log_name], 'r') as file:
        return json.load(file)


# Add a new entry to a specific log
def write_log(log_name, entry):
    with open(LOG_FILES[log_name], 'r+') as file:
        logs = json.load(file)
        logs.append(entry)
        file.seek(0)
        json.dump(logs, file, indent=4)


def log_session(start_time, end_time, pdf_count, invoices_extracted, pages_updated, absent_invoices):
    entry = {
        "start_time": start_time,
        "end_time": end_time,
        "pdf_count": pdf_count,
        "invoices_extracted": invoices_extracted,
        "pages_updated": pages_updated,
        "absent_invoices": absent_invoices,
        "timestamp": datetime.now().isoformat()
    }
    write_log("sessions", entry)
