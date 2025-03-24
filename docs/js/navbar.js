document.addEventListener("DOMContentLoaded", function () {
    let basePath = "./";

    let navbarHTML = `
        <!-- 🌟 Overlay voor dim-effect -->
        <div id="navOverlay" class="nav-overlay"></div>

        <!-- 🌟 Navigatiemenu -->
        <div id="mobileNav" class="nav-menu">
            <div class="nav-header">
                <span id="closeNav" class="close-nav">&times;</span>
            </div>
            <a class="nav-link" href="${basePath}index.html">Home</a>
            <a class="nav-link" href="${basePath}blog.html">Blog</a>
            <a class="nav-link" href="${basePath}gamemode.html">Gamemode</a>
        </div>

        <!-- 🌟 Navbar -->
        <nav class="navbar fixed-top">
            <div class="container d-flex justify-content-center">
                <button id="navToggle" class="nav-toggle-btn">☰ The Mona</button>
            </div>
        </nav>
    `;

    document.getElementById("navbar-placeholder").innerHTML = navbarHTML;

    // Voeg functionaliteit toe voor het openen/sluiten van de mobiele navigatie
    let navToggle = document.getElementById("navToggle");
    let closeNav = document.getElementById("closeNav");
    let mobileNav = document.getElementById("mobileNav");
    let navOverlay = document.getElementById("navOverlay");

    if (navToggle && closeNav && mobileNav && navOverlay) {
        navToggle.addEventListener("click", function () {
            mobileNav.classList.add("show");
            navOverlay.classList.add("show");
        });

        closeNav.addEventListener("click", function () {
            mobileNav.classList.remove("show");
            navOverlay.classList.remove("show");
        });

        navOverlay.addEventListener("click", function () {
            mobileNav.classList.remove("show");
            navOverlay.classList.remove("show");
        });

        document.querySelectorAll(".nav-link").forEach(link => {
            link.addEventListener("click", function () {
                mobileNav.classList.remove("show");
                navOverlay.classList.remove("show");
            });
        });
    }
});
