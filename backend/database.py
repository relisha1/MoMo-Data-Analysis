# database.py
import sqlite3
import logging

# Create a logger for the database module
logger = logging.getLogger(__name__)

# Database path
DATABASE_PATH = 'database/momo.db'

def connect_db():
    """
    Connects to the SQLite database and returns a connection and cursor.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def close_db(conn):
    """
    Closes the database connection.
    """
    try:
        conn.close()
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")
        raise

def create_database():
    """
    Creates the SQLite database and the Transactions table if they don't exist.
    """
    conn, cursor = connect_db()

    try:
        # Drop the table if it exists
        cursor.execute('DROP TABLE IF EXISTS Transactions')

        # Create the table with the correct schema
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            fee INTEGER NOT NULL,
            date TEXT NOT NULL,
            details TEXT,
            transaction_id TEXT UNIQUE
        )
        ''')

        conn.commit()
        logger.info("Database and table created successfully.")
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        raise
    finally:
        close_db(conn)

def insert_transaction(transaction):
    """
    Inserts a single transaction into the database.
    """
    conn, cursor = connect_db()

    try:
        cursor.execute('''
        INSERT INTO Transactions (transaction_type, amount, fee, date, details, transaction_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            transaction['category'],
            transaction['amount'],
            transaction['fee'],
            transaction['date'],
            transaction['body'],
            transaction.get('transaction_id', None)  # Optional field
        ))
        conn.commit()
        logger.info(f"Transaction inserted successfully: {transaction}")
    except sqlite3.IntegrityError as e:
        logger.warning(f"Duplicate transaction ID: {transaction.get('transaction_id')}. Error: {e}")
    except Exception as e:
        logger.error(f"Error inserting transaction: {transaction}. Error: {e}")
    finally:
        close_db(conn)

def get_transactions():
    """
    Fetches all transactions from the database.
    """
    conn, cursor = connect_db()

    try:
        cursor.execute("SELECT * FROM Transactions")
        transactions = cursor.fetchall()
        logger.info(f"Fetched {len(transactions)} transactions.")
        return transactions
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        raise
    finally:
        close_db(conn)

def get_transaction_by_id(transaction_id):
    """
    Fetches a single transaction by its ID.
    """
    conn, cursor = connect_db()

    try:
        cursor.execute("SELECT * FROM Transactions WHERE id = ?", (transaction_id,))
        transaction = cursor.fetchone()
        if transaction:
            logger.info(f"Fetched transaction: {transaction}")
        else:
            logger.warning(f"No transaction found with ID: {transaction_id}")
        return transaction
    except Exception as e:
        logger.error(f"Error fetching transaction by ID: {e}")
        raise
    finally:
        close_db(conn)

def delete_transaction(transaction_id):
    """
    Deletes a transaction by its ID.
    """
    conn, cursor = connect_db()

    try:
        cursor.execute("DELETE FROM Transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        logger.info(f"Deleted transaction with ID: {transaction_id}")
    except Exception as e:
        logger.error(f"Error deleting transaction: {e}")
        raise
    finally:
        close_db(conn)
