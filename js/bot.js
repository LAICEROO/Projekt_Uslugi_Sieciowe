// Kommunicate settings configuration
var kommunicateSettings = {
  "appId": "2f10426634de874c7b3ca6a55e4c6d8f7", // Kommunicate app ID
  "popupWidget": true, // Enable popup widget
  "automaticChatOpenOnNavigation": false // Disable automatic chat open on navigation
};

// Self-invoking function to load the Kommunicate script
(function(d, m) {
  // Create a new script element
  var s = document.createElement("script");
  s.type = "text/javascript"; // Set the type to JavaScript
  s.async = true; // Load script asynchronously
  s.src = "https://widget.kommunicate.io/v2/kommunicate.app"; // Set the source URL for the Kommunicate script

  // Append the script to the head of the document
  var h = document.getElementsByTagName("head")[0];
  h.appendChild(s);

  // Set the global kommunicate object
  window.kommunicate = m;
  m._globals = kommunicateSettings; // Assign settings to the global kommunicate object
})(document, window.kommunicate || {}); // Pass the document and existing kommunicate object or an empty object

// Event listener for DOM content loaded
document.addEventListener('DOMContentLoaded', function() {
  // Select all elements with the ID 'book-now'
  var bookNowButtons = document.querySelectorAll('#book-now');

  // Add a click event listener to each 'book-now' button
  bookNowButtons.forEach(function(button) {
      button.addEventListener('click', function(event) {
          event.preventDefault(); // Prevent the default action of the button

          // Check if the Kommunicate object and its method 'launchConversation' are available
          if (window.kommunicate && window.kommunicate.launchConversation) {
              window.kommunicate.launchConversation(); // Launch the conversation
          } else {
              console.error('Kommunicate is not loaded yet'); // Log an error if Kommunicate is not ready
          }
      });
  });
});
