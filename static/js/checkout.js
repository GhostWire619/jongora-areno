

// Function to perform subtraction and display result
function subtractNumbers() {
    // Get the values from the p elements
    var num1 = parseFloat(document.getElementById("num1").textContent);
    var num2 = parseFloat(document.getElementById("num2").textContent);
    
    // Subtract the second number from the first number
    var result = num1 - num2;
    
    // Display the result in the result p element
    document.getElementById("result").textContent = result;
}

// Call subtractNumbers function initially
subtractNumbers();

// Add event listener for changes in content of num1 and num2 p elements
document.getElementById("num1").addEventListener("input", subtractNumbers);
document.getElementById("num2").addEventListener("input", subtractNumbers);