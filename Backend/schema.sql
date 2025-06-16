CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_id TEXT,
    type TEXT,
    amount INTEGER,
    fee INTEGER,
    sender TEXT,
    receiver TEXT,
    date TEXT,
    details TEXT
);

