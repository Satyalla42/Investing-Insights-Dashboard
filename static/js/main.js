function updateDashboard() {
    const ticker = document.getElementById('ticker').value.trim().toUpperCase();
    const assetType = document.getElementById('assetType').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    console.log('Starting updateDashboard with:', { ticker, assetType, startDate, endDate });

    if (!ticker) {
        showError('Please enter a ticker symbol');
        return;
    }

    showLoading();

    fetch(`/get_tickers/${assetType}`)
        .then(response => {
            console.log('Ticker check response:', response);
            return response.json();
        })
        .then(tickers => {
            console.log('Available tickers:', tickers);
            if (!tickers.includes(ticker)) {
                throw new Error(`Ticker ${ticker} not found. Please make sure to include the exchange suffix if needed (e.g., .HK for Hong Kong stocks, .T for Tokyo stocks).`);
            }
            
            const requestData = {
                ticker: ticker,
                asset_type: assetType,
                start_date: startDate,
                end_date: endDate
            };
            console.log('Sending data request:', requestData);
            
            return fetch('/get_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
        })
        .then(response => {
            console.log('Data response status:', response.status);
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || `Failed to fetch data (${response.status})`);
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.metrics) updateMetrics(data.metrics);
            if (data.candlestick_chart && data.volume_chart) {
                updateCharts(data.candlestick_chart, data.volume_chart);
            } else {
                showError('No chart data available');
            }
            hideLoading();
        })
        .catch(error => {
            console.error('Error in updateDashboard:', error);
            showError(error.message);
            hideLoading();
        });
}

function updateCharts(candlestickData, volumeData) {
    console.log('updateCharts called');

    if (!candlestickData || !volumeData) {
        document.getElementById('candlestickChart').innerHTML = '<div class="alert alert-warning">No chart data available</div>';
        document.getElementById('volumeChart').innerHTML = '<div class="alert alert-warning">No volume data available</div>';
        return;
    }

    try {
        // Parse the chart data
        const candlestickConfig = typeof candlestickData === 'string' ? 
            JSON.parse(candlestickData) : candlestickData;
        const volumeConfig = typeof volumeData === 'string' ? 
            JSON.parse(volumeData) : volumeData;

        // Custom theme colors
        const themeColors = {
            oliveGreen: '#556B2F',
            oliveGreenLight: '#6B8E23',
            background: '#f8f9fa',
            gridColor: '#e9ecef',
            textColor: '#212529'
        };

        // Set chart configurations
        const chartConfig = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['lasso2d']
        };

        // Common axis styling
        const commonAxisStyle = {
            title: {
                font: {
                    size: 14,
                    color: themeColors.textColor
                }
            },
            tickfont: {
                size: 12,
                color: themeColors.textColor
            },
            gridcolor: themeColors.gridColor,
            linecolor: themeColors.gridColor,
            showgrid: true
        };

        // Update candlestick chart layout
        candlestickConfig.layout = {
            ...candlestickConfig.layout,
            paper_bgcolor: themeColors.background,
            plot_bgcolor: themeColors.background,
            font: {
                color: themeColors.textColor
            },
            title: {
                text: 'Price History',
                font: {
                    size: 16,
                    color: themeColors.textColor
                }
            },
            xaxis: {
                ...commonAxisStyle,
                title: {
                    text: 'Date',
                    ...commonAxisStyle.title
                }
            },
            yaxis: {
                ...commonAxisStyle,
                title: {
                    text: 'Price',
                    ...commonAxisStyle.title
                }
            },
            margin: { t: 30, l: 60, r: 20, b: 40 }
        };

        // Update volume chart layout
        volumeConfig.layout = {
            ...volumeConfig.layout,
            paper_bgcolor: themeColors.background,
            plot_bgcolor: themeColors.background,
            font: {
                color: themeColors.textColor
            },
            title: {
                text: 'Volume',
                font: {
                    size: 16,
                    color: themeColors.textColor
                }
            },
            xaxis: {
                ...commonAxisStyle,
                title: {
                    text: 'Date',
                    ...commonAxisStyle.title
                }
            },
            yaxis: {
                ...commonAxisStyle,
                title: {
                    text: 'Volume',
                    ...commonAxisStyle.title
                }
            },
            margin: { t: 30, l: 60, r: 20, b: 40 }
        };

        // Update candlestick colors
        if (candlestickConfig.data && candlestickConfig.data.length > 0) {
            candlestickConfig.data = candlestickConfig.data.map(trace => ({
                ...trace,
                increasing: { line: { color: themeColors.oliveGreen } },
                decreasing: { line: { color: '#d32f2f' } },
                line: { color: themeColors.oliveGreen }
            }));
        }

        // Update volume colors
        if (volumeConfig.data && volumeConfig.data.length > 0) {
            volumeConfig.data = volumeConfig.data.map(trace => ({
                ...trace,
                marker: {
                    ...trace.marker,
                    color: themeColors.oliveGreenLight,
                    line: { color: themeColors.oliveGreen }
                }
            }));
        }

        // Create the candlestick chart
        Plotly.newPlot('candlestickChart', candlestickConfig.data, candlestickConfig.layout, chartConfig);
        
        // Create the volume chart
        Plotly.newPlot('volumeChart', volumeConfig.data, volumeConfig.layout, chartConfig);

    } catch (error) {
        console.error('Error updating charts:', error);
        console.error('Error details:', {
            message: error.message,
            stack: error.stack
        });
        document.getElementById('candlestickChart').innerHTML = '<div class="alert alert-danger">Error creating charts: ' + error.message + '</div>';
        document.getElementById('volumeChart').innerHTML = '<div class="alert alert-danger">Error creating charts: ' + error.message + '</div>';
    }
}

function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger';
    alertDiv.textContent = message;
    document.getElementById('metricsContainer').innerHTML = '';
    document.getElementById('metricsContainer').appendChild(alertDiv);
}

function showLoading() {
    document.getElementById('metricsContainer').innerHTML = '<div class="loading">Loading...</div>';
}

function hideLoading() {
    const loadingElement = document.querySelector('.loading');
    if (loadingElement) {
        loadingElement.remove();
    }
}

function updateMetrics(metrics) {
    if (!metrics) return;
    
    const container = document.getElementById('metricsContainer');
    container.innerHTML = '';
    
    // Define metrics with their explanations
    const metricsInfo = {
        'Average Volume': {
            value: metrics['Average Volume'],
            explanation: 'The typical number of shares traded daily. Higher volume often indicates more active trading and interest in the stock.'
        },
        'Daily Return': {
            value: metrics['Daily Return'],
            explanation: 'The percentage change in price from the previous trading day. Shows how much you would have gained or lost if you held the stock for one day.'
        },
        'Highest Price': {
            value: metrics['Highest Price'],
            explanation: 'The highest price the asset has reached in the selected time period. Useful for understanding the asset\'s peak value.'
        },
        'Latest Price': {
            value: metrics['Latest Price'],
            explanation: 'The most recent trading price of the asset. This is the current market value.'
        },
        'Lowest Price': {
            value: metrics['Lowest Price'],
            explanation: 'The lowest price the asset has reached in the selected time period. Shows the bottom of the price range.'
        },
        'Volatility (30d)': {
            value: metrics['Volatility (30d)'],
            explanation: 'A measure of price fluctuation over the last 30 days. Higher volatility means more price swings and potentially higher risk.'
        }
    };
    
    for (const [key, info] of Object.entries(metricsInfo)) {
        if (info.value && typeof info.value !== 'object') {
            const metricDiv = document.createElement('div');
            metricDiv.className = 'metric-card';
            
            metricDiv.innerHTML = `
                <div class="metric-label">${key}</div>
                <div class="metric-value">${info.value}</div>
                <div class="metric-explanation">${info.explanation}</div>
            `;
            
            container.appendChild(metricDiv);
        }
    }
}

// Add event listener when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, setting up event listeners');
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Get date input elements
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const maxDate = '2025-08-31';
    const minDate = '2020-01-01';

    // Function to validate dates
    function validateDates() {
        const startDate = new Date(startDateInput.value);
        const endDate = new Date(endDateInput.value);
        const maxAllowedDate = new Date(maxDate);
        const minAllowedDate = new Date(minDate);

        // Validate start date
        if (startDate > maxAllowedDate) {
            startDateInput.value = maxDate;
        } else if (startDate < minAllowedDate) {
            startDateInput.value = minDate;
        }

        // Validate end date
        if (endDate > maxAllowedDate) {
            endDateInput.value = maxDate;
        } else if (endDate < minAllowedDate) {
            endDateInput.value = minDate;
        }

        // Ensure start date is not after end date
        if (startDate > endDate) {
            startDateInput.value = endDateInput.value;
        }
    }

    // Add event listeners for date changes
    startDateInput.addEventListener('change', validateDates);
    endDateInput.addEventListener('change', validateDates);

    // Add form submit event listener
    const form = document.getElementById('analysisForm');
    if (form) {
        console.log('Form found, adding submit listener');
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            validateDates(); // Validate dates before submitting
            console.log('Form submitted');
            updateDashboard();
        });
    } else {
        console.error('Analysis form not found!');
    }
    
    // Trigger initial update
    updateDashboard();
}); 