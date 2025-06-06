//reviews slider
const reviewssplide = new Splide( '#reviews', {
    perPage: 2,
    gap : '1rem',
    drag : 'free',
    arrows: true,
    perMove: 1,
    padding: { left: 0, right: 0 },
    snap: true,
    type: 'loop',
    pagination: true,
    autoplay: true,
    breakpoints: {
  
      
      1200: {
      perPage: 1,
      padding: { left: 0, right: 120 },
      },
      1104: {
      perPage: 1,
      padding: { left: 0, right: 100 },
      },
      964: {
      perPage: 1,
      padding: { left: 0, right: 90 },
      },
      884: {
      perPage: 1,
      padding: { left: 0, right: 50 },
      },
      764: {
      perPage: 1,
      padding: { left: 30, right: 30 },
      },
      678: {
        perPage: 1,
        padding: { left: 30, right: 30 },
      },
      610: {
        perPage: 1,
        padding: { left: 30, right: 30 },
      },
      580: {
        perPage: 1,
        padding: { left: 30, right: 30 },
      },
      520: {
        perPage: 1,
        padding: { left: 30, right: 30 },
      },
      470: {
        perPage: 1,
        padding: { left: 20, right: 20 },
      },
      440: {
        perPage: 1,
        padding: { left: 20, right: 20 },
      },
      390: {
        perPage: 1,
        padding: { left: 20, right: 20 },
      },
      335: {
        perPage: 1,
        padding: { left: 20, right: 20 },
      },
      },
    } );
    reviewssplide.mount()
  
  

    // Get all elements with the class 'number'
const numberDivs = document.querySelectorAll('.number');

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

//displaying stars per average

const averagestars = document.getElementById('stars');
const averageresult = document.getElementById('average');

const averageValue = parseFloat(averageresult.textContent); // Convert text content to a number

if (averageValue < 2) {
  averagestars.textContent = '★☆☆☆☆';
} else if (averageValue >= 2 && averageValue < 3) {
  averagestars.textContent = '★★☆☆☆';
} else if (averageValue >= 3 && averageValue < 4) {
  averagestars.textContent = '★★★☆☆';
} else if (averageValue >= 4 && averageValue < 4.5) {
  averagestars.textContent = '★★★★☆';
} else if (averageValue >= 4.5) {
  averagestars.textContent = '★★★★★';
}

averagestars.style.color = 'gold';
averagestars.style.fontSize = '40px';

//hidding details upon submitting

const reviewsubmitbtn = document.querySelector('.reviewsubmitbtn');
const reviewform = document.querySelector('.review-form');


reviewsubmitbtn.addEventListener('DOMContentLoaded', function() {
  // Show an alert when the page finishes loading
  alert('Thank You For Your Feedback, We will review it shortly!');
  
  // Hide the form after the alert is dismissed
  document.getElementById('myForm').style.display = 'none';
});


// Get the modal element and the button that opens it
const modal = document.getElementById('myModal');
const btn = document.getElementById('openModalBtn');
const span = document.getElementsByClassName('close')[0];

// Open the modal when the button is clicked
btn.onclick = function() {
  modal.style.display = 'block';
}

// Close the modal when the user clicks on the 'x' (close) button
span.onclick = function() {
  modal.style.display = 'none';
}

// Close the modal when the user clicks anywhere outside of the modal content
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = 'none';
  }
}

function submitForm() {
  var loader = document.getElementById("loader");
  loader.style.display = "flex"; 
  return true; // Prevent the form from submitting automatically
}





