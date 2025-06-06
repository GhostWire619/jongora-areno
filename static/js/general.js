 //categories slider
 const mealssplide = new Splide( '#meals-splide', {
    perPage: 10,
    gap : '1rem',
    drag : 'free',
    perMove: 1,
    padding: '0px 10px',
    snap: true,
    type: 'loop',
    pagination: false,
    autoplay: true,
    arrows: false,
    breakpoints: {
      1190: {
        perPage: 9,
        gap : '10px',
        padding: '20px',
      },
      1064: {
        perPage: 8,
        padding: '0px',
      },
      964: {
        perPage: 7,
      },
      864: {
        perPage: 6,
      },
      764: {
        perPage: 5,
        padding: { left: 0, right: 180 },
      },
      664: {
        perPage: 5,
        padding: { left: 0, right: 80 },
      },
      584: {
        perPage: 5,
        padding: { left: 0, right: 40 },
      },
      510: {
        perPage: 5,
        padding: { left: 0, right: 0 },
      },
      450: {
      perPage: 4,
      padding: { left: 0, right: 20 },
      
      },
      360: {
        perPage: 3,
        
        },
    },
    } );
    mealssplide.mount()
  

 


function showfollowbtn (followbtn) {
  const followBtn = document.getElementById(followbtn)
  if(followBtn.style.display !== 'flex'){
    followBtn.style.display= 'flex';
    followBtn.style.opacity = '1';
  } else {
    followBtn.style.display= 'none';
  followBtn.style.opacity = '0';
  }
  
}

function showpostdescr (postId) {
  const postdescr = document.getElementById(postId)
  
  if (postdescr.style.height !== 'auto') {
    postdescr.style.height = 'auto';
    postdescr.style.transition = 'all 200ms';
  } else {
    postdescr.style.height = '20px';
    postdescr.style.transition = 'all 200ms';
  }
}

//loading more 
  
function loadMorePosts() {
  let currentItem = 15;
  const button = document.getElementById('loadMoreButton');
  const productboxes = [...document.querySelectorAll('.productpost')];

  function showMore() {
    for (let i = currentItem; i < currentItem + 15 && i < productboxes.length; i++) {
      productboxes[i].style.display = 'flex';
    }
    currentItem += 15;

    if (currentItem >= productboxes.length) {
      button.style.display = 'none';
    }
  }

  button.onclick = showMore;

  // Initially show the first two items
  showMore();
}
loadMorePosts();






//share button API for general posts url

function copyAndShare(url_link) {
  // Get the current webpage URL
  const currentUrl = url_link;
 
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


















