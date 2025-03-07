document.addEventListener('DOMContentLoaded', function () {
    const overlay = document.getElementById('overlay');
    var ctx = document.getElementById('hitrateChart').getContext('2d');
    var hitrateChart;

    var hitrate_history = [];
    var tension = 0.1;

    // Drag variables
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;

    // Drag functionality
    overlay.addEventListener('mousedown', startDragging);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDragging);

    function startDragging(e) {
        initialX = e.clientX - currentX;
        initialY = e.clientY - currentY;
        isDragging = true;
        overlay.style.cursor = 'grabbing';
    }

    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            overlay.style.left = currentX + 'px';
            overlay.style.top = currentY + 'px';
        }
    }

    function stopDragging() {
        isDragging = false;
        overlay.style.cursor = 'move';
    }

    // Initialize position
    currentX = parseInt(overlay.style.left) || 0;
    currentY = parseInt(overlay.style.top) || 0;

    var options = {
        scales: {
            y: {
                display: true,
                type: 'linear',
                suggestedMin: -1,
                suggestedMax: 1,
                title: {
                    display: true,
                    text: 'Hitrate (%)'
                }
            },
            x: {
                display: true,
                type: 'linear',
                suggestedMin: 0,
                suggestedMax: 10,
                title: {
                    display: true,
                    text: 'Last 10 Samples'
                },
                ticks: {
                    color: 'white',
                    beginAtZero: true,
                    max: 100
                }
            }
        },
        plugins: {
            legend: {
                labels: {
                    color: 'white'
                }
            }
        }
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

        // Update chart if hitrate data exists
        if (data.hitrate_history && Array.isArray(data.hitrate_history)) {
            hitrate_history = data.hitrate_history.slice(-10); // Keep last 10 values
            if (!hitrateChart) {
                hitrateChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: hitrate_history.map((_, idx) => idx),
                        datasets: [{
                            label: 'Hitrate',
                            data: hitrate_history,
                            borderColor: 'white',
                            tension: tension,
                            fill: false
                        }]
                    },
                    options: options
                });
            } else {
                hitrateChart.data.labels = hitrate_history.map((_, idx) => idx);
                hitrateChart.data.datasets[0].data = hitrate_history;
                hitrateChart.update();
            }
        }
    }

    function fetchData() {
        fetch('/data') // Relative URL for browser, absolute for PyQt
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error, status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                updateFields(data);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    setInterval(fetchData, 2000); // Update every 2 seconds

    document.getElementById('close_button').addEventListener('click', () => {
        if (window.process && window.process.exit) window.process.exit(); // For standalone
        else window.close(); // For browser
    });
    document.getElementById('live_ai_button').addEventListener('click', () => {
        fetch('/toggle_live_ai', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                document.getElementById('live_ai').textContent = data.live_ai ? 'ON' : 'OFF';
            })
            .catch(error => console.error('Toggle error:', error));
    });
});