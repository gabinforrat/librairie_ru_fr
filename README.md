# Inventaire Librairie
Cette application web permet de gérer un inventaire de librairie, utilisant l'alphabet latin et cyrilique.

## Fonctionnalités
- Enregistrement sans ISBN
- Enregistrement avec l'aide de l'ISBN
- Recherche en fonction:
	- Du titre
	- De l'auteur
	- De l'édition
	- De la catégorie
	- De la langue
	- De l'ISBN
- Génération d'un document comptable français

---
# Instalation
Nécessite : Python, pip et sqlite3

```sh
pip install -r requirement.txt
cat database.sql > sqlite3 src/inventaire.db
```

## Application Web
Pour lancer l'application utilisez:
```sh
python3 src/app.py
```
Et connectez-vous sur `localhost:8000`

## Entrée par fichier
Remplir le fichier `Entree_Inventaire_Massive.ods`
Si nécessaire de retrouver une version vierge du fichier : [Github](https://github.com/gabinforrat/librairie_ru_fr/blob/main/Entree_Inventaire_Massive.ods)

Pour l'ajouter
```sh
python3 src/ods_entree.py
```

---

---
# Credit
*Frontend* 	: [Mehdi AISSY](https://github.com/m-aissi)
*Backend* 	: [Gabin FORRAT](https://github.com/gabinforrat)
