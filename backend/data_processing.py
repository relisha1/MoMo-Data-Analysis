# data_processing.py
import xml.etree.ElementTree as ET
import re
import logging
from datetime import datetime
from database import create_database, insert_transaction

# Set up logging for general logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create a separate logger for unprocessed messages
unprocessed_logger = logging.getLogger('unprocessed')
unprocessed_logger.setLevel(logging.WARNING)  # Only log warnings and errors

# Create a file handler for unprocessed messages
file_handler = logging.FileHandler('logs/unprocessed_messages.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
unprocessed_logger.addHandler(file_handler)

# Define transaction categories
TRANSACTION_CATEGORIES = {
    "received": "Incoming Money",
    "payment": "Payments to Code Holders",
    "transferred": "Transfers to Mobile Numbers",
    "deposit": "Bank Deposits",
    "airtime": "Airtime Bill Payments",
    "cash power": "Cash Power Bill Payments",
    "third party": "Transactions Initiated by Third Parties",
    "withdrawn": "Withdrawals from Agents",
    "bank transfer": "Bank Transfers",
    "internet bundle": "Internet and Voice Bundle Purchases",
    "voice bundle": "Internet and Voice Bundle Purchases"
}

def parse_xml(file_path):
    """
    Parses an XML file containing SMS data and extracts transaction details.
    """
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        logging.info(f"Root element: {root.tag}")
        logging.info(f"Number of <sms> elements: {len(root.findall('sms'))}")

        transactions = []
        skipped_messages = 0

        for sms in root.findall('sms'):
            body = sms.attrib.get('body')
            if body is None:
                skipped_messages += 1
                unprocessed_logger.warning(f"Skipping SMS: No 'body' attribute found. Full SMS: {ET.tostring(sms, encoding='unicode')}")
                continue

            # Skip OTP messages
            if "one-time password" in body.lower():
                skipped_messages += 1
                unprocessed_logger.warning(f"Skipping OTP message: {body}")
                continue

            try:
                category, amount, fee, date = categorize_sms(body, sms.attrib)
                transaction = {
                    'category': category,
                    'amount': amount,
                    'fee': fee,
                    'date': date,
                    'body': body
                }
                transactions.append(transaction)
                insert_transaction(transaction)  # Insert into the database
            except ValueError as e:
                skipped_messages += 1
                unprocessed_logger.warning(f"Unprocessed message: {body}. Error: {e}")
            except Exception as e:
                skipped_messages += 1
                unprocessed_logger.error(f"Unexpected error processing SMS: {body}. Error: {e}")

        logging.info(f"Processed {len(transactions)} transactions. Skipped {skipped_messages} messages.")
        return transactions

    except ET.ParseError as e:
        unprocessed_logger.error(f"Error parsing XML file: {e}")
        return []
    except FileNotFoundError as e:
        unprocessed_logger.error(f"File not found: {e}")
        return []
    except Exception as e:
        unprocessed_logger.error(f"An unexpected error occurred: {e}")
        return []

def categorize_sms(body, sms_attrib):
    """
    Categorizes an SMS body and extracts transaction details.
    """
    logging.debug(f"Categorizing SMS: {body}")

    # Determine the category
    body_lower = body.lower()
    category = "Other"
    for keyword, cat in TRANSACTION_CATEGORIES.items():
        if keyword in body_lower:
            category = cat
            break

    # Extract amount
    amount_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+) RWF', body)
    if amount_match is None:
        # Try alternative formats (e.g., "igura 2,000 RWF" or "DEPOSIT RWF 25000")
        amount_match = re.search(r'igura (\d{1,3}(?:,\d{3})*|\d+) RWF', body_lower)
        if amount_match is None:
            amount_match = re.search(r'DEPOSIT RWF (\d{1,3}(?:,\d{3})*|\d+)', body)
            if amount_match is None:
                raise ValueError(f"Amount not found in body: {body}")
    amount = int(amount_match.group(1).replace(",", ""))
    if amount <= 0:
        raise ValueError(f"Invalid amount: {amount}")

    # Extract fee
    fee_match = re.search(r'(fee|charges)[: ]*(\d{1,3}(?:,\d{3})*|\d+) RWF', body_lower)
    fee = int(fee_match.group(2).replace(",", "")) if fee_match else 0

    # Extract and validate date
    date_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', body)
    if date_match is None:
        # Try alternative formats (e.g., "2024-08-23")
        date_match = re.search(r'\d{4}-\d{2}-\d{2}', body)
        if date_match is None:
            # Use the current date as a fallback
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.warning(f"No date found in body. Using current date: {date}")
        else:
            date = date_match.group() + " 00:00:00"  # Add default time
    else:
        date = date_match.group()
    try:
        datetime.strptime(date, "%Y-%m-%d %H:%M:%S")  # Validate date format
    except ValueError:
        raise ValueError(f"Invalid date format: {date}")

    logging.debug(f"Category: {category}, Amount: {amount}, Fee: {fee}, Date: {date}")
    return category, amount, fee, date

if __name__ == "__main__":
    # Create the database and table if they don't exist
    create_database()

    # Parse the XML file and process transactions
    transactions = parse_xml("../sms_data.xml")
    print(f"Processed {len(transactions)} transactions.")
