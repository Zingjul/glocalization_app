//posts.js
document.addEventListener("DOMContentLoaded", function() {
    let page = 1; // Track the page number for API pagination
    let loadMoreButton = document.getElementById("load-more");

    function fetchPosts() {
        fetch(`/api/posts/?page=${page}`)  // Fetch data from DRF API
            .then(response => response.json())
            .then(data => {
                const postList = document.getElementById("post-list");

                data.results.forEach(post => {
                    let li = document.createElement("li");
                    li.innerHTML = `<strong>${post.title}</strong> - ${post.content.substring(0, 100)}
                                    <a href="/posts/${post.id}/">Read More</a>`;
                    postList.appendChild(li);
                });

                if (!data.next) { // Hide button if no more posts to load
                    loadMoreButton.style.display = "none";
                }
            })
            .catch(error => console.error("Error fetching posts:", error));
    }

    // Load initial posts when the page loads
    fetchPosts();

    // Load more posts when button is clicked
    loadMoreButton.addEventListener("click", function() {
        page++;
        fetchPosts();
    });
});
