summaryChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels,
        datasets: [{
            label: 'Number of Transactions',
            data: counts,
            backgroundColor: '#ffcb05', // MTN yellow
            borderColor: '#000000',     // MTN black
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true,
                ticks: { color: '#000' }
            },
            x: {
                ticks: { color: '#000' }
            }
        },
        plugins: {
            legend: {
                labels: {
                    color: '#000'
                }
            }
        }
    }
});
