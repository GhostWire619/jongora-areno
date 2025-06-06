


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

  //posting div
  
  window.addEventListener('click', function(event) {
  const modal = document.getElementById('myModal');
    if (event.target === modal) {
      modal.style.display = 'none';
    }
  });

  function showPostModal() {
    const modal = document.getElementById('myModal');
    modal.style.display = 'flex';
  }
  function closePostModal() {
    const modal = document.getElementById('myModal');
    modal.style.display = 'none';
  }


  //settings profile image preview
  function displayImage() {
    const input = document.getElementById('image-input');
    const preview = document.getElementById('image-preview');
    const container = document.getElementById('image-container');

    const file = input.files[0];
 
    if (file) {
      const reader = new FileReader();

      reader.onload = function (e) {
        preview.src = e.target.result;
        container.style.display = 'block';
      };

      reader.readAsDataURL(file);
    } else {
      // Clear the image preview if no file is selected
      preview.src = '';
      container.style.display = 'none';
    }
  }

function formatNumber(num) {
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + 'B';
    } else if (num >= 1000000) {
        return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    }
    return num.toString();
}

document.addEventListener("DOMContentLoaded", function() {
    const numberElements = document.querySelectorAll('.number');
    numberElements.forEach(element => {
        const originalNumber = parseInt(element.innerText, 10);
        const formattedNumber = formatNumber(originalNumber);
        element.innerText = formattedNumber;
    }); 
});

function submitForm() {
  var loader = document.getElementById("loader");
  loader.style.display = "flex"; 
  return true; // Prevent the form from submitting automatically
}

// code to delete a post
function confirmDelete(name) {
  const confirmation = confirm(`Are You sure You Want to delete This Post: ${name} ?`);
  if (confirmation) {
      return true; // Proceed with form submission
  } else {
      return false; // Cancel form submission
  }
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


function confirmuserdelete() {
  const deleteuserconfirmdiv = document.getElementById('deleteuserconfirmdiv')
  deleteuserconfirmdiv.style.display = 'flex';
}
function closeuserdelete() {
  var deleteuserconfirmdiv = document.getElementById('deleteuserconfirmdiv')
  deleteuserconfirmdiv.style.display = 'none';
}




//limiting user to upload a video less than 5mb
// Get the file input and form elements
const videoInput = document.getElementById('videoInput');
const uploadForm = document.getElementById('uploadForm');

videoInput.addEventListener('change', function() {
  // Check if a file is selected
  if (videoInput.files.length > 0) {
    // Get the selected file
    const videoFile = videoInput.files[0];

    // Check the file size (5MB = 5 * 1024 * 1024 bytes)
    const maxSize = 5 * 1024 * 1024;
    if (videoFile.size > maxSize) {
      // Alert the user
      alert('The video file is too large. Please select a file smaller than 5MB.');
      // Clear the file input
      videoInput.value = '';
    }
  }
});

// Prevent form submission if the file is too large
uploadForm.addEventListener('submit', function(event) {
  if (videoInput.files.length > 0 && videoInput.files[0].size > maxSize) {
    event.preventDefault();
    alert('The video file is too large. Please select a file smaller than 5MB.');
  }
});
