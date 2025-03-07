document.addEventListener('DOMContentLoaded', function () {
    var ctx = document.getElementById('hitrateChart').getContext('2d');
    var hitrateChart;

    var hitrate_history = [];
    var tension = 0.1;

    var options = {
        scales: {
            y: { display: true, type: 'linear', suggestedMin: -1, suggestedMax: 1, title: { display: true, text: 'Hitrate (%)' } },
            x: { display: true, type: 'linear', suggestedMin: 0, suggestedMax: 10, title: { display: true, text: 'Last 10 Samples' }, ticks: { color: 'white', beginAtZero: true, max: 100 } }
        },
        plugins: { legend: { labels: { color: 'white' } } }
    };

    console.log("Hitrate chart initialized.");

    function updateFields(data) {
        document.getElementById('song').textContent = data.song || 'N/A';
        document.getElementById('artist').textContent = data.artist || 'N/A';
        document.getElementById('album').textContent = data.album || 'N/A';
        document.getElementById('theory').textContent = data.theory || 'N/A';
        document.getElementById('trivia').textContent = data.trivia || 'N/A';
        document.getElementById('hitrate').textContent = data.hitrate ? data.hitrate.toFixed(2) + '%' : '0.0%';
        document.getElementById('streak').textContent = data.streak || 'N/A';
        document.getElementById('highest_streak').textContent = data.highest_streak || 'N/A';
        document.getElementById('live_ai').textContent = data.live_ai ? 'ON' : 'OFF';

        if (data.hitrate_history && Array.isArray(data.hitrate_history)) {
            hitrate_history = data.hitrate_history.slice(-10);
            if (!hitrateChart) {
                hitrateChart = new Chart(ctx, { type: 'line', data: { labels: hitrate_history.map((_, idx) => idx), datasets: [{ label: 'Hitrate', data: hitrate_history, borderColor: 'white', tension: tension, fill: false }] }, options });
            } else {
                hitrateChart.data.labels = hitrate_history.map((_, idx) => idx);
                hitrateChart.data.datasets[0].data = hitrate_history;
                hitrateChart.update();
            }
        }
    }

    function fetchData() {
        fetch('/data').then(r => { if (!r.ok) throw new Error(`HTTP error, status: ${r.status}`); return r.json(); }).then(updateFields).catch(e => console.error('Error fetching data:', e));
    }

    setInterval(fetchData, 2000);

    document.getElementById('close_button').addEventListener('click', () => window.close());
    document.getElementById('live_ai_button').addEventListener('click', () => fetch('/toggle_live_ai', { method: 'POST' }).then(r => r.json()).then(d => document.getElementById('live_ai').textContent = d.live_ai ? 'ON' : 'OFF').catch(e => console.error('Toggle error:', e)));
});