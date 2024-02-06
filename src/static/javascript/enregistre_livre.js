function afficheSiVide(titre,auteur,qt,prix,lang,cat,edition){
    if(titre==""){
      document.getElementById("msgTitre").innerHTML =  "- Veuillez renseigner ce champ.";
    }
    else{
      document.getElementById("msgTitre").innerHTML =  "";
    }
    if(auteur==""){
      document.getElementById("msgAuteur").innerHTML =  "- Veuillez renseigner ce champ.";
    }
    else{
      document.getElementById("msgAuteur").innerHTML =  "";
    }
    if(qt==""){
      document.getElementById("msgQt").innerHTML =  "- Veuillez renseigner ce champ.";
    }
    else{
      document.getElementById("msgQt").innerHTML =  "";
    }
    if(prix==""){
      document.getElementById("msgPrix").innerHTML =  "- Veuillez renseigner ce champ.";
    }
    else{
      document.getElementById("msgPrix").innerHTML =  "";
    }
    if(lang==""){
      document.getElementById("msgLang").innerHTML =  "- Veuillez renseigner ce champ.";
    }
    else{
      document.getElementById("msgLang").innerHTML =  "";
    }
    if(cat==""){
      document.getElementById("msgCat").innerHTML =  "- Veuillez renseigner ce champ.";              
    }
    else{
      document.getElementById("msgCat").innerHTML =  "";
    }
    if(edition==""){
      document.getElementById("msgEdition").innerHTML =  "- Veuillez renseigner ce champ.";
      
    }
    else{
      document.getElementById("msgEdition").innerHTML =  "";
    }
    document.getElementById("successMsg").innerHTML =  "";
  }