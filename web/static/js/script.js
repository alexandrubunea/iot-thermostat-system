function sendButtonUpdate(action) {
    fetch('/button-press', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: action }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Button action received by server:', data);
    })
    .catch(error => {
        console.error('Error sending button action:', error);
    });
}

function formatTime(minutes) {
    if(minutes >= 200)
        return "indefinitely".toUpperCase();

    const totalSeconds = minutes * 60;
    const hrs = Math.floor(totalSeconds / 3600);
    const mins = Math.floor((totalSeconds % 3600) / 60);
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
}

let tempChart, humidityChart; // Variables for the Chart.js instances

function initializeCharts() {
    // Initialize Temperature Chart
    const tempCtx = document.getElementById('temperatureChart').getContext('2d');
    tempChart = new Chart(tempCtx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 100], // Placeholder data
                backgroundColor: ['#3498db', '#ecf0f1'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '85%',
            rotation: -125,
            circumference: 250,
            plugins: { tooltip: { enabled: false } },
            legend: { display: false }
        }
    });

    // Initialize Humidity Chart
    const humCtx = document.getElementById('humidityChart').getContext('2d');
    humidityChart = new Chart(humCtx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 100], // Placeholder data
                backgroundColor: ['#1abc9c', '#ecf0f1'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            cutout: '85%',
            rotation: -125,
            circumference: 250,
            plugins: { tooltip: { enabled: false } },
            legend: { display: false }
        }
    });
}

function updateData() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            // Update DOM elements
            document.getElementById('temperatureDisplay').textContent = `${data.temperature} °C`;
            document.getElementById('humidityDisplay').textContent = `${data.humidity} %`;
            document.getElementById('runningTimeDisplay').textContent = formatTime(data.running_time);
            document.getElementById('targetTemperature').textContent = `${data.target_temperature} °C`;

            // Update Temperature Chart
            tempChart.data.datasets[0].data = [data.temperature, 100 - data.temperature];
            tempChart.update();

            // Update Humidity Chart
            humidityChart.data.datasets[0].data = [data.humidity, 100 - data.humidity];
            humidityChart.update();
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Set up periodic updates every 250ms
setInterval(updateData, 250);

// Initial data load and chart initialization
window.onload = () => {
    initializeCharts();
    updateData();
};