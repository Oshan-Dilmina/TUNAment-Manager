function showPopup(message) {
    document.getElementById('popupMessage').innerText = message.replaceAll("&#34;", '"');
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('popup').style.display = 'block';
}

function closePopup() {
    document.getElementById('overlay').style.display = 'none';
    document.getElementById('popup').style.display = 'none';
}

function showConfirmPopup(message) {
    document.getElementById('confirmMessage').innerText = message;
    document.getElementById('overlay').style.display = 'block';
    document.getElementById('confirmPopup').style.display = 'block';

    // Bind the resolve function to the confirmAction function
    window.confirmAction = function(result) {
        document.getElementById('overlay').style.display = 'none';
        document.getElementById('confirmPopup').style.display = 'none';
        return result; // Return the result
    };
}
