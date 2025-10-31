// static/script.js


// Rôle / description par défaut selon la classe détectée
const AIRCRAFT_INFO = {
  A10:  { type: "Attack aircraft",   role: "CAS / anti-char",     origin: "USA",
          desc: "L’A-10 est spécialisé dans l’appui rapproché, robuste et précis à basse altitude." },
  B1:   { type: "Bomber",            role: "Bombardement supersonique", origin: "USA",
          desc: "Le B-1 est un bombardier à grande vitesse et longue portée." },
  B52:  { type: "Bomber",            role: "Bombardement stratégique",  origin: "USA",
          desc: "Le B-52 offre une portée et une charge utile stratégiques." },
  C130: { type: "Transport",         role: "Transport tactique",   origin: "USA",
          desc: "Le C-130 assure transport, aéro-largage et évacuation sanitaire." },
  C5:   { type: "Transport",         role: "Transport stratégique",origin: "USA",
          desc: "Le C-5 Galaxy transporte du fret très volumineux sur longue distance." },
  F117: { type: "Stealth",           role: "Attaque furtive",      origin: "USA",
          desc: "Le F-117 fut l’un des premiers appareils furtifs opérationnels." },
  F15:  { type: "Fighter",           role: "Supériorité aérienne", origin: "USA",
          desc: "Le F-15 combine vitesse, manœuvrabilité et charge utile importante." },
  F22:  { type: "Stealth Fighter",   role: "Supériorité aérienne", origin: "USA",
          desc: "Le F-22 associe furtivité, capteurs avancés et super-croisière." },
  MQ9:  { type: "UAV",               role: "ISR / frappe",         origin: "USA",
          desc: "Le MQ-9 est un drone MALE pour renseignement et frappe de précision." },
  Tu160:{ type: "Bomber",            role: "Bombardement stratégique",  origin: "Russie",
          desc: "Le Tu-160 est un bombardier supersonique à aile variable." },
  aircraft: { type: "Aircraft", role: "Générique", origin: "—",
          desc: "Aéronef détecté (classe générique). Affinez l’identification." },
  jet:      { type: "Jet",      role: "Générique", origin: "—",
          desc: "Jet détecté (classe générique). Affinez l’identification." }
};

function infoFor(cls) {
  return AIRCRAFT_INFO[cls] || {
    type: "Aircraft", role: "—", origin: "—",
    desc: "Aéronef détecté. Informations détaillées non disponibles pour cette classe."
  };
}
let lastSeenClass = null;

async function refreshDetection() {
  try {
    const r = await fetch('/last_detection');
    const d = await r.json();

    if (!d || !d.class) return; // rien à afficher

    // Évite de réécrire le DOM si la classe n’a pas changé
    const changed = d.class !== lastSeenClass;
    lastSeenClass = d.class;

    // Récupère des infos lisibles
    const meta = infoFor(d.class);

    // Mets à jour le panneau méta
    const elType   = document.getElementById('ac_type');
    const elModel  = document.getElementById('ac_model');
    const elRole   = document.getElementById('ac_role');
    const elOrigin = document.getElementById('ac_origin');

    if (elType)   elType.textContent   = meta.type;
    if (elModel)  elModel.textContent  = d.class;
    if (elRole)   elRole.textContent   = meta.role;
    if (elOrigin) elOrigin.textContent = meta.origin;

    // Mets à jour la description (inclut la confiance)
    const elDesc = document.getElementById('ac_description');
    if (elDesc) {
      const conf = (d.confidence != null) ? ` (confiance: ${(d.confidence*100).toFixed(1)}%)` : "";
      elDesc.textContent = `${meta.desc}${conf ? " " + conf : ""}`;
    }

    // Optionnel : déclenche une analyse LLM uniquement si la classe a changé
    if (changed) {
      refreshAnalysis(); // appellera /analysis et mettra #llm_output à jour
    }
  } catch (e) {
    // silencieux
  }
}

async function refreshAnalysis() {
  try {
    const r = await fetch('/analysis');
    const d = await r.json();
    const el = document.getElementById('llm_output');
    if (el && d && d.text) el.textContent = d.text;
  } catch {}
}

// Lance un polling toutes les 2–3 s
setInterval(() => {
  refreshDetection();
}, 2500);

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
