// Select all product containers
const productContainers = document.querySelectorAll('.product-container');

// Loop through each product container
productContainers.forEach(container => {
  // Select buttons and input fields within the current container
  const buttons = container.querySelectorAll('.more, .less');
  const cartamounts = container.querySelectorAll('.cartamount');

  // Loop through each cartamount input field
  cartamounts.forEach(cartamount => {
    let counter = parseInt(cartamount.value) || 1; // Initialize counter with input field value or 1 if empty

    // Function to update the counter and display it in the <input> element
    function updateCounter() {
      cartamount.value = counter;
    }

    // Function to handle button clicks
    function buttonClick(event) {
      if (event.target.classList.contains('more')) {
        counter++;
      } else if (event.target.classList.contains('less')) {
        if (counter > 1) {
          counter--;
        }
      }
      updateCounter();
    }

    // Attach event listeners to buttons within the current container
    buttons.forEach(button => {
      button.addEventListener('click', buttonClick);
    });

    // Initial counter display
    updateCounter();
  });
});

// JavaScript to handle full-screen image display
const thumbnails = document.querySelectorAll('.thumbnail');
const fullscreenImageContainer = document.getElementById('fullscreen-image-container');
const fullscreenImage = document.getElementById('fullscreen-image');

thumbnails.forEach(thumbnail => {
thumbnail.addEventListener('click', () => {
    fullscreenImage.src = thumbnail.src;
    fullscreenImageContainer.style.display = 'block';
});
});

fullscreenImageContainer.addEventListener('click', () => {
fullscreenImageContainer.style.display = 'none';
});


//item images slider
const itemimagesslider = new Splide( '#itemimagesslider', {
    perPage: 1,
    drag : 'free',
    perMove: 1,
    padding: 0,
    snap: true,
    type: 'loop',
    rewind: true,
    arrows: true,
    interval: 25000,
    pagination: true,
    autoplay: true,
    breakpoints: {
      1200: {
      perPage: 1,
      },
      
      764: {
      perPage: 1,
      }, 
      678: {
        perPage: 1,
      },
      610: {
        perPage: 1,
      },
      580: {
        perPage: 1,
      },
      
      },
    } );
    itemimagesslider.mount()

       //fifth slider
const relatedproducts = new Splide( '#relatedproducts', {
  perPage: 4,
  gap : '1rem',
  drag : 'free',
  perMove: 1,
  padding: { left: 0, right: 80 },
  snap: true,
  type: 'loop',
  pagination: false,
  autoplay: false,
  breakpoints: {

    1200: {
    perPage: 4,
    padding: { left: 0, right: 20 },
    },
    1104: {
    perPage: 3,
    padding: { left: 0, right: 100 },
    },
    964: {
    perPage: 3,
    padding: { left: 0, right: 50 },
    },
    884: {
    perPage: 2,
    padding: { left: 0, right: 180 },
    },
    764: {
    perPage: 3,
    padding: { left: 0, right: 20 },
    },
    678: {
      perPage: 2,
      padding: { left: 0, right: 170 },
    },
    610: {
      perPage: 2,
      padding: { left: 0, right: 130 },
    },
    580: {
      perPage: 2,
      padding: { left: 0, right: 80 },
    },
    520: {
      perPage: 2,
      padding: { left: 0, right: 30 },
    },
    470: {
      perPage: 2,
      padding: { left: 0, right: 0 },
    },
    440: {
      perPage: 1,
      padding: { left: 0, right: 170 },
    },
    390: {
      perPage: 1,
      padding: { left: 0, right: 120 },
    },
    335: {
      perPage: 1,
      padding: { left: 0, right: 50 },
    },
    },
  } );
  relatedproducts.mount()



//share button API

function copyAndShare() {
  // Get the current webpage URL
  const currentUrl = window.location.href;

  // Copy the URL to the clipboard
  navigator.clipboard.writeText(currentUrl)
    .then(() => {
      console.log('URL copied to clipboard:', currentUrl);
      // Check if the share API is available
      if (navigator.share) {
        // Share the URL
        navigator.share({
          title: 'Share URL',
          url: currentUrl
        })
        .then(() => console.log('URL shared successfully'))
        .catch((error) => console.error('Error sharing URL:', error));
      } else {
        // If share API is not available, notify the user
        alert('Share API not supported in this browser');
      }
    })
    .catch((error) => {
      console.error('Error copying to clipboard:', error);
      alert('Failed to copy URL to clipboard');
    });
}

// Get the video element
const video = document.getElementById('videoPlayer');

// Function to toggle fullscreen mode
function toggleFullScreen() {
    if (!document.fullscreenElement) {
        video.requestFullscreen().catch(err => {
            console.log(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
        });
    } else {
        document.exitFullscreen();
    }
}

// Function to handle click event on the video
function handleClick() {
    if (video.paused) {
        video.play();
    } else {
        video.pause();
    }
}

// Add click event listeners
video.addEventListener('click', handleClick);
video.addEventListener('dblclick', toggleFullScreen);






