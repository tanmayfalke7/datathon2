// Function to fetch and display course recommendations
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
    
    // Direct call to recommendations API
    fetch('/api/recommendations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            domain: 'Programming',
            difficulty: 'Beginner'
        })
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