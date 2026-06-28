(function ($) {
    "use strict";




// hamburger menu
jQuery(document).ready(function () {
	jQuery('header .mainmenu').meanmenu({
    meanScreenWidth: "992",
  });
});


document.querySelectorAll('.menu-anim > li > a').forEach(button => button.innerHTML = '<div class="menu-text"><span>' + button.textContent.split('').join('</span><span>') + '</span></div>');

setTimeout(() => {
  var menu_text = document.querySelectorAll(".menu-text span")
  menu_text.forEach((item) => {
    var font_sizes = window.getComputedStyle(item, null);
    let font_size = font_sizes.getPropertyValue("font-size");
    let size_in_number = parseInt(font_size.replace("px", ""));
    let new_size = parseInt(size_in_number / 3)
    new_size = new_size + "px"
    if (item.innerHTML == " ") {
      item.style.width = new_size
    }
  })
}, 1000)
// hamburger menu End


// Search Start
document.addEventListener("click", (event) => {
  const searchToggle = event.target.closest(".search-icon");
  if (searchToggle) {
    searchToggle.classList.toggle("active");
  }
});
// Search End





}(jQuery)); 