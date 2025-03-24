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

    if (navToggle && closeNav && mobileNav && navOverlay) {
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
    }
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

    window.addEventListener("scroll", revealSections);
    revealSections();
});

document.addEventListener("DOMContentLoaded", function () {
    let sections = document.querySelectorAll(".full-section");
    let navLinks = document.querySelectorAll(".nav-link");

    function markActiveSection() {
        let scrollY = window.scrollY + window.innerHeight / 2;
        let activeSection = null;

        sections.forEach(section => {
            let sectionTop = section.offsetTop;
            let sectionHeight = section.offsetHeight;

            if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
                activeSection = section.id;
            }
        });

        navLinks.forEach(link => {
            let targetId = link.getAttribute("href").replace("#", "");
            if (targetId === activeSection) {
                link.classList.add("active");
            } else {
                link.classList.remove("active");
            }
        });
    }

    function revealSections() {
        let scrollPosition = window.scrollY + window.innerHeight - 100;
        sections.forEach(section => {
            if (section.offsetTop < scrollPosition) {
                section.classList.add("show");
            }
        });
    }

    window.addEventListener("scroll", () => {
        revealSections();
        markActiveSection();
    });

    revealSections();
    markActiveSection();
});

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener("click", function (e) {
            let target = this.getAttribute("href");

            if (!target.startsWith("#")) {
                return;
            }

            e.preventDefault();
            let targetId = target.substring(1);
            let targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    function updateScrollMargin() {
        let navbarHeight = document.querySelector(".navbar").offsetHeight;
        document.documentElement.style.setProperty('--navbar-height', `${navbarHeight}px`);
    }

    updateScrollMargin();
    window.addEventListener("resize", updateScrollMargin);
});
