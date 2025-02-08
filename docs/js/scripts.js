document.addEventListener("DOMContentLoaded", function () {
    let navToggle = document.getElementById("navToggle");
    let closeNav = document.getElementById("closeNav");
    let mobileNav = document.getElementById("mobileNav");
    let navOverlay = document.getElementById("navOverlay");
    let navLinks = document.querySelectorAll(".nav-link");

    function closeMenu() {
        mobileNav.classList.remove("show");
        navOverlay.classList.remove("show");
    }

    navToggle.addEventListener("click", function () {
        mobileNav.classList.add("show");
        navOverlay.classList.add("show");
    });

    closeNav.addEventListener("click", closeMenu);
    navOverlay.addEventListener("click", closeMenu);

    // Sluit navigatie bij klikken op een menu-item
    navLinks.forEach(link => {
        link.addEventListener("click", closeMenu);
    });

    // Sluit menu als gebruiker buiten het menu klikt
    document.addEventListener("click", function (event) {
        if (!mobileNav.contains(event.target) && !navToggle.contains(event.target)) {
            closeMenu();
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    let sections = document.querySelectorAll(".full-section");

    function revealSections() {
        let scrollPosition = window.scrollY + window.innerHeight - 100;
        sections.forEach(section => {
            if (section.offsetTop < scrollPosition) {
                section.classList.add("show");
            }
        });
    }

    // Activeer de functie bij scrollen
    window.addEventListener("scroll", revealSections);
    revealSections(); // Direct uitvoeren bij laden van de pagina
});

