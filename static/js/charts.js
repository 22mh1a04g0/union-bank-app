document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('transactionChart');
    if (!ctx) return;

    // Get data from data attributes
    const chartDataElement = document.getElementById('chartData');
    const deposits = parseFloat(chartDataElement.getAttribute('data-deposits')) || 0;
    const withdrawals = parseFloat(chartDataElement.getAttribute('data-withdrawals')) || 0;

    let chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Deposits', 'Withdrawals'],
            datasets: [{
                data: [deposits, withdrawals],
                backgroundColor: [
                    '#0033A0', // Union Bank Blue
                    '#E31837'  // Union Bank Red
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-main').trim()
                    }
                }
            }
        }
    });

    // Update chart colors on theme change
    window.addEventListener('themeChanged', () => {
        chart.options.plugins.legend.labels.color = getComputedStyle(document.documentElement).getPropertyValue('--text-main').trim();
        chart.update();
    });
});
