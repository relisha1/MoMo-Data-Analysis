import xml.etree.ElementTree as ET
import sqlite3
import re
import logging
from datetime import datetime

# Logging for unclassified messages
logging.basicConfig(filename='unprocessed_messages.log', level=logging.INFO)

# DB setup
conn = sqlite3.connect('momo_sms.db')
c = conn.cursor()

# Create table
c.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_id TEXT,
    type TEXT,
    amount INTEGER,
    fee INTEGER,
    sender TEXT,
    receiver TEXT,
    date TEXT,
    details TEXT
)
''')
conn.commit()

# Helpers
def parse_date(text):
    try:
        return datetime.strptime(text, '%Y-%m-%d %H:%M:%S').isoformat()
    except Exception:
        return None

def categorize_sms(body):
    b = body.lower()
    if 'received' in b: return 'Incoming Money'
    if 'payment' in b and 'to' in b: return 'Payments to Code Holders'
    if 'transfer' in b: return 'Transfers to Mobile Numbers'
    if 'bank deposit' in b: return 'Bank Deposits'
    if 'airtime' in b: return 'Airtime Bill Payments'
    if 'cash power' in b: return 'Cash Power Bill Payments'
    if 'third party' in b or 'initiated by' in b: return 'Transactions Initiated by Third Parties'
    if 'withdrawn' in b: return 'Withdrawals from Agents'
    if 'bank transfer' in b: return 'Bank Transfers'
    if 'internet bundle' in b or 'voice bundle' in b: return 'Internet and Voice Bundle Purchases'
    return 'Unknown'

def extract_data(body):
    tx_id = re.search(r'TxId[:\s]*([0-9]+)', body)
    amount = re.search(r'(\d+)\s*RWF', body)
    fee = re.search(r'Fee[:\s]*(\d+)\s*RWF', body)
    date = re.search(r'Date[:\s]*([\d-]+\s[\d:]+)', body)
    sender = re.search(r'from ([\w\s]+)[\.,]', body)
    receiver = re.search(r'to ([\w\s]+)[\.,]', body)

    return (
        tx_id.group(1) if tx_id else None,
        int(amount.group(1)) if amount else None,
        int(fee.group(1)) if fee else 0,
        sender.group(1).strip() if sender else None,
        receiver.group(1).strip() if receiver else None,
        parse_date(date.group(1)) if date else None,
        body
    )

# Load and parse XML
tree = ET.parse('modified_sms_v2.xml')
root = tree.getroot()

for sms in root.findall('sms'):
    body = sms.find('body').text
    if not body:
        continue

    category = categorize_sms(body)
    tx_id, amount, fee, sender, receiver, date, details = extract_data(body)

    if category == 'Unknown' or not date:
        logging.info(f"Unprocessed: {body}")
        continue

    c.execute('''
        INSERT INTO transactions (tx_id, type, amount, fee, sender, receiver, date, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (tx_id, category, amount, fee, sender, receiver, date, details))

conn.commit()
conn.close()
print("Data inserted into momo_sms.db")

