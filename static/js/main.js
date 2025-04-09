// Form submission handler
document.getElementById('certificateForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Create FormData object to handle file uploads
    const formData = new FormData(e.target);
    
    try {
        // Submit certificate data with FormData
        const response = await fetch('/api/certificates', {
            method: 'POST',
            body: formData // FormData automatically sets the correct Content-Type
        });
        
        if (response.ok) {
            // Get recommendations
            const recommendationsResponse = await fetch('/api/recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    course_name: formData.get('course_name'),
                    domain: formData.get('domain'),
                    duration: parseInt(formData.get('duration')),
                    difficulty: formData.get('difficulty'),
                    performance_score: parseInt(formData.get('performance_score'))
                })
            });
            
            const recommendations = await recommendationsResponse.json();
            displayRecommendations(recommendations);
            
            // Reset form
            e.target.reset();
            
            // Show success message
            alert('Certificate added successfully!');
        } else {
            throw new Error('Failed to add certificate');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while submitting the certificate.');
    }
});

// Display recommendations
function displayRecommendations(recommendations) {
    const recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.innerHTML = '';
    
    if (recommendations.length === 0) {
        recommendationsDiv.innerHTML = '<p class="text-muted">No recommendations available.</p>';
        return;
    }
    
    recommendations.forEach(rec => {
        const recElement = document.createElement('div');
        recElement.className = 'recommendation-item';
        recElement.innerHTML = `
            <h6>${rec.name}</h6>
            <p>Domain: ${rec.domain}</p>
            <p>Difficulty: ${rec.difficulty}</p>
        `;
        recommendationsDiv.appendChild(recElement);
    });
}

// Dashboard charts and statistics
async function loadDashboardData() {
    try {
        // Get current user ID from the page or use a default
        const userId = document.body.dataset.userId || 1;
        const response = await fetch(`/api/statistics/${userId}`);
        const stats = await response.json();
        
        updateStatistics(stats);
        createCharts(stats);
        loadCertificates(userId);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Load user certificates
async function loadCertificates(userId) {
    try {
        const response = await fetch(`/api/certificates/${userId}`);
        const certificates = await response.json();
        
        const certificatesTable = document.getElementById('certificatesTable');
        certificatesTable.innerHTML = '';
        
        if (certificates.length === 0) {
            certificatesTable.innerHTML = '<tr><td colspan="7" class="text-center">No certificates found</td></tr>';
            return;
        }
        
        certificates.forEach(cert => {
            const row = document.createElement('tr');
            
            // Format date
            const date = new Date(cert.completion_date);
            const formattedDate = date.toLocaleDateString();
            
            // Create certificate image cell
            let imageCell = '<td>No image</td>';
            if (cert.image_path) {
                imageCell = `<td><a href="/static/${cert.image_path}" target="_blank">View Certificate</a></td>`;
            }
            
            row.innerHTML = `
                <td>${cert.course_name}</td>
                <td>${cert.domain}</td>
                <td>${cert.duration} hours</td>
                <td>${cert.difficulty}</td>
                <td>${cert.performance_score || 'N/A'}</td>
                ${imageCell}
                <td>${formattedDate}</td>
            `;
            
            certificatesTable.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading certificates:', error);
    }
}

// Update statistics
function updateStatistics(stats) {
    document.getElementById('totalCourses').textContent = stats.total_courses;
    document.getElementById('averageScore').textContent = stats.average_score.toFixed(1);
}

// Create charts
function createCharts(stats) {
    // Domain Distribution Chart
    const domainData = [{
        values: Object.values(stats.domains),
        labels: Object.keys(stats.domains),
        type: 'pie',
        hole: 0.4
    }];
    
    const domainLayout = {
        title: 'Course Domains',
        showlegend: true
    };
    
    Plotly.newPlot('domainChart', domainData, domainLayout);
    
    // Difficulty Levels Chart
    const difficultyData = [{
        x: Object.keys(stats.difficulty_levels),
        y: Object.values(stats.difficulty_levels),
        type: 'bar'
    }];
    
    const difficultyLayout = {
        title: 'Difficulty Distribution',
        xaxis: { title: 'Difficulty Level' },
        yaxis: { title: 'Number of Courses' }
    };
    
    Plotly.newPlot('difficultyChart', difficultyData, difficultyLayout);
    
    // Progress Chart - Using actual certificate data
    // Get certificates data for the progress chart
    const userId = document.body.dataset.userId || 1;
    fetch(`/api/certificates/${userId}`)
        .then(response => response.json())
        .then(certificates => {
            // Group certificates by month
            const monthlyData = {};
            
            certificates.forEach(cert => {
                const date = new Date(cert.completion_date);
                const monthYear = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
                
                if (!monthlyData[monthYear]) {
                    monthlyData[monthYear] = 0;
                }
                monthlyData[monthYear]++;
            });
            
            // Sort months chronologically
            const sortedMonths = Object.keys(monthlyData).sort();
            
            // Calculate cumulative progress
            let cumulative = 0;
            const cumulativeData = sortedMonths.map(month => {
                cumulative += monthlyData[month];
                return cumulative;
            });
            
            // Format month labels for display
            const monthLabels = sortedMonths.map(month => {
                const [year, monthNum] = month.split('-');
                const date = new Date(year, monthNum - 1);
                return date.toLocaleDateString('default', { month: 'short', year: 'numeric' });
            });
            
            const progressData = [{
                x: monthLabels,
                y: cumulativeData,
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Courses Completed'
            }];
            
            const progressLayout = {
                title: 'Course Completion Progress',
                xaxis: { title: 'Month' },
                yaxis: { title: 'Total Courses Completed' }
            };
            
            Plotly.newPlot('progressChart', progressData, progressLayout);
        })
        .catch(error => {
            console.error('Error loading certificate data for progress chart:', error);
            
            // Fallback to empty progress chart if data loading fails
            const progressData = [{
                x: [],
                y: [],
                type: 'scatter',
                mode: 'lines+markers'
            }];
            
            const progressLayout = {
                title: 'Course Completion Progress',
                xaxis: { title: 'Month' },
                yaxis: { title: 'Total Courses Completed' }
            };
            
            Plotly.newPlot('progressChart', progressData, progressLayout);
        });
}

// Load dashboard data when on dashboard page
if (window.location.pathname === '/dashboard') {
    loadDashboardData();
} 