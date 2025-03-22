function filterArticles() {
    let searchTerm = document.getElementById("searchInput").value.toLowerCase();
    let articles = document.querySelectorAll(".article");

    articles.forEach(article => {
        let title = article.querySelector(".card-title").innerText.toLowerCase();
        let description = article.querySelector(".card-text").innerText.toLowerCase();

        if (title.includes(searchTerm) || description.includes(searchTerm)) {
            article.style.display = "block";
        } else {
            article.style.display = "none";
        }
    });
}

document.getElementById("searchInput").addEventListener("keyup", filterArticles);
