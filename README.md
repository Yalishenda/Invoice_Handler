# Invoice Handler Automation

This project automates the processing of restaurant payment invoices received via email. It extracts data from PDF attachments, organizes the information, and updates a Notion database using the Notion API. This tool streamlines the process of tracking payments and managing invoices efficiently.

## Features

- **PDF Data Extraction**: Extracts key information from invoice PDFs, such as invoice number, date, and amount.
- **Email Parsing**: Automatically identifies and processes incoming emails with invoice attachments.
- **Notion API Integration**: Sends extracted data to a specified Notion database for seamless organization and tracking.
- **Error Handling**: Detects and logs errors during PDF parsing or API communication.

## Gmail API Integration

This project uses the Gmail API for parsing and retrieving emails. For proper functioning, the `invoice_handler` directory must contain a `config` directory with the following:

1. `__init__.py`: This file should include:
   - `notion_token`: Your Notion API token.
   - `database_id`: The ID of the Notion database.
   - `gmail_secret_filename`: The filename of the Gmail API credentials JSON.
   - `sender_email`: The sender email address to process invoices from.

2. `client_secret_*.json`: The Gmail API credentials file, downloaded from the Google Cloud Console.


## Project Structure

```
Invoice_Handler/
├── downloads                         # Downloaded PDF files directory
├── invoice_handler/
│   ├── config/
│   │   ├── __init__.py               # Configuration file with tokens and secrets
│   │   └── client_secret_*.json      # Gmail API credentials
│   ├── logs/
│   │   ├── emails.json               # Log of processed emails add PDF's
│   │   ├── payments.json             # Log of payment details from each PDF
│   │   ├── sessions.json             # Log of sessions
│   │   └── status_updates.json       # Log of status updates in Notion
│   ├── gmail_handler.py              # Handles Gmail API interactions
│   ├── log_functions.py              # Functions for logging
│   ├── notion_handler.py             # Handles Notion API interactions
│   └── read_pdf.py                   # Reads and extracts data from PDFs
├── main.py                           # Main script to run the automation
├── poetry.lock                       # Poetry lock file
├── pyproject.toml                    # Poetry project configuration
├── README.md                         # Project documentation
└── requirements.txt                  # Python dependencies
```

## Prerequisites

1. Python 3.9 or above.
2. Access to a Notion account with API credentials.
3. Gmail API credentials for accessing emails.
4. Email account credentials for receiving invoice emails.

## Acknowledgments

- [Notion API Documentation](https://developers.notion.com/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
