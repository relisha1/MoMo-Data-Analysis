// Global variables
let transactions = [];
let filteredTransactions = [];

// DOM Elements
const loadingElement = document.getElementById('loading');
const errorMessageElement = document.getElementById('errorMessage');
const successMessageElement = document.getElementById('successMessage');
const noDataElement = document.getElementById('noDataMessage');
const transactionsTableBody = document.getElementById('transactionsTableBody');

// Filter elements
const filterType = document.getElementById('filterType');
const filterDateFrom = document.getElementById('filterDateFrom');
const filterDateTo = document.getElementById('filterDateTo');
const btnFilter = document.getElementById('btnFilter');
const btnReset = document.getElementById('btnReset');

// Statistics elements
const totalTransactions = document.getElementById('totalTransactions');
const totalAmount = document.getElementById('totalAmount');
const totalFees = document.getElementById('totalFees');
const avgTransaction = document.getElementById('avgTransaction');

// Chart variables
let typeChart = null;
let amountChart = null;

// Utility functions
function showLoading() {
    if (loadingElement) loadingElement.style.display = 'block';
    if (errorMessageElement) errorMessageElement.style.display = 'none';
    if (successMessageElement) successMessageElement.style.display = 'none';
}

function hideLoading() {
    if (loadingElement) loadingElement.style.display = 'none';
}

function showError(message) {
    hideLoading();
    if (errorMessageElement) {
        errorMessageElement.textContent = message;
        errorMessageElement.style.display = 'block';
    }
    if (successMessageElement) successMessageElement.style.display = 'none';
}

function showSuccess(message) {
    hideLoading();
    if (successMessageElement) {
        successMessageElement.textContent = message;
        successMessageElement.style.display = 'block';
    }
    if (errorMessageElement) errorMessageElement.style.display = 'none';
    
    // Auto-hide success message after 3 seconds
    setTimeout(() => {
        if (successMessageElement) successMessageElement.style.display = 'none';
    }, 3000);
}

// Convert database row to transaction object
function convertDbRowToTransaction(row) {
    if (Array.isArray(row)) {
        // Row is an array from database
        return {
            id: row[0],
            type: row[1],
            category: row[1],
            amount: row[2],
            fee: row[3],
            date: row[4],
            details: row[5],
            transaction_id: row[6] || `TX${row[0]}`,
            sender: extractSenderFromDetails(row[5]),
            receiver: extractReceiverFromDetails(row[5])
        };
    } else {
        // Row is already an object
        return {
            ...row,
            sender: row.sender || extractSenderFromDetails(row.details),
            receiver: row.receiver || extractReceiverFromDetails(row.details)
        };
    }
}

// Extract sender from transaction details
function extractSenderFromDetails(details) {
    if (!details) return 'N/A';
    
    const senderMatch = details.match(/from ([+\d\s]+)/i);
    return senderMatch ? senderMatch[1].trim() : 'N/A';
}

// Extract receiver from transaction details
function extractReceiverFromDetails(details) {
    if (!details) return 'N/A';
    
    const receiverMatch = details.match(/to ([+\d\s]+)/i);
    return receiverMatch ? receiverMatch[1].trim() : 'N/A';
}

// Fetch transactions from the Flask API
async function fetchTransactions() {
    showLoading();
    
    try {
        console.log('Fetching transactions from /transactions...');
        const response = await fetch('/transactions');
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('Fetched data:', data);
        
        if (Array.isArray(data)) {
            // Convert raw database rows to transaction objects
            transactions = data.map(row => convertDbRowToTransaction(row));
            filteredTransactions = [...transactions];
            updateDisplay();
            showSuccess(`Loaded ${transactions.length} transactions successfully!`);
        } else {
            throw new Error('Invalid data format received');
        }
        
    } catch (error) {
        console.error('Error fetching transactions:', error);
        showError(`Failed to load transactions: ${error.message}`);
        
        // If no data, show sample data button
        if (transactionsTableBody) {
            transactionsTableBody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 20px;">
                        <p>No transactions found. This might be because:</p>
                        <ul style="text-align: left; margin: 10px auto; max-width: 400px;">
                            <li>The database is empty</li>
                            <li>The database file doesn't exist</li>
                            <li>You need to run the data processing script first</li>
                        </ul>
                        <p>Try running: <code>python data_processing.py</code></p>
                    </td>
                </tr>
            `;
        }
    }
}

// Update all display elements
function updateDisplay() {
    updateStatistics();
    updateTable();
    updateCharts();
}

// Update statistics
function updateStatistics() {
    const stats = calculateStatistics(filteredTransactions);
    
    if (totalTransactions) totalTransactions.textContent = stats.count;
    if (totalAmount) totalAmount.textContent = `${stats.totalAmount.toLocaleString()} RWF`;
    if (totalFees) totalFees.textContent = `${stats.totalFees.toLocaleString()} RWF`;
    if (avgTransaction) avgTransaction.textContent = `${stats.avgAmount.toLocaleString()} RWF`;
}

// Calculate statistics
function calculateStatistics(data) {
    if (!data || data.length === 0) {
        return { count: 0, totalAmount: 0, totalFees: 0, avgAmount: 0 };
    }
    
    const count = data.length;
    const totalAmount = data.reduce((sum, t) => sum + (t.amount || 0), 0);
    const totalFees = data.reduce((sum, t) => sum + (t.fee || 0), 0);
    const avgAmount = Math.round(totalAmount / count);
    
    return { count, totalAmount, totalFees, avgAmount };
}

// Update transactions table
function updateTable() {
    if (!transactionsTableBody) return;
    
    if (!filteredTransactions || filteredTransactions.length === 0) {
        transactionsTableBody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 20px;">
                    No transactions found matching your criteria.
                </td>
            </tr>
        `;
        if (noDataElement) noDataElement.style.display = 'block';
        return;
    }
    
    if (noDataElement) noDataElement.style.display = 'none';
    
    transactionsTableBody.innerHTML = filteredTransactions.map(transaction => `
        <tr>
            <td>${transaction.id || 'N/A'}</td>
            <td>${transaction.transaction_id || `TX${transaction.id || '000'}`}</td>
            <td title="${transaction.type || transaction.category || 'N/A'}">${truncateText(transaction.type || transaction.category || 'N/A', 30)}</td>
            <td>${(transaction.amount || 0).toLocaleString()}</td>
            <td>${(transaction.fee || 0).toLocaleString()}</td>
            <td>${transaction.sender || 'N/A'}</td>
            <td>${transaction.receiver || 'N/A'}</td>
            <td>${formatDate(transaction.date)}</td>
        </tr>
    `).join('');
}

// Utility function to truncate text
function truncateText(text, maxLength) {
    if (!text) return 'N/A';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

// Format date for display
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (error) {
        return dateString;
    }
}

// Apply filters
function applyFilters() {
    const typeValue = filterType ? filterType.value : '';
    const dateFrom = filterDateFrom ? filterDateFrom.value : '';
    const dateTo = filterDateTo ? filterDateTo.value : '';
    
    filteredTransactions = transactions.filter(transaction => {
        // Type filter
        if (typeValue && transaction.type !== typeValue && transaction.category !== typeValue) {
            return false;
        }
        
        // Date filter
        if (dateFrom || dateTo) {
            const transactionDate = new Date(transaction.date);
            
            if (dateFrom && transactionDate < new Date(dateFrom)) {
                return false;
            }
            
            if (dateTo && transactionDate > new Date(dateTo + ' 23:59:59')) {
                return false;
            }
        }
        
        return true;
    });
    
    updateDisplay();
    showSuccess(`Filters applied! Showing ${filteredTransactions.length} of ${transactions.length} transactions.`);
}

// Reset filters
function resetFilters() {
    if (filterType) filterType.value = '';
    if (filterDateFrom) filterDateFrom.value = '';
    if (filterDateTo) filterDateTo.value = '';
    
    filteredTransactions = [...transactions];
    updateDisplay();
    showSuccess('Filters reset successfully!');
}

// Update charts
function updateCharts() {
    updateTypeChart();
    updateAmountChart();
}

// Update transaction type chart
function updateTypeChart() {
    const ctx = document.getElementById('typeChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (typeChart) {
        typeChart.destroy();
    }
    
    // Prepare data
    const typeCounts = {};
    filteredTransactions.forEach(transaction => {
        const type = transaction.type || transaction.category || 'Other';
        typeCounts[type] = (typeCounts[type] || 0) + 1;
    });
    
    const labels = Object.keys(typeCounts);
    const data = Object.values(typeCounts);
    
    typeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF',
                    '#4BC0C0', '#FF6384'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Update amount chart
function updateAmountChart() {
    const ctx = document.getElementById('amountChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (amountChart) {
        amountChart.destroy();
    }
    
    // Prepare data (top 10 transactions by amount)
    const sortedTransactions = [...filteredTransactions]
        .sort((a, b) => (b.amount || 0) - (a.amount || 0))
        .slice(0, 10);
    
    const labels = sortedTransactions.map((t, index) => `TX${index + 1}`);
    const amounts = sortedTransactions.map(t => t.amount || 0);
    
    amountChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Amount (RWF)',
                data: amounts,
                backgroundColor: '#36A2EB',
                borderColor: '#2E8BC0',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString() + ' RWF';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    
    // Add event listeners
    if (btnFilter) {
        btnFilter.addEventListener('click', applyFilters);
    }
    
    if (btnReset) {
        btnReset.addEventListener('click', resetFilters);
    }
    
    // Fetch initial data
    fetchTransactions();
});

// Export functions for global access
window.applyFilters = applyFilters;
window.resetFilters = resetFilters;