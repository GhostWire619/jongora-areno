//preloader
document.addEventListener('DOMContentLoaded', function () {
  const preloaderbg = document.getElementById('preloaderbg');

  if (preloaderbg) {
      // Add a smooth transition for opacity
      preloaderbg.style.transition = 'opacity 200ms';
      preloaderbg.style.opacity = '0';

      setTimeout(() => {
          preloaderbg.style.display = 'none';
      }, 200); // Matches the transition duration
  }
});
