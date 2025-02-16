document.addEventListener("DOMContentLoaded", function () {
    let basePath = window.location.pathname.includes("/TheMona/") ? "/TheMona/" : "/";

    let navbarHTML = `
        <!-- 🌟 Navigatiemenu -->
        <div id="navOverlay" class="nav-overlay"></div>

        <div id="mobileNav" class="nav-menu">
            <div class="nav-header">
                <span id="closeNav" class="close-nav">&times;</span>
            </div>
            <a class="nav-link" href="${basePath}index.html">Home</a>
            <a class="nav-link" href="${basePath}blog.html">Blog</a>
            <a class="nav-link" href="${basePath}index.html#story">Story</a>
            <a class="nav-link" href="${basePath}index.html#project">Project</a>
            <a class="nav-link" href="${basePath}index.html#contact">Get in touch</a>
        </div>

        <!-- 🌟 Navbar -->
        <nav class="navbar fixed-top">
            <div class="container d-flex justify-content-center">
                <button id="navToggle" class="nav-toggle-btn">☰ The Mona</button>
            </div>
        </nav>
    `;

    // Voeg de navbar toe aan het document
    document.getElementById("navbar-placeholder").innerHTML = navbarHTML;

    // JavaScript-functionaliteit voor navigatiemenu
    let navToggle = document.getElementById("navToggle");
    let mobileNav = document.getElementById("mobileNav");
    let navOverlay = document.getElementById("navOverlay");
    let closeNav = document.getElementById("closeNav");

    if (navToggle && mobileNav && navOverlay && closeNav) {
        navToggle.addEventListener("click", function () {
            mobileNav.classList.toggle("open");
            navOverlay.classList.toggle("active");
        });

        closeNav.addEventListener("click", function () {
            mobileNav.classList.remove("open");
            navOverlay.classList.remove("active");
        });

        // Sluit het menu als een link wordt aangeklikt
        document.querySelectorAll(".nav-link").forEach(link => {
            link.addEventListener("click", function () {
                mobileNav.classList.remove("open");
                navOverlay.classList.remove("active");
            });
        });

    } else {
        console.error("🚨 Navigatie-elementen niet gevonden! Check de HTML.");
    }
});
