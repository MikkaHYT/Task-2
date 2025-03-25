document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        var flash = document.getElementById("flash");
        if (flash) {
            flash.style.transition = "opacity 0.75s ease-out";
            flash.style.opacity = "0";
            setTimeout(function() {
                flash.style.display = "none";
            }, 500);
        }
    }, 2250);
});