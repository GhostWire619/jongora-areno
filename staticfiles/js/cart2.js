   



    //  to add and minus cart quantity
    // Get all the plus buttons
  const plusButtons = document.querySelectorAll('.plus-button');
  
  // Get all the minus buttons
  const minusButtons = document.querySelectorAll('.minus-button');
  
  // Iterate over plus buttons and attach event listeners
  plusButtons.forEach((button) => {
  button.addEventListener('click', () => {
    // Get the corresponding input field
    const inputField = button.parentElement.querySelector('.quantity-input');
    
    // Get the current value of the input field
    let value = parseInt(inputField.value);
    
    // Increment the value by 1
    value++;
    
    // Update the value of the input field
    inputField.value = value;
  });
  });
  
  // Iterate over minus buttons and attach event listeners
  minusButtons.forEach((button) => {
  button.addEventListener('click', () => {
    // Get the corresponding input field
    const inputField = button.parentElement.querySelector('.quantity-input');
    
    // Get the current value of the input field
    let value = parseInt(inputField.value);
    
    // Decrement the value by 1 if greater than 0
    if (value > 0) {
        value--;
    }
    
    // Update the value of the input field
    inputField.value = value;
  });
  });
    