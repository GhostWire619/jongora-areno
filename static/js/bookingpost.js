
// Select all product containers


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






// showing booking form for areno bnb

function showBookForm() {
    const bookingformcont = document.querySelector('.bookingformcont')
    bookingformcont.style.display = 'flex'
}
function hideBookForm() {
    const bookingformcont = document.querySelector('.bookingformcont')
    bookingformcont.style.display = 'none'
}

function showQstnForm() {
    const questionformcont = document.querySelector('.questionformcont')
    questionformcont.style.display = 'flex'
}
function hideQstnForm() {
    const questionformcont = document.querySelector('.questionformcont')
    questionformcont.style.display = 'none'
}

// submit loader
function submitForm() {
    var loader = document.getElementById("loader");
    loader.style.display = "flex"; 
    return true; // Prevent the form from submitting automatically
  }

//preloader
window.onload = function(){
    var preloaderbg = document.getElementById('preloaderbg');
    preloaderbg.style.opacity = '0';
    preloaderbg.style.transition = '200ms';
    
    setTimeout(function() {
    preloaderbg.style.display = 'none';
  }, 200);
  };
