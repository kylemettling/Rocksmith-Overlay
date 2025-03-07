function initHitrateChart() {
    const ctx = document.getElementById('hitrate_chart').getContext('2d');
    hitrateChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array(10).fill().map((_, i) => i + 1), // Last 10 samples
            datasets: [{
                label: 'Hitrate (%)',
                data: Array(10).fill(0), // Initialize with zeros
                borderColor: 'red',
                fill: false,
                tension: 0.1
            }]
        },
        options: {
            scales: {
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Hitrate (%)'
                    },
                    ticks: {
                        color: 'white',
                        beginAtZero: true,
                        max: 100
                    }
                },
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Last 10 Samples'
                    },
                    ticks: {
                        color: 'white'
                    }
                }
            },
            plugins: { legend: { labels: { color: 'white' } } }
        }
    });
    console.log("Hitrate chart initialized");
}

function updateFields(data) {
    document.getElementById('song').textContent = data.song || 'N/A';
    document.getElementById('artist').textContent = data.artist || 'N/A';
    document.getElementById('album').textContent = data.album || 'N/A';
    document.getElementById('theory').textContent = data.theory || 'N/A';
    document.getElementById('trivia').textContent = data.trivia || 'N/A';
    document.getElementById('hitrate').textContent = data.hitrate !== undefined ? data.hitrate.toFixed(2) : 'N/A';
    document.getElementById('streak').textContent = data.streak || 'N/A';
    document.getElementById('highest_streak').textContent = data.highest_streak || 'N/A';
    document.getElementById('live_ai').textContent = data.live_ai ? 'ON' : 'OFF';

    // Update chart if hitrate data exists
    if (data.hitrate_history && Array.isArray(data.hitrate_history)) {
        hitrateChart.data.datasets[0].data = data.hitrate_history.slice(-10).map(val => val || 0);
        hitrateChart.update();
    }
}

function fetchData() {
    fetch('/data')
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error, status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            updateFields(data);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            updateFields({});
        });
}

let hitrateChart;
initHitrateChart();
fetchData();
setInterval(fetchData, 2000); // Update every 2 seconds

document.getElementById('close_button').addEventListener('click', () => window.close());

document.getElementById('live_ai_button').addEventListener('click', () => {
    fetch('/toggle_live_ai', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            document.getElementById('live_ai').textContent = data.live_ai ? 'ON' : 'OFF';
        })
        .catch(error => console.error('Toggle error:', error));
});