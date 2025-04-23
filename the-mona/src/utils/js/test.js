function updateMainHeight() {
    const navbar = document.getElementById("navbar");
    const main = document.getElementById("main-content");
  
    if (navbar && main) {
      const navHeight = navbar.offsetHeight;
      main.style.minHeight = `calc(100vh - ${navHeight}px)`;
    }
  }
  
  window.addEventListener("load", updateMainHeight);
  window.addEventListener("resize", updateMainHeight);
  