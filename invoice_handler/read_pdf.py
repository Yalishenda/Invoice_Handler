import camelot
import pandas as pd
from bidi.algorithm import get_display
import invoice_handler.log_functions as log
import shutil
import tempfile
from datetime import datetime
import os


def extract_dataframe(pdf_paths):
    """
    Extracts tables from a list of PDF paths, combines them into a single DataFrame,
    and handles logging of payments to ensure unique entries are processed.

    Args:
        pdf_paths (list of str): List of paths to PDF files.

    Returns:
        pd.DataFrame: Rows of data not already logged, ready for further processing.
    """
    # English headers for PDF data
    standard_headers = [
        "for_payment",
        "details",
        "invoice_amount_w_vat",
        "date",
        "invoice_num",
        "reference"
    ]

    combined_df = pd.DataFrame(columns=standard_headers)
    new_rows = []

    # Initialize logs
    log.initialize_logs()
    processed_logs = log.read_log("payments")

    temp_dir = tempfile.mkdtemp()  # Create a temporary directory for Camelot

    try:
        for pdf_path in pdf_paths:
            try:
                # Set the custom temporary directory
                tables = camelot.read_pdf(
                    "downloads/" + pdf_path, pages="all", flavor="lattice", strip_text="\n"
                )
            except Exception as e:
                print(f"Error processing PDF: {pdf_path}. Error: {e}")
                continue

            if len(tables) > 0:
                df = tables[0].df
                df = df.drop(df.index[0])  # Drop the first row (assumed to be headers in the extracted table)
                df = df.reset_index(drop=True)
                df = df.apply(lambda col: col.map(lambda x: get_display(x) if isinstance(x, str) else x))
                df.columns = standard_headers

                # Append the tail of the table from page 2 if it exists
                if len(tables) > 1:
                    df_tail = tables[1].df
                    df_tail = df_tail.reset_index(drop=True)
                    df_tail = df_tail.apply(lambda col: col.map(lambda x: get_display(x) if isinstance(x, str) else x))
                    df_tail.columns = df.columns  # Align columns with the first table
                    df = pd.concat([df, df_tail], ignore_index=True)

                # Process rows for logging
                for _, row in df.iterrows():
                    invoice_num = row["invoice_num"]
                    total_with_vat = row["invoice_amount_w_vat"]

                    # Check if the row already exists in logs
                    if not any(
                            log_entry["invoice_num"] == invoice_num and log_entry["total_with_vat"] == total_with_vat
                            for log_entry in processed_logs
                    ):
                        # Add to logs
                        log_entry = {
                            "file_name": pdf_path,
                            "invoice_num": invoice_num,
                            "total_with_vat": total_with_vat,
                            "timestamp": datetime.now().isoformat()
                        }
                        log.write_log("payments", log_entry)

                        # Keep track of new rows
                        new_rows.append(row)

                combined_df = pd.concat([combined_df, df], ignore_index=True)

    finally:
        # Ensure all temporary files are cleaned up
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                try:
                    os.remove(os.path.join(root, file))
                except Exception as e:
                    print(f"Error deleting temporary file {file}: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)

    # Reset the index of the returned DataFrame
    return pd.DataFrame(new_rows, columns=standard_headers).reset_index(drop=True)

