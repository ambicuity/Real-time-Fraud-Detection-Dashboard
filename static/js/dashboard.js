/**
 * Real-time Fraud Detection Dashboard JavaScript
 * Handles WebSocket connections, real-time updates, and chart visualization
 */

// Global variables
let socket = null;
let fraudTrendChart = null;
let transactionDistributionChart = null;
let isMonitoring = false;
let transactionData = [];
let alertData = [];

// Chart data storage
let chartData = {
    fraudTrend: {
        labels: [],
        transactions: [],
        frauds: []
    },
    transactionTypes: {
        safe: 0,
        suspicious: 0,
        fraud: 0
    }
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Fraud Detection Dashboard Loading...');
    
    initializeWebSocket();
    initializeCharts();
    initializeEventListeners();
    loadInitialData();
    
    console.log('✅ Dashboard Initialized');
});

/**
 * Initialize WebSocket connection
 */
function initializeWebSocket() {
    socket = io();
    
    // Connection events
    socket.on('connect', function() {
        console.log('🔗 Connected to WebSocket server');
        updateConnectionStatus(true);
        updateWebSocketStatus('Connected');
    });
    
    socket.on('disconnect', function() {
        console.log('❌ Disconnected from WebSocket server');
        updateConnectionStatus(false);
        updateWebSocketStatus('Disconnected');
    });
    
    // Data events
    socket.on('stats_update', function(stats) {
        updateDashboardStats(stats);
    });
    
    socket.on('new_transaction', function(transaction) {
        addNewTransaction(transaction);
        updateCharts();
    });
    
    socket.on('fraud_alert', function(alert) {
        addFraudAlert(alert);
        showFraudModal(alert);
        playAlertSound();
    });
}

/**
 * Initialize Chart.js charts
 */
function initializeCharts() {
    // Fraud Trend Chart
    const fraudTrendCtx = document.getElementById('fraud-trend-chart').getContext('2d');
    fraudTrendChart = new Chart(fraudTrendCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Total Transactions',
                data: [],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: 'Fraud Detected',
                data: [],
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
    
    // Transaction Distribution Chart
    const distributionCtx = document.getElementById('transaction-distribution-chart').getContext('2d');
    transactionDistributionChart = new Chart(distributionCtx, {
        type: 'doughnut',
        data: {
            labels: ['Safe', 'Suspicious', 'Fraud'],
            datasets: [{
                data: [100, 0, 0],
                backgroundColor: [
                    '#27ae60',
                    '#f39c12',
                    '#e74c3c'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Start/Stop monitoring buttons
    document.getElementById('start-monitoring').addEventListener('click', startMonitoring);
    document.getElementById('stop-monitoring').addEventListener('click', stopMonitoring);
    
    // Fraud only toggle
    document.getElementById('fraud-only-toggle').addEventListener('change', toggleFraudOnlyView);
    
    // Modal close
    document.querySelector('.close-modal').addEventListener('click', closeModal);
    
    // Close modal when clicking outside
    document.getElementById('fraud-modal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
    
    // ESC key to close modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

/**
 * Load initial data from API
 */
async function loadInitialData() {
    try {
        // Load current statistics
        const statsResponse = await fetch('/api/stats');
        const stats = await statsResponse.json();
        updateDashboardStats(stats);
        
        // Load recent transactions
        const transactionsResponse = await fetch('/api/transactions?limit=50');
        const transactions = await transactionsResponse.json();
        
        transactionData = transactions;
        updateTransactionsTable();
        
        // Load recent alerts
        const alertsResponse = await fetch('/api/alerts?limit=20');
        const alerts = await alertsResponse.json();
        
        alertData = alerts;
        updateAlertsPanel();
        
        console.log('📊 Initial data loaded successfully');
        
    } catch (error) {
        console.error('❌ Error loading initial data:', error);
    }
}

/**
 * Start real-time monitoring
 */
async function startMonitoring() {
    try {
        const response = await fetch('/api/start_monitoring');
        const result = await response.json();
        
        if (result.status === 'started' || result.status === 'already_running') {
            isMonitoring = true;
            document.getElementById('start-monitoring').style.display = 'none';
            document.getElementById('stop-monitoring').style.display = 'inline-flex';
            
            console.log('▶️ Monitoring started');
            showNotification('Real-time monitoring started', 'success');
        }
    } catch (error) {
        console.error('❌ Error starting monitoring:', error);
        showNotification('Failed to start monitoring', 'error');
    }
}

/**
 * Stop real-time monitoring
 */
async function stopMonitoring() {
    try {
        const response = await fetch('/api/stop_monitoring');
        const result = await response.json();
        
        if (result.status === 'stopped') {
            isMonitoring = false;
            document.getElementById('start-monitoring').style.display = 'inline-flex';
            document.getElementById('stop-monitoring').style.display = 'none';
            
            console.log('⏹️ Monitoring stopped');
            showNotification('Real-time monitoring stopped', 'info');
        }
    } catch (error) {
        console.error('❌ Error stopping monitoring:', error);
        showNotification('Failed to stop monitoring', 'error');
    }
}

/**
 * Update dashboard statistics
 */
function updateDashboardStats(stats) {
    document.getElementById('total-transactions').textContent = stats.total_transactions?.toLocaleString() || '0';
    document.getElementById('fraud-detected').textContent = stats.fraud_detected?.toLocaleString() || '0';
    document.getElementById('total-amount').textContent = `$${(stats.total_amount || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    document.getElementById('blocked-amount').textContent = `$${(stats.fraud_amount || 0).toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    
    if (stats.last_updated) {
        const updateTime = moment(stats.last_updated).format('YYYY-MM-DD HH:mm:ss');
        document.getElementById('last-updated').textContent = updateTime;
    }
}

/**
 * Add new transaction to the data and update UI
 */
function addNewTransaction(transaction) {
    transactionData.unshift(transaction);
    
    // Keep only last 100 transactions in memory for performance
    if (transactionData.length > 100) {
        transactionData = transactionData.slice(0, 100);
    }
    
    updateTransactionsTable();
    
    // Update chart data
    updateChartData(transaction);
}

/**
 * Update chart data with new transaction
 */
function updateChartData(transaction) {
    const now = moment().format('HH:mm');
    
    // Update fraud trend data
    if (chartData.fraudTrend.labels.length === 0 || 
        chartData.fraudTrend.labels[chartData.fraudTrend.labels.length - 1] !== now) {
        
        chartData.fraudTrend.labels.push(now);
        chartData.fraudTrend.transactions.push(1);
        chartData.fraudTrend.frauds.push(transaction.is_fraud ? 1 : 0);
        
        // Keep only last 20 data points
        if (chartData.fraudTrend.labels.length > 20) {
            chartData.fraudTrend.labels.shift();
            chartData.fraudTrend.transactions.shift();
            chartData.fraudTrend.frauds.shift();
        }
    } else {
        // Update current time slot
        const lastIndex = chartData.fraudTrend.transactions.length - 1;
        chartData.fraudTrend.transactions[lastIndex]++;
        if (transaction.is_fraud) {
            chartData.fraudTrend.frauds[lastIndex]++;
        }
    }
    
    // Update transaction distribution
    if (transaction.fraud_score > 0.7) {
        chartData.transactionTypes.fraud++;
    } else if (transaction.fraud_score > 0.3) {
        chartData.transactionTypes.suspicious++;
    } else {
        chartData.transactionTypes.safe++;
    }
}

/**
 * Update charts with new data
 */
function updateCharts() {
    // Update fraud trend chart
    fraudTrendChart.data.labels = chartData.fraudTrend.labels;
    fraudTrendChart.data.datasets[0].data = chartData.fraudTrend.transactions;
    fraudTrendChart.data.datasets[1].data = chartData.fraudTrend.frauds;
    fraudTrendChart.update('none');
    
    // Update transaction distribution chart
    const total = chartData.transactionTypes.safe + 
                  chartData.transactionTypes.suspicious + 
                  chartData.transactionTypes.fraud;
    
    if (total > 0) {
        transactionDistributionChart.data.datasets[0].data = [
            chartData.transactionTypes.safe,
            chartData.transactionTypes.suspicious,
            chartData.transactionTypes.fraud
        ];
        transactionDistributionChart.update('none');
    }
}

/**
 * Update transactions table
 */
function updateTransactionsTable() {
    const tbody = document.getElementById('transactions-body');
    const fraudOnlyToggle = document.getElementById('fraud-only-toggle').checked;
    
    let filteredData = transactionData;
    if (fraudOnlyToggle) {
        filteredData = transactionData.filter(t => t.is_fraud);
    }
    
    if (filteredData.length === 0) {
        tbody.innerHTML = '<tr class="no-data"><td colspan="6">No transactions to display</td></tr>';
        return;
    }
    
    tbody.innerHTML = '';
    
    filteredData.slice(0, 20).forEach(transaction => {
        const row = document.createElement('tr');
        
        // Add animation class for new transactions
        if (transactionData.indexOf(transaction) === 0) {
            row.classList.add(transaction.is_fraud ? 'new-fraud-transaction' : 'new-transaction');
        }
        
        const time = moment(transaction.timestamp).format('HH:mm:ss');
        const amount = `$${transaction.amount.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        const merchant = transaction.merchant;
        const userId = transaction.user_id;
        const score = transaction.fraud_score.toFixed(3);
        
        // Determine score class
        let scoreClass = 'low';
        if (transaction.fraud_score > 0.7) scoreClass = 'high';
        else if (transaction.fraud_score > 0.3) scoreClass = 'medium';
        
        // Determine status
        let status = 'Safe';
        let statusClass = 'status-safe';
        if (transaction.is_fraud) {
            status = 'FRAUD';
            statusClass = 'status-fraud';
        } else if (transaction.fraud_score > 0.3) {
            status = 'Suspicious';
            statusClass = 'status-suspicious';
        }
        
        row.innerHTML = `
            <td>${time}</td>
            <td>${amount}</td>
            <td>${merchant}</td>
            <td>${userId}</td>
            <td><span class="fraud-score ${scoreClass}">${score}</span></td>
            <td><span class="status-badge ${statusClass}">${status}</span></td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * Toggle fraud-only view
 */
function toggleFraudOnlyView() {
    updateTransactionsTable();
}

/**
 * Add fraud alert
 */
function addFraudAlert(alert) {
    alertData.unshift(alert);
    
    // Keep only last 50 alerts
    if (alertData.length > 50) {
        alertData = alertData.slice(0, 50);
    }
    
    updateAlertsPanel();
    updateAlertCount();
}

/**
 * Update alerts panel
 */
function updateAlertsPanel() {
    const container = document.getElementById('alerts-container');
    
    if (alertData.length === 0) {
        container.innerHTML = `
            <div class="no-alerts">
                <i class="fas fa-shield-alt"></i>
                <p>No fraud alerts</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    
    alertData.slice(0, 10).forEach(alert => {
        const alertElement = document.createElement('div');
        alertElement.className = 'alert-item';
        alertElement.addEventListener('click', () => showFraudModal(alert));
        
        const time = moment(alert.timestamp).format('MMM DD, HH:mm:ss');
        const amount = `$${alert.amount.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
        
        alertElement.innerHTML = `
            <div class="alert-header">
                <div class="alert-title">Fraud Detected</div>
                <div class="alert-time">${time}</div>
            </div>
            <div class="alert-details">
                <span class="alert-amount">${amount}</span> transaction from ${alert.merchant}
                <br>User: ${alert.user_id} | Score: ${alert.fraud_score.toFixed(3)}
            </div>
        `;
        
        container.appendChild(alertElement);
    });
}

/**
 * Update alert count
 */
function updateAlertCount() {
    document.getElementById('alert-count').textContent = alertData.length;
}

/**
 * Show fraud modal with alert details
 */
function showFraudModal(alert) {
    const modal = document.getElementById('fraud-modal');
    const modalBody = document.getElementById('fraud-modal-body');
    
    const time = moment(alert.timestamp).format('MMMM DD, YYYY at HH:mm:ss');
    const amount = `$${alert.amount.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    
    modalBody.innerHTML = `
        <div style="margin-bottom: 1rem;">
            <h3 style="color: #e74c3c; margin-bottom: 0.5rem;">
                <i class="fas fa-exclamation-triangle"></i> High-Risk Transaction Detected
            </h3>
            <p style="color: #7f8c8d; margin-bottom: 1.5rem;">${time}</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <strong>Transaction ID:</strong><br>
                    <code>${alert.transaction_id}</code>
                </div>
                <div>
                    <strong>Amount:</strong><br>
                    <span style="font-size: 1.2rem; color: #e74c3c; font-weight: bold;">${amount}</span>
                </div>
                <div>
                    <strong>Merchant:</strong><br>
                    ${alert.merchant}
                </div>
                <div>
                    <strong>User ID:</strong><br>
                    ${alert.user_id}
                </div>
                <div>
                    <strong>Fraud Score:</strong><br>
                    <span style="background: #fadbd8; color: #e74c3c; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: bold;">
                        ${alert.fraud_score.toFixed(3)}
                    </span>
                </div>
                <div>
                    <strong>Risk Level:</strong><br>
                    <span style="background: #e74c3c; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: bold;">
                        HIGH RISK
                    </span>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 1rem;">
            <h4 style="color: #2c3e50; margin-bottom: 0.5rem;">Fraud Indicators:</h4>
            <p style="background: #fff3cd; color: #856404; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107;">
                <i class="fas fa-info-circle"></i> ${alert.reason}
            </p>
        </div>
        
        <div style="background: #d4edda; color: #155724; padding: 1rem; border-radius: 8px; border-left: 4px solid #28a745;">
            <h4 style="margin-bottom: 0.5rem;"><i class="fas fa-lightbulb"></i> Recommended Actions:</h4>
            <ul style="margin-left: 1rem; margin-bottom: 0;">
                <li>Review user's recent transaction history</li>
                <li>Verify the transaction with the cardholder</li>
                <li>Consider blocking the account temporarily</li>
                <li>Investigate merchant for suspicious activity</li>
            </ul>
        </div>
    `;
    
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
}

/**
 * Close fraud modal
 */
function closeModal() {
    const modal = document.getElementById('fraud-modal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

/**
 * Update connection status
 */
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    const icon = statusElement.querySelector('i');
    
    if (connected) {
        statusElement.className = 'status-indicator connected';
        statusElement.innerHTML = '<i class="fas fa-circle"></i> Connected';
        icon.style.color = '#27ae60';
    } else {
        statusElement.className = 'status-indicator disconnected';
        statusElement.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
        icon.style.color = '#e74c3c';
    }
}

/**
 * Update WebSocket status
 */
function updateWebSocketStatus(status) {
    document.getElementById('websocket-status').textContent = status;
}

/**
 * Play alert sound for fraud detection
 */
function playAlertSound() {
    // Create audio context for alert sound
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (error) {
        console.log('Audio alert not available');
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Simple notification system (could be enhanced with a library)
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideInRight 0.3s ease;
    `;
    
    switch (type) {
        case 'success':
            notification.style.background = '#27ae60';
            break;
        case 'error':
            notification.style.background = '#e74c3c';
            break;
        case 'warning':
            notification.style.background = '#f39c12';
            break;
        default:
            notification.style.background = '#3498db';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Utility functions
window.closeModal = closeModal;