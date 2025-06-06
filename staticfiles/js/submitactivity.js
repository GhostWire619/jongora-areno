function submitForm() {
    var loader = document.getElementById("loader");
    loader.style.display = "flex"; 
    return true; // Prevent the form from submitting automatically
}

const fileInput = document.getElementById('fileInput');
const fileText = document.getElementById('fileText');
const fileInput2 = document.getElementById('fileInput2');
const fileText2 = document.getElementById('fileText2');
const fileInput3 = document.getElementById('fileInput3');
const fileText3 = document.getElementById('fileText3');
const fileInput4 = document.getElementById('fileInput4');
const fileText4 = document.getElementById('fileText4');

fileInput.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        fileText.textContent = file.name;
    } else {
        fileText.textContent = 'drag and drop your file here or click to select a file!';
    }
});
fileInput2.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        fileText2.textContent = file.name;
    } else {
        fileText2.textContent = 'drag and drop your file here or click to select a file!';
    }
});
fileInput3.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        fileText3.textContent = file.name;
    } else {
        fileText3.textContent = 'drag and drop your file here or click to select a file!';
    }
});
fileInput4.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        fileText4.textContent = file.name;
    } else {
        fileText4.textContent = 'drag and drop your file here or click to select a file!';
    }
});