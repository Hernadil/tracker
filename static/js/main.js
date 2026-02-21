// Tracker App - Main JS
document.addEventListener('DOMContentLoaded', function() {
  var alerts = document.querySelectorAll('.alert');
  alerts.forEach(function(alert) {
    setTimeout(function() {
      alert.style.transition = 'opacity 0.4s';
      alert.style.opacity = '0';
      setTimeout(function() { if (alert.parentNode) alert.parentNode.removeChild(alert); }, 400);
    }, 4000);
  });
});
