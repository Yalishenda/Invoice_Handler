import invoice_handler.gmail_handler as mail
import invoice_handler.notion_handler as notion
import invoice_handler.read_pdf as pdf
import invoice_handler.log_functions as log
from datetime import datetime

# Initialize logs
log.initialize_logs()

# Start the session logging
start_time = datetime.now().isoformat()
downloaded = mail.fetch_pdf_attachments()

if downloaded:
    pdf_count = len(downloaded)
    payment_df = pdf.extract_dataframe(downloaded)

    notion_data = notion.load_data()
    pages_to_update = []

    # Compare payment_df and notion_data
    for _, row in payment_df.iterrows():
        matching_row = notion_data[notion_data['invoice_num'] == row['invoice_num']]

        if not matching_row.empty:
            page = matching_row.iloc[0].to_dict()

            if page['status'] != 'paid':
                pages_to_update.append(page)
                payment_df.drop(_, inplace=True)

    # Update pages in Notion
    pages_updated = 0
    for page in pages_to_update:
        notion.update_page_status(page, 'paid')
        pages_updated += 1

    # Log absent invoices
    absent_invoices = payment_df.to_dict(orient='records')
    if absent_invoices:
        print("Invoices not found in Notion:", absent_invoices)

    # End the session logging
    end_time = datetime.now().isoformat()
    log.log_session(
        start_time=start_time,
        end_time=end_time,
        pdf_count=pdf_count,
        invoices_extracted=len(payment_df) + len(pages_to_update),
        pages_updated=pages_updated,
        absent_invoices=absent_invoices
    )

else:
    print("We are up to date. No new PDF file found")
