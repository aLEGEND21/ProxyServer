// Loads the target page when the submit button is clicked
function loadTargetPage () {
    let targetPageURL = document.getElementById("url-input").value;
    // Add http to the beginning of the target page if it is not there
    if (!targetPageURL.startsWith("http://") || !targetPageURL.startsWith("https://")) {
        targetPageURL = `http://${targetPageURL}`;
    }
    location.href = `${location.protocol}//${location.host}/${targetPageURL}`;
}

// Also trigger the loading of the target page when the user clicks enter
document.addEventListener("keyup", function (event) {
    if (event.key == "Enter") {
        loadTargetPage();
    }
});