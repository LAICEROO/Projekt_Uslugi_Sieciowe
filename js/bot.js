var kommunicateSettings = {
  "appId": "2f10426634de874c7b3ca6a55e4c6d8f7",
  "popupWidget": true,
  "automaticChatOpenOnNavigation": false
};

(function(d, m) {
  var s = document.createElement("script");
  s.type = "text/javascript";
  s.async = true;
  s.src = "https://widget.kommunicate.io/v2/kommunicate.app";
  var h = document.getElementsByTagName("head")[0];
  h.appendChild(s);
  window.kommunicate = m;
  m._globals = kommunicateSettings;
})(document, window.kommunicate || {});

document.addEventListener('DOMContentLoaded', function() {
  var bookNowButtons = document.querySelectorAll('#book-now');
  bookNowButtons.forEach(function(button) {
      button.addEventListener('click', function(event) {
          event.preventDefault();
          if (window.kommunicate && window.kommunicate.launchConversation) {
              window.kommunicate.launchConversation();
          } else {
              console.error('Kommunicate is not loaded yet');
          }
      });
  });
});
