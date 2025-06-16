# MoMo-Data-Analysis
# MoMo SMS Dashboard

A simple web app that reads your mobile money SMS messages, organizes them, and shows you helpful charts and statistics about your transactions.

## What This App Does

Think of this as your personal mobile money transaction analyzer. It takes your SMS messages about money transfers, payments, and deposits, then creates a beautiful dashboard where you can see:

- How much money you've sent and received
- What types of transactions you make most
- Charts showing your spending patterns
- A searchable list of all your transactions

## What You'll See

### SMS Reading
- Reads SMS messages from a backup file
- Automatically sorts them into categories (like "Money Received", "Bill Payments", etc.)
- Extracts important info like amounts, dates, and transaction fees

###  Data Storage
- Saves all your transaction data in a simple database
- No duplicates - smart enough to skip messages it's already seen
- Creates the database automatically when you first run it

### Web Dashboard
- Beautiful, easy-to-use web interface
- Works on your phone and computer
- Shows charts and graphs of your spending
- Filter transactions by type or date range

### Reports & Charts
- See totals: how much you've spent, received, paid in fees
- Pie charts showing what types of transactions you make most
- Bar charts of your biggest transactions
- Average transaction amounts

## What You Need

- **Python 3.7 or newer** (this is the programming language the app uses)
- **Flask** (a simple web framework - we'll install this)
- Your SMS messages in XML format (usually from a phone backup)

## How to Set It Up

### Step 1: Get Python Ready
Make sure you have Python installed. Open your terminal/command prompt and type:
```bash
python --version
```
You should see something like "Python 3.8.x" or newer.

### Step 2: Install Flask
```bash
pip install flask
```
This installs the web framework we need.

### Step 3: Download the Project
- Download all the project files
- Put them in a folder on your computer
- Make sure all the Python files (.py files) are in the same folder

### Step 4: Create Folders
Create two empty folders inside your project folder:
```bash
mkdir logs
mkdir database
```
- `logs` - stores error messages if something goes wrong
- `database` - where your transaction data gets saved

### Step 5: Add Your SMS Data
- Get your SMS messages in XML format (usually from an Android SMS backup app)
- Name the file `sms_data.xml`
- Put it in your main project folder

### Step 6: Process Your SMS Messages
Run this command to read and organize your SMS data:
```bash
python data_processing.py
```
This will:
- Read your SMS file
- Find all the mobile money messages
- Sort them by type (payments, receipts, etc.)
- Save them to the database

### Step 7: Start the Web App
```bash
python app.py
```
You should see a message saying the server is running.

### Step 8: Open Your Dashboard
- Open your web browser
- Go to: `http://localhost:5000`
- You should see your dashboard with all your transaction data!

## How to Use the Dashboard

### Main Statistics
At the top, you'll see:
- **Total Transactions**: How many mobile money transactions you've made
- **Total Amount**: All the money you've sent and received combined
- **Total Fees**: How much you've paid in transaction fees
- **Average**: Your average transaction amount

### Filtering Your Data
Use the dropdown menus to:
- **Filter by Type**: Show only certain types of transactions (like "Airtime Payments")
- **Filter by Date**: Show transactions from a specific time period
- **Reset**: Clear all filters to see everything again

### Charts
- **Pie Chart**: Shows what percentage of your transactions are each type
- **Bar Chart**: Shows your biggest transactions

### Transaction List
Scroll down to see a table with all your transactions, including:
- Date and time
- Transaction type
- Amount
- Fees paid
- Any additional details

## Files in This Project

**data_processing.py** - Reads and processes SMS messages
**database.py** - Manages the database
**app.py** - The web application
**templates/index.html** - The dashboard webpage
**static/script.js** - Makes the dashboard interactive
**static/style.css** - Makes the dashboard look good
**logs/unprocessed_messages.log** - Error messages (if any)
**database/momo.db** - Your transaction database
**sms_data.xml** - Your SMS messages (you provide this)
