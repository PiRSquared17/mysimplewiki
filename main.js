/*
 * Client-side interaction for the pages of MyWiki, the simple wiki.
 *
 * Feel free to modify this file to suit your needs, especially if you edited
 * the page template.
 *
 */

(function () {
    "use strict";
    var searchBox = document.querySelectorAll("li.search")[0];
    searchBox.style.display = "none";
    var searchTrigger = document.querySelectorAll("a.search")[0];
    searchTrigger.onclick = function () {
        if (searchBox.style.display === "none") {
            searchBox.style.display = "block";
            searchTrigger.classList.add("active")
        }
        else {
            searchBox.style.display = "none";
            searchTrigger.classList.remove("active")
        }
    };
    var menuTrigger = document.querySelectorAll("nav div.menutrigger")[0];
    var menu = document.querySelectorAll("body > header nav ul")[0];
    if (window.innerWidth <= 900) {
        menu.style.display = "none";
    }
    menuTrigger.onclick = function () {
        if (menu.style.display === "none") {
            menu.style.display = "block";
        }
        else {
            menu.style.display = "none";
        }
    };
}());
