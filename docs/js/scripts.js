document.addEventListener("DOMContentLoaded", function () {
    let hasScrolled = false;
    let navbar = document.getElementById("navbar");
    let mobileNav = document.getElementById("mobileNav");

    window.addEventListener("scroll", function () {
        let scrollPosition = window.scrollY;

        if (scrollPosition > 50) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }

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

    document.getElementById("navToggle").addEventListener("click", function () {
        mobileNav.classList.toggle("show");
    });

    document.querySelectorAll(".nav-link").forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            let targetId = this.getAttribute("data-target"); // Gebruik data-target i.p.v. href
            let targetSection = document.querySelector(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: "smooth" });
            }
            mobileNav.classList.remove("show");
        });
    });
    
});
