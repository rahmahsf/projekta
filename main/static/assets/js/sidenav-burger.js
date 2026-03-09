// sidenav transition-burger

document.addEventListener('DOMContentLoaded', function() {
  var sidenav = document.querySelector("aside");
  var sidenav_trigger = document.getElementById("hamburger-btn");
  var sidenav_close_button = document.querySelector("[sidenav-close]");
  
  // Check if elements exist
  if (!sidenav || !sidenav_trigger) {
    console.error('Sidenav elements not found');
    return;
  }
  
  console.log('Sidenav elements found:', { sidenav, sidenav_trigger, sidenav_close_button });

  sidenav_trigger.addEventListener("click", function () {
    console.log('Hamburger clicked');
    sidenav.classList.toggle("translate-x-0");
    sidenav.classList.toggle("shadow-soft-xl");
    
    if (sidenav_close_button) {
      sidenav_close_button.classList.toggle("hidden");
    }
  });
  
  if (sidenav_close_button) {
    sidenav_close_button.addEventListener("click", function () {
      sidenav_trigger.click();
    });
  }

  window.addEventListener("click", function (e) {
    if (!sidenav.contains(e.target) && !sidenav_trigger.contains(e.target)) {
      if (sidenav.classList.contains("translate-x-0")) {
        sidenav_trigger.click();
      }
    }
  });
});
