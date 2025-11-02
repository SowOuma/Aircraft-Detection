// --- Métadonnées locales rapides ---
const AIRCRAFT_INFO = {
  A10:{type:"Attack aircraft",role:"CAS / anti-char",origin:"USA",desc:"L’A-10 est spécialisé dans l’appui rapproché, robuste et précis à basse altitude."},
  B1:{type:"Bomber",role:"Bombardement supersonique",origin:"USA",desc:"Bombardier à grande vitesse et longue portée."},
  B52:{type:"Bomber",role:"Bombardement stratégique",origin:"USA",desc:"Très grande portée et charge utile stratégique."},
  C130:{type:"Transport",role:"Transport tactique",origin:"USA",desc:"Transport, aéro-largage et évacuation sanitaire."},
  C5:{type:"Transport",role:"Transport stratégique",origin:"USA",desc:"Fret très volumineux sur longue distance."},
  F117:{type:"Stealth",role:"Attaque furtive",origin:"USA",desc:"Un des premiers appareils furtifs opérationnels."},
  F15:{type:"Fighter",role:"Supériorité aérienne",origin:"USA",desc:"Vitesse, manœuvrabilité et grande charge utile."},
  F22:{type:"Stealth Fighter",role:"Supériorité aérienne",origin:"USA",desc:"Furtivité, capteurs avancés, super-croisière."},
  MQ9:{type:"UAV",role:"ISR / frappe",origin:"USA",desc:"Drone MALE pour renseignement et frappe de précision."},
  Tu160:{type:"Bomber",role:"Bombardement stratégique",origin:"Russie",desc:"Bombardier supersonique à aile variable."},
  aircraft:{type:"Aircraft",role:"Générique",origin:"—",desc:"Aéronef détecté (classe générique)."},
  jet:{type:"Jet",role:"Générique",origin:"—",desc:"Jet détecté (classe générique)."}
};
function infoFor(cls){
  return AIRCRAFT_INFO[cls] || {type:"Aircraft",role:"—",origin:"—",desc:"Aéronef détecté."};
}

// --- Polling + déclenchement LLM ---
let lastSeenClass = null;
let lastAnalysisAt = 0;
const ANALYSIS_COOLDOWN_MS = 3000;

async function refreshAnalysis(det) {
  const el = document.getElementById("llm_output");
  try {
    const resp = await fetch("/analysis", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        "class": det.cls,
        "confidence": det.conf ?? 0.0,
        "context": ""
      })
    });

    let data;
    try {
      data = await resp.json();
    } catch {
      const t = await resp.text();
      el.innerHTML = `<span style="color:#f87171;">⚠️ Erreur d'analyse :</span> ${t.slice(0,200)}`;
      return;
    }

    const a = data.analysis;

    if (a && typeof a === "object") {
      // 🔹 Si le serveur renvoie un objet JSON
      const facts = (a.facts || []).map(f => `- ${f}`).join("\n");
      const content = `${a.summary}\n${facts}${a.caution && facts ? "\n" : ""}${a.caution ? `Note: ${a.caution}` : ""}`;
      el.innerHTML = marked.parse(content);
    } else if (typeof a === "string") {
      // 🔹 Ici on transforme ton texte Markdown (avec **gras**, etc.)
      el.innerHTML = marked.parse(a);
    } else if (data.error) {
      el.innerHTML = `<span style="color:#f87171;">⚠️ Erreur :</span> ${data.error}`;
    } else {
      el.innerHTML = "<em>Analyse vide.</em>";
    }
  } catch (e) {
    if (el) el.innerHTML = "<span style='color:#f87171;'>🚫 Erreur réseau ou serveur.</span>";
    console.error(e);
  }
}


async function refreshDetection(){
  try{
    const r = await fetch('/last_detection');
    const d = await r.json();
    if(!d || !d.class) return;

    const changed = d.class !== lastSeenClass;
    lastSeenClass = d.class;

    const meta = infoFor(d.class);
    const confPct = (d.confidence != null) ? ` (confiance: ${(d.confidence*100).toFixed(1)}%)` : "";

    // Mise à jour du panneau info
    const elType   = document.getElementById('ac_type');
    const elModel  = document.getElementById('ac_model');
    const elRole   = document.getElementById('ac_role');
    const elOrigin = document.getElementById('ac_origin');
    const elDesc   = document.getElementById('ac_description');

    if(elType)   elType.textContent   = meta.type;
    if(elModel)  elModel.textContent  = d.class;
    if(elRole)   elRole.textContent   = meta.role;
    if(elOrigin) elOrigin.textContent = meta.origin;
    if(elDesc)   elDesc.textContent   = meta.desc + confPct;

    // Déclenche l'analyse LLM seulement si la classe change et cooldown ok
    const now = Date.now();
    if (changed && (now - lastAnalysisAt > ANALYSIS_COOLDOWN_MS)){
      lastAnalysisAt = now;
      await refreshAnalysis({ cls: d.class, conf: d.confidence });
    }
  }catch(e){
    // silencieux
  }
}
// À l’ouverture de la page, on vide les anciennes infos côté serveur
fetch("/reset_detection", { method: "POST" })
  .then(() => console.log("Détection réinitialisée au démarrage"))
  .catch(() => console.warn("Impossible de réinitialiser la détection"));

// --- Bouton Camera1 et formulaire source ---
$(document).ready(function(){
  $('#camera1').click(function(){
    $.post('/cliquer_bouton', { button: 'camera1' }, function(response){
      if(response.url){
        $('#video_camera1').attr('src', response.url);
      }else{
        alert('Erreur : Aucun flux disponible pour la caméra 1.');
      }
    });
  });

  document.getElementById('camera-form').addEventListener('submit', function(e){
    e.preventDefault();
    const camera1Url = document.getElementById('cam1').value;
    if(!camera1Url){ alert('Veuillez entrer la source.'); return; }
    fetch('/recuperer_source', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ camera1_url: camera1Url })
    })
    .then(r=>r.json())
    .then(d=>{
      if(d.error) alert('Erreur: '+d.error);
      else console.log('Source ok:', d);
    })
    .catch(console.error);
  });
});

// Polling
setInterval(refreshDetection, 2500);
