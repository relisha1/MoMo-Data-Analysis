from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('momo_sms.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/transactions')
def get_transactions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if (tx_type := request.args.get('type')):
            query += " AND type = ?"
            params.append(tx_type)
        if (date_from := request.args.get('date_from')):
            query += " AND date >= ?"
            params.append(date_from)
        if (date_to := request.args.get('date_to')):
            query += " AND date <= ?"
            params.append(date_to)
        if (min_amount := request.args.get('min_amount')):
            query += " AND amount >= ?"
            params.append(min_amount)

        query += " ORDER BY date DESC LIMIT 100"

        rows = cursor.execute(query, params).fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/summary_by_type')
def summary_by_type():
    try:
        conn = get_db_connection()
        rows = conn.execute('''
            SELECT type, COUNT(*) AS count, SUM(amount) AS total_amount
            FROM transactions
            GROUP BY type
        ''').fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

