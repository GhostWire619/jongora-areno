


 // Get all ticket counter elements and calculate the amount of tickets
 const ticketCounters = document.querySelectorAll('.ticketcounter');

 ticketCounters.forEach(ticketCounter => {
   const plusButton = ticketCounter.nextElementSibling.querySelector('.ticketplus');
   const minusButton = ticketCounter.nextElementSibling.querySelector('.ticketminus');
 
   plusButton.addEventListener('click', () => {
     let currentAmount = parseInt(ticketCounter.textContent);
     currentAmount++;
     ticketCounter.textContent = currentAmount;
   });
 
   minusButton.addEventListener('click', () => {
     let currentAmount = parseInt(ticketCounter.textContent);
     currentAmount = Math.max(currentAmount - 1, 0);
     ticketCounter.textContent = currentAmount;
   });
 });

 function calculate() {
    // Get all sets
    const sets = document.querySelectorAll('.set');
    
    sets.forEach(set => {
      const dynamicNumber = parseInt(set.querySelector('.dynamicNumber').textContent);
      const staticNumber = parseInt(set.querySelector('.staticNumber').textContent);
      
      // Calculate the product
      const product = dynamicNumber * staticNumber;
      
      set.querySelector('.amount').value = product;
    });
  }
  
  calculate();
  
  document.querySelectorAll('.dynamicNumber').forEach(span => {
    span.addEventListener('DOMSubtreeModified', calculate);
  });
 

//calculate the total price per ticket value

const inputA = document.getElementById('a');
const inputB = document.getElementById('b');
const inputC = document.getElementById('c');
const output = document.getElementById('result');

// Function to update the output based on the values of input fields
function updateOutput() {
  // Get the values from the input fields and convert them to integers
  const valueA = inputA ? parseInt(inputA.value) || 0 : 0;
  const valueB = inputB ? parseInt(inputB.value) || 0 : 0;
  const valueC = inputC ? parseInt(inputC.value) || 0 : 0; 
  
  // Calculate the sum of the values
  var sum = valueA + valueB + valueC;
  
  // Update the output with the calculated sum
  output.textContent = sum;
}

// Call the updateOutput function initially to set the initial value
updateOutput();

// Add event listeners to input fields to update the output whenever their values change
inputA.addEventListener('input', updateOutput);
inputB.addEventListener('input', updateOutput);
inputC.addEventListener('input', updateOutput);

// Simulate dynamic changes
// For example, change the values of input fields programmatically
const interval = 10; // 5 seconds in milliseconds
setInterval(updateOutput, interval);


