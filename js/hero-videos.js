document.addEventListener('DOMContentLoaded', () => {
  const videos = document.querySelectorAll('.hero-video');
  if (videos.length <= 1) return;

  let currentIndex = 0;
  
  // Initialize first video
  videos[currentIndex].classList.add('active');

  // Cycle every 6 seconds
  setInterval(() => {
    videos[currentIndex].classList.remove('active');
    
    currentIndex = (currentIndex + 1) % videos.length;
    
    videos[currentIndex].classList.add('active');
  }, 6000);
});
