document.addEventListener("DOMContentLoaded", function () {
    let hasScrolled = false;
    let navbar = document.getElementById("navbar");
    let mobileNav = document.getElementById("mobileNav");
    let navToggle = document.getElementById("navToggle");

    // 🔹 Navbar effect bij scrollen
    window.addEventListener("scroll", function () {
        let scrollPosition = window.scrollY;

        // Navbar tonen/verbergen afhankelijk van scrollpositie
        if (scrollPosition > 50) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }

        // Automatische scroll naar "Story" bij eerste kleine scroll
        if (!hasScrolled && scrollPosition > 10) {
            hasScrolled = true;
            let storySection = document.getElementById("story");
            if (storySection) {
                setTimeout(() => {
                    storySection.scrollIntoView({ behavior: "smooth" });
                }, 150);
            }
        }
    });

    // 🔹 Openen en sluiten van het mobiele menu
    navToggle.addEventListener("click", function () {
        mobileNav.classList.toggle("show");

        // Voorkomen dat de pagina scrollt wanneer menu open is
        if (mobileNav.classList.contains("show")) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "";
        }
    });

    // 🔹 Sluit het menu als je ergens anders klikt
    document.addEventListener("click", function (event) {
        if (!mobileNav.contains(event.target) && !navToggle.contains(event.target)) {
            mobileNav.classList.remove("show");
            document.body.style.overflow = "";
        }
    });

    // 🔹 Smooth scroll naar secties en sluit menu na klik
    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            let targetId = this.getAttribute("href"); // Gebruik href in plaats van data-target
            let targetSection = document.querySelector(targetId);

            if (targetSection) {
                targetSection.scrollIntoView({ behavior: "smooth" });
            }

            // Menu sluiten na klikken
            mobileNav.classList.remove("show");
            document.body.style.overflow = "";
        });
    });
});
