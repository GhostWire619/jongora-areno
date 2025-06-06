

// displaying rats for seller
function showRateForm() {
    const userrateform = document.querySelector('.userrateform')
    userrateform.style.display = 'flex'
  }
  function hideRateForm() {
    const userrateform = document.querySelector('.userrateform')
    userrateform.style.display = 'none'
  }
  
  //displaying average rates
    // Get all elements with the class 'number'
    const numberDivs = document.querySelectorAll('.userrate');
  
    // Calculate the sum of all values
    let sum = 0;
    numberDivs.forEach(div => {
      sum += parseInt(div.getAttribute('data-value'));
    });
    
    // Calculate the average
    const average = sum / numberDivs.length;
    
    // Display the average on the HTML page
    const averageDisplay = document.getElementById('average');
    averageDisplay.textContent = isNaN(average) ? 'N/A' : average.toFixed(1); // Display 'N/A' if no numbers are present
      