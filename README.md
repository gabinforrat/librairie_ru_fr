# Inventaire Librairie 
Cette application web permet de gérer un inventaire de librairie, utilisant l'alphabet latin et cyrilique. 

## Fonctionnalités
- Enregistrement sans ISBN
- Recherche en fonction: 
	- Du titre
	- De l'auteur
	- De l'édition
	- De la catégorie
	- De la langue
- Génération d'un document comptable français

## A FAIRE
- Modification des livres (à terminer)
- Solde / Réduction
- Enregistrement avec ISBN

### Idées possibles
- Panier ?
- Vente au poid ? 

---
# Instalation
```sh
pip install -r requirement.txt
cat database.sql > sqlite3 src/inventaire.db
```
Pour lancer l'application utilisez:
```sh
python3 src/app.py
```
Et connectez-vous sur `localhost:8000`


---
# Credit
*Frontend* 	: [Mehdi AISSY](https://github.com/m-aissi)
*Backend* 	: [Gabin FORRAT](https://github.com/gabinforrat) 