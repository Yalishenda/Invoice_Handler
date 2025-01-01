import fitz
import numpy
import pandas as pd


def extract_hebrew_text_from_pdf(pdf_path):
    """
    Extracts Hebrew text from a PDF using PyMuPDF (Fitz).
    """
    # Open the PDF
    doc = fitz.open(pdf_path)
    extracted_text = ""

    # Iterate through all pages
    for page in doc:
        # Extract text from the page
        extracted_text += page.get_text("text")

    doc.close()
    return extracted_text


def parse_reservation_data(text):
    """
    Parses reservation data from Hebrew text using patterns.
    """
    import re

    # Define regex patterns for fields
    name_pattern = r"שם:\s([א-ת\s]+)"
    date_pattern = r"תאריך:\s(\d{2}/\d{2}/\d{4})"
    time_pattern = r"שעה:\s(\d{2}:\d{2})"
    guests_pattern = r"מספר אורחים:\s(\d+)"

    # Extract data
    name = re.search(name_pattern, text)
    date = re.search(date_pattern, text)
    time = re.search(time_pattern, text)
    guests = re.search(guests_pattern, text)

    # Safely return data
    return {
        "שם": name.group(1) if name else "",
        "תאריך": date.group(1) if date else "",
        "שעה": time.group(1) if time else "",
        "מספר אורחים": guests.group(1) if guests else ""
    }


def process_pdfs_to_csv(pdf_files, output_csv):
    """
    Processes a list of PDFs to extract reservation data and save it as a CSV.
    """
    all_reservations = []

    for pdf in pdf_files:
        # Extract text from PDF
        text = extract_hebrew_text_from_pdf(pdf)

        # Parse reservation data
        reservation_data = parse_reservation_data(text)
        all_reservations.append(reservation_data)

    # Save data to CSV
    df = pd.DataFrame(all_reservations)
    df.to_csv(output_csv, encoding="utf-8-sig", index=False)
    print(f"Reservations saved to {output_csv}")


# Example usage
pdf_files = ["reservation1.pdf", "reservation2.pdf"]  # List of PDF file paths
output_csv = "reservations.csv"

#process_pdfs_to_csv(pdf_files, output_csv)
