# app.py
from flask import Flask, jsonify, request, render_template
from database import get_transactions, get_transaction_by_id
import logging

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Root route
@app.route('/')
def home():
    return render_template('index.html')

# API endpoint to fetch all transactions
@app.route('/api/transactions', methods=['GET'])
def api_transactions():
    try:
        # Fetch all transactions from the database
        raw_transactions = get_transactions()
        
        # Convert tuples to dictionaries for JSON response
        transactions = []
        for row in raw_transactions:
            transaction = {
                'id': row[0],
                'type': row[1],  # transaction_type from DB
                'category': row[1],  # same as type for compatibility
                'amount': row[2],
                'fee': row[3],
                'date': row[4],
                'details': row[5],
                'transaction_id': row[6] if len(row) > 6 else f"TX{row[0]}"
            }
            transactions.append(transaction)
        
        logger.info(f"Returning {len(transactions)} transactions")
        return jsonify(transactions)
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        return jsonify({"error": str(e)}), 500

# API endpoint to add sample data
@app.route('/api/add-sample-data', methods=['GET'])
def add_sample_data():
    try:
        from database import insert_transaction
        from datetime import datetime, timedelta
        import random
        
        # Sample transaction data
        sample_transactions = [
            {
                'category': 'Incoming Money',
                'amount': 50000,
                'fee': 100,
                'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'body': 'You have received 50,000 RWF from +250788123456. Fee: 100 RWF. Balance: 150,000 RWF.',
                'transaction_id': 'TX001'
            },
            {
                'category': 'Transfers to Mobile Numbers',
                'amount': 25000,
                'fee': 50,
                'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
                'body': 'You have transferred 25,000 RWF to +250788654321. Fee: 50 RWF. Balance: 100,000 RWF.',
                'transaction_id': 'TX002'
            },
            {
                'category': 'Airtime Bill Payments',
                'amount': 5000,
                'fee': 0,
                'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
                'body': 'You have purchased airtime worth 5,000 RWF. Balance: 125,000 RWF.',
                'transaction_id': 'TX003'
            },
            {
                'category': 'Bank Deposits',
                'amount': 100000,
                'fee': 200,
                'date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S'),
                'body': 'You have deposited 100,000 RWF to your bank account. Fee: 200 RWF. Balance: 80,000 RWF.',
                'transaction_id': 'TX004'
            },
            {
                'category': 'Withdrawals from Agents',
                'amount': 30000,
                'fee': 300,
                'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
                'body': 'You have withdrawn 30,000 RWF from agent. Fee: 300 RWF. Balance: 180,000 RWF.',
                'transaction_id': 'TX005'
            }
        ]
        
        # Insert sample transactions
        for transaction in sample_transactions:
            try:
                insert_transaction(transaction)
            except Exception as e:
                logger.warning(f"Could not insert sample transaction: {e}")
        
        return jsonify({"message": f"Added {len(sample_transactions)} sample transactions"})
    except Exception as e:
        logger.error(f"Error adding sample data: {e}")
        return jsonify({"error": str(e)}), 500

# API endpoint to fetch transactions by category
@app.route('/api/transactions/<category>', methods=['GET'])
def api_transactions_by_category(category):
    try:
        # Fetch all transactions from the database
        raw_transactions = get_transactions()
        
        # Convert and filter transactions
        filtered_transactions = []
        for row in raw_transactions:
            if row[1] == category:  # transaction_type matches category
                transaction = {
                    'id': row[0],
                    'type': row[1],
                    'category': row[1],
                    'amount': row[2],
                    'fee': row[3],
                    'date': row[4],
                    'details': row[5],
                    'transaction_id': row[6] if len(row) > 6 else f"TX{row[0]}"
                }
                filtered_transactions.append(transaction)
        
        return jsonify(filtered_transactions)
    except Exception as e:
        logger.error(f"Error fetching transactions by category: {e}")
        return jsonify({"error": str(e)}), 500

# API endpoint to fetch a single transaction by ID
@app.route('/api/transactions/id/<int:transaction_id>', methods=['GET'])
def api_transaction_by_id(transaction_id):
    try:
        # Fetch the transaction by ID
        row = get_transaction_by_id(transaction_id)
        if row:
            transaction = {
                'id': row[0],
                'type': row[1],
                'category': row[1],
                'amount': row[2],
                'fee': row[3],
                'date': row[4],
                'details': row[5],
                'transaction_id': row[6] if len(row) > 6 else f"TX{row[0]}"
            }
            return jsonify(transaction)
        else:
            return jsonify({"error": "Transaction not found"}), 404
    except Exception as e:
        logger.error(f"Error fetching transaction by ID: {e}")
        return jsonify({"error": str(e)}), 500

# Keep original routes for backward compatibility
@app.route('/transactions', methods=['GET'])
def transactions():
    return api_transactions()

@app.route('/transactions/<category>', methods=['GET'])
def transactions_by_category(category):
    return api_transactions_by_category(category)

@app.route('/transactions/id/<int:transaction_id>', methods=['GET'])
def transaction_by_id(transaction_id):
    return api_transaction_by_id(transaction_id)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)