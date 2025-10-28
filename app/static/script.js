// static/script.js
$(document).ready(function() {
  // Montrer le flux vidéo de Camera1
  $('#camera1').click(function() {
    $.post('/cliquer_bouton', { button: 'camera1' }, function(response) {
      if (response.url) {
        $('#video_camera1').attr('src', response.url);
      } else {
        alert('Erreur : Aucun flux disponible pour la caméra 1.');
      }
    });
  });

 
});


document.getElementById('camera-form').addEventListener('submit', function(event) {
  event.preventDefault();

  const camera1Url = document.getElementById('cam1').value;


  if (camera1Url) {
    console.log('Camera 1 URL:', camera1Url);
  

    gestion_source(camera1Url);
    alert('Source envoyée avec succès.');
  } else {
    alert('Veuillez entrer les URLs pour les deux caméras.');
  }
});

function gestion_source(url1) {
  fetch('/recuperer_source', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },

    body: JSON.stringify({ camera1_url: url1})
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      alert('Erreur: ' + data.error);
    } else {
      console.log('Success:', data);
    }
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}
