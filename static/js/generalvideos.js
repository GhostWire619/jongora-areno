document.addEventListener("DOMContentLoaded", function() {
    const videos = document.querySelectorAll('.videoPlayer');

    // Function to toggle fullscreen mode
    function toggleFullScreen (video) {
        if (!document.fullscreenElement) {
            video.requestFullscreen().catch(err => {
                console.log(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`);
            });
        } else {
            document.exitFullscreen();
        }
    };

    

    // Intersection Observer callback
    const callback = (entries, observer) => {
        entries.forEach(entry => {
            const video = entry.target;
            if (entry.isIntersecting) {
                video.play();
            } else {
                video.pause();
            }
        });
    };

    const observer = new IntersectionObserver(callback, { threshold: 0.5 });

    videos.forEach(video => {
        observer.observe(video);

        function handleClick () {
            if (video.paused) {
                video.play();
            } else {
                video.pause();
            }
        };

        // Add event listeners for play/pause and fullscreen toggle
        video.addEventListener('click', handleClick());
        video.addEventListener('touchend', handleClick());// Changed 'touchdown' to 'touchend'
        video.addEventListener('dblclick', toggleFullScreen(video));
    
       

    });

    

    

});

document.addEventListener("DOMContentLoaded", function() {
    const videos = document.querySelectorAll('video[data-src]');

    // Function to load video source
    const loadVideo = (video) => {
        if (!video.src) {
            video.src = video.getAttribute('data-src');
        }
    };

    // Intersection Observer callback
    const videoObserverCallback = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadVideo(entry.target);
                observer.unobserve(entry.target);
            }
        });
    };

    // Create an Intersection Observer
    const videoObserver = new IntersectionObserver(videoObserverCallback, {
        root: null,
        rootMargin: '0px',
        threshold: 0.25 // Adjust this value as needed
    });

    // Observe each video
    videos.forEach(video => {
        videoObserver.observe(video);
    });

    // Load video on user interaction
    videos.forEach(video => {
        video.addEventListener('click', () => loadVideo(video), { once: true });
        video.addEventListener('mouseover', () => loadVideo(video), { once: true });
    });
});














