//code for changing language
const englishBtn = document.getElementById('englishBtn');
const swahiliBtn = document.getElementById('swahiliBtn');
const elementsToTranslate = document.querySelectorAll('.translate');

// Function to set language
function setLanguage(language) {
  elementsToTranslate.forEach(element => {
    if (language === 'english') {
      element.textContent = element.getAttribute('data-en');
      englishBtn.style.backgroundColor = 'black'
      englishBtn.style.color = 'orangered'
      swahiliBtn.style.backgroundColor = 'rgba(209, 205, 205, 0.466)'
      swahiliBtn.style.color = 'black'
    } else if (language === 'swahili') {
      element.textContent = element.getAttribute('data-sw');
      englishBtn.style.backgroundColor = 'rgba(209, 205, 205, 0.466)'
      englishBtn.style.color = 'black'
      swahiliBtn.style.backgroundColor = 'black'
      swahiliBtn.style.color = 'orangered'
    }
  });

  // Store selected language in local storage
  localStorage.setItem('selectedLanguage', language);
}

// Check if language is stored in local storage and apply
const storedLanguage = localStorage.getItem('selectedLanguage');
if (storedLanguage) {
  setLanguage(storedLanguage);
}

// Event listeners for language buttons
englishBtn.addEventListener('click', () => {
  setLanguage('english');
});

swahiliBtn.addEventListener('click', () => {
  setLanguage('swahili');
});

  



//expanding notification div
  // Get all buttons with the class '.notification-menu'
  const notificationMenuButtons = document.querySelectorAll('.mobile-notification');
  const notificationMenuDiv = document.querySelector('.notificationdiv');
  
  // Loop through each button and attach event listeners
  notificationMenuButtons.forEach(button => {
    button.addEventListener('click', () => {
      notificationMenuDiv.style.display = 'flex';
    });
  });
  
  // Add event listener to close the notification when clicking outside
  const notificationDarkSide = document.querySelector('.notificationdarkside');
  const notyclose = document.querySelector('.noty-close');
  notificationDarkSide.addEventListener('click', () => {
    notificationMenuDiv.style.display = 'none';
  });
  notyclose.addEventListener('click', () => {
    notificationMenuDiv.style.display = 'none';
  });









