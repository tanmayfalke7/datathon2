// Function to fetch course recommendations
async function fetchRecommendations(courseId) {
    try {
        const response = await fetch(`/api/recommendations/${courseId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch recommendations');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        return [];
    }
}

// Function to display recommendations
function displayRecommendations(recommendations) {
    const recommendationsList = document.getElementById('recommendationsList');
    const recommendationsSection = document.getElementById('recommendationsSection');
    
    if (!recommendations || recommendations.length === 0) {
        recommendationsSection.style.display = 'none';
        return;
    }
    
    recommendationsList.innerHTML = '';
    
    recommendations.forEach(course => {
        const courseCard = document.createElement('div');
        courseCard.className = 'col-md-4 mb-4';
        courseCard.innerHTML = `
            <div class="card h-100">
                <div class="card-body">
                    <h5 class="card-title">${course.name}</h5>
                    <p class="card-text">
                        <strong>Domain:</strong> ${course.domain}<br>
                        <strong>Difficulty:</strong> ${course.difficulty}<br>
                        <strong>Duration:</strong> ${course.duration} hours
                    </p>
                    ${course.prerequisites ? `<p class="card-text"><strong>Prerequisites:</strong> ${course.prerequisites}</p>` : ''}
                    ${course.description ? `<p class="card-text">${course.description}</p>` : ''}
                    ${course.instructor ? `<p class="card-text"><strong>Instructor:</strong> ${course.instructor}</p>` : ''}
                    ${course.rating ? `<p class="card-text"><strong>Rating:</strong> ${course.rating.toFixed(1)}/5.0</p>` : ''}
                    ${course.url ? `<a href="${course.url}" target="_blank" class="btn btn-primary mt-2">View Course</a>` : ''}
                </div>
            </div>
        `;
        recommendationsList.appendChild(courseCard);
    });
    
    recommendationsSection.style.display = 'block';
}

// Function to load courses into the dropdown
async function loadCourses() {
    console.log("Loading courses...");
    try {
        const response = await fetch('/api/courses');
        console.log("API response status:", response.status);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch courses: ${response.status} ${response.statusText}`);
        }
        
        const courses = await response.json();
        console.log(`Received ${courses.length} courses from API`);
        
        const courseSelect = document.getElementById('course');
        if (!courseSelect) {
            console.error("Course select element not found!");
            return;
        }
        
        // Clear existing options except the first one
        while (courseSelect.options.length > 1) {
            courseSelect.remove(1);
        }
        
        // Add courses to the dropdown
        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.id;
            option.textContent = `${course.name} (${course.domain} - ${course.difficulty})`;
            courseSelect.appendChild(option);
        });
        
        console.log(`Loaded ${courses.length} courses into dropdown`);
        
        // Make sure the dropdown is visible and enabled
        courseSelect.style.display = 'block';
        courseSelect.disabled = false;
    } catch (error) {
        console.error('Error loading courses:', error);
        alert('Failed to load courses. Please refresh the page.');
    }
}

// Function to handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    console.log("Form submission started");
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Log form data for debugging
    for (let [key, value] of formData.entries()) {
        console.log(`Form data: ${key} = ${value}`);
    }
    
    try {
        console.log("Sending request to /api/certificates");
        const response = await fetch('/api/certificates', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            console.error('Server error:', result.error);
            throw new Error(result.error || `Failed to upload certificate: ${response.status} ${response.statusText}`);
        }
        
        console.log("Upload successful:", result);
        
        // Display recommendations if available
        if (result.recommendations) {
            console.log("Displaying recommendations:", result.recommendations);
            displayRecommendations(result.recommendations);
        }
        
        // Show success message
        alert('Certificate uploaded successfully!');
        
        // Reset form
        form.reset();
        
        // Refresh dashboard data if we're on the dashboard page
        if (window.location.pathname === '/dashboard') {
            console.log("Refreshing dashboard data after certificate upload");
            fetchUserStatistics();
            fetchCertificates();
        }
        
    } catch (error) {
        console.error('Error uploading certificate:', error);
        alert(`Failed to upload certificate: ${error.message}`);
    }
}

// Function to load dashboard data
async function loadDashboardData() {
    try {
        // Get current user ID from the page or use a default
        const userId = document.body.dataset.userId || 1;
        console.log("Loading dashboard data for user:", userId);
        
        const response = await fetch(`/api/statistics/${userId}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch statistics: ${response.status} ${response.statusText}`);
        }
        
        const stats = await response.json();
        console.log("Received statistics:", stats);
        
        updateStatistics(stats);
        createCharts(stats);
        loadCertificates(userId);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Function to update statistics
function updateStatistics(stats) {
    document.getElementById('totalCourses').textContent = stats.total_courses;
    document.getElementById('averageScore').textContent = stats.average_score.toFixed(1);
}

// Function to load certificates
async function loadCertificates(userId) {
    try {
        console.log("Loading certificates for user:", userId);
        const response = await fetch(`/api/certificates/${userId}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch certificates: ${response.status} ${response.statusText}`);
        }
        
        const certificates = await response.json();
        console.log(`Loaded ${certificates.length} certificates`);
        
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

// Function to create charts
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

// Show/hide loading indicator
function toggleLoading(show) {
    const loader = document.getElementById('loadingIndicator');
    if (show) {
        loader.classList.remove('d-none');
    } else {
        loader.classList.add('d-none');
    }
}

// Function to delete a certificate
async function deleteCertificate(certificateId) {
    try {
        const response = await fetch(`/api/certificates/${certificateId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete certificate');
        }

        // Remove the certificate from the UI
        const certificateElement = document.querySelector(`[data-certificate-id="${certificateId}"]`);
        if (certificateElement) {
            certificateElement.remove();
        }

        // Update statistics
        await fetchUserStatistics();

        // Show success message
        showNotification('Certificate deleted successfully', 'success');

    } catch (error) {
        console.error('Error deleting certificate:', error);
        showNotification(error.message || 'Failed to delete certificate', 'error');
    }
}

// Function to show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Add notification to the page
    const container = document.querySelector('.container');
    container.insertBefore(notification, container.firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Fetch and display user statistics
async function fetchUserStatistics() {
    try {
        toggleLoading(true);
        const userId = document.body.dataset.userId;
        if (!userId) {
            throw new Error('User ID not found');
        }

        console.log("Fetching statistics for user:", userId);
        const response = await fetch(`/api/statistics/${userId}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch statistics: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Statistics data:', data);
        
        // Update statistics cards
        const totalCoursesElement = document.getElementById('totalCourses');
        const averageScoreElement = document.getElementById('averageScore');
        
        if (totalCoursesElement) {
            totalCoursesElement.textContent = data.total_courses || 0;
            console.log("Updated total courses:", data.total_courses || 0);
        } else {
            console.error("Total courses element not found");
        }
        
        if (averageScoreElement) {
            averageScoreElement.textContent = `${(data.average_score || 0).toFixed(1)}%`;
            console.log("Updated average score:", data.average_score || 0);
        } else {
            console.error("Average score element not found");
        }
        
        // Create charts
        if (data.domains && Object.keys(data.domains).length > 0) {
            createDomainChart(data.domains);
        } else {
            console.log("No domain data available");
        }
        
        if (data.difficulty_levels && Object.keys(data.difficulty_levels).length > 0) {
            createDifficultyChart(data.difficulty_levels);
        } else {
            console.log("No difficulty level data available");
        }
        
        // Create progress chart with certificates data
        if (data.certificates && data.certificates.length > 0) {
            createProgressChart(data.certificates);
            document.getElementById('no-progress-data').style.display = 'none';
            document.getElementById('progress-chart').style.display = 'block';
        } else {
            document.getElementById('no-progress-data').style.display = 'block';
            document.getElementById('progress-chart').style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error fetching statistics:', error);
        const totalCoursesElement = document.getElementById('totalCourses');
        const averageScoreElement = document.getElementById('averageScore');
        
        if (totalCoursesElement) {
            totalCoursesElement.textContent = 'Error';
        }
        
        if (averageScoreElement) {
            averageScoreElement.textContent = 'Error';
        }
    } finally {
        toggleLoading(false);
    }
}

// Create domain distribution chart
function createDomainChart(data) {
    console.log("Creating domain chart with data:", data);
    const ctx = document.getElementById('domainChart');
    if (!ctx) {
        console.error("Domain chart canvas not found");
        return;
    }
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: Object.keys(data),
            datasets: [{
                data: Object.values(data),
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF'
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

// Create difficulty levels chart
function createDifficultyChart(data) {
    console.log("Creating difficulty chart with data:", data);
    const ctx = document.getElementById('difficultyChart');
    if (!ctx) {
        console.error("Difficulty chart canvas not found");
        return;
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(data),
            datasets: [{
                label: 'Number of Courses',
                data: Object.values(data),
                backgroundColor: '#36A2EB'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Create course progress chart
function createProgressChart(certificates) {
    const ctx = document.getElementById('progress-chart');
    if (!ctx) return;
    
    // Sort certificates by completion date
    certificates.sort((a, b) => new Date(a.completion_date) - new Date(b.completion_date));
    
    // Prepare data for the chart
    const labels = certificates.map(cert => cert.course_name);
    const scores = certificates.map(cert => cert.performance_score);
    const dates = certificates.map(cert => new Date(cert.completion_date).toLocaleDateString());
    
    // Create the chart
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Performance Score',
                data: scores,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Course Progress Over Time'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const cert = certificates[context.dataIndex];
                            return [
                                `Course: ${cert.course_name}`,
                                `Score: ${cert.performance_score}`,
                                `Domain: ${cert.domain}`,
                                `Difficulty: ${cert.difficulty}`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Performance Score'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Completion Date'
                    }
                }
            }
        }
    });
}

// Fetch and display certificates
async function fetchCertificates() {
    try {
        toggleLoading(true);
        const userId = document.body.dataset.userId;
        if (!userId) {
            throw new Error('User ID not found');
        }

        console.log("Fetching certificates for user:", userId);
        const response = await fetch(`/api/certificates/${userId}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch certificates: ${response.status}`);
        }
        
        const certificates = await response.json();
        console.log('Certificates data:', certificates);
        
        const tbody = document.getElementById('certificatesTableBody');
        if (!tbody) {
            console.error("Certificates table body not found");
            return;
        }
        
        tbody.innerHTML = '';
        
        if (certificates.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">No certificates found</td>
                </tr>
            `;
            return;
        }
        
        certificates.forEach(cert => {
            const row = document.createElement('tr');
            row.setAttribute('data-certificate-id', cert.id);
            row.innerHTML = `
                <td>${cert.course_name}</td>
                <td>${cert.domain}</td>
                <td>${cert.difficulty}</td>
                <td>${cert.performance_score ? `${cert.performance_score}%` : 'N/A'}</td>
                <td>${new Date(cert.completion_date).toLocaleDateString()}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="deleteCertificate(${cert.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Error fetching certificates:', error);
        const tbody = document.getElementById('certificatesTableBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        Error loading certificates. Please try again later.
                    </td>
                </tr>
            `;
        }
    } finally {
        toggleLoading(false);
    }
}

function fetchRecommendedCourses() {
    const userId = document.body.dataset.userId;
    console.log("Fetching recommendations for user ID:", userId);
    
    if (!userId) {
        console.error('User ID not found');
        const recommendationsContainer = document.getElementById('recommended-courses');
        recommendationsContainer.innerHTML = `
            <div class="col-12 text-center">
                <p class="text-danger">Error: User ID not found. Please log in again.</p>
            </div>
        `;
        return;
    }
    
    // Get the most recent certificate to base recommendations on
    fetch(`/api/certificates/${userId}`)
        .then(response => {
            console.log("Certificates API response status:", response.status);
            if (!response.ok) {
                throw new Error(`Failed to fetch certificates: ${response.status}`);
            }
            return response.json();
        })
        .then(certificates => {
            console.log("Received certificates:", certificates);
            
            if (certificates && certificates.length > 0) {
                // Get the most recent certificate
                const mostRecentCert = certificates[0];
                console.log("Using most recent certificate for recommendations:", mostRecentCert);
                
                // Use the most recent certificate to get recommendations
                return fetch('/api/recommendations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        domain: mostRecentCert.domain,
                        difficulty: mostRecentCert.difficulty,
                        name: mostRecentCert.course_name
                    })
                });
            } else {
                console.log("No certificates found, using default recommendations");
                // If no certificates, use default recommendations
                return fetch('/api/recommendations', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        domain: 'Programming',
                        difficulty: 'Beginner'
                    })
                });
            }
        })
        .then(response => {
            console.log("Recommendations API response status:", response.status);
            if (!response.ok) {
                throw new Error(`Failed to fetch recommendations: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Received recommendations data:", data);
            const recommendationsContainer = document.getElementById('recommended-courses');
            
            if (data && data.length > 0) {
                recommendationsContainer.innerHTML = data.map(course => `
                    <div class="col-md-4 mb-3">
                        <div class="card h-100">
                            <div class="card-body">
                                <h6 class="card-title">${course.name}</h6>
                                <p class="card-text">
                                    <small class="text-muted">
                                        Domain: ${course.domain}<br>
                                        Difficulty: ${course.difficulty}<br>
                                        Duration: ${course.duration} hours
                                    </small>
                                </p>
                                <p class="card-text">${course.description || 'No description available'}</p>
                                ${course.url ? `<a href="${course.url}" target="_blank" class="btn btn-sm btn-primary mt-2">View Course</a>` : ''}
                            </div>
                        </div>
                    </div>
                `).join('');
            } else {
                recommendationsContainer.innerHTML = `
                    <div class="col-12 text-center">
                        <p class="text-muted">No recommendations available at this time.</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching recommendations:', error);
            const recommendationsContainer = document.getElementById('recommended-courses');
            recommendationsContainer.innerHTML = `
                <div class="col-12 text-center">
                    <p class="text-danger">Error loading recommendations: ${error.message}</p>
                </div>
            `;
        });
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded, initializing...");
    
    // Load courses into dropdown if on upload page
    if (document.getElementById('course')) {
        loadCourses();
    }
    
    // Add form submit handler if on upload page
    const form = document.getElementById('certificateForm');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
        console.log("Form submit handler added");
    }
    
    // Load dashboard data if we're on the dashboard page
    if (window.location.pathname === '/dashboard') {
        console.log("Loading dashboard data on page load");
        const userId = document.body.dataset.userId;
        if (userId) {
            fetchUserStatistics();
            fetchCertificates();
            fetchRecommendedCourses();
        } else {
            console.error('User ID not found');
        }
    }
}); 