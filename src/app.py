from flask import Flask, make_response, request, render_template, redirect, Response, abort, url_for
import sqlite3
from translation_ru_fr import transcription_russe_vers_france
from get_info import get_categories, get_langues
from datetime import date
from pathlib import Path
import csv
import io
import re
import requests
import os

"""
Configuration:
	- Connect to the database
	- Set up app as Flask
"""
#Base de donnée
FOLDER = Path(__file__).parent.resolve()
DATABASE = f"{str(FOLDER)}/inventaire.db"
if os.path.isfile(DATABASE):
	connection = sqlite3.connect(DATABASE, check_same_thread=False)
	cursor = connection.cursor()
else:
	f = open(DATABASE,"a")
	f.close()
	with open(f"{str(Path(__file__).parent.parent)}/database.sql",'r') as file:
		database_script = file.read()
	connection = sqlite3.connect(DATABASE, check_same_thread=False)
	cursor = connection.cursor()
	cursor.executescript(database_script)
	connection.commit()

#Flask
app = Flask(__name__)

"""
Variable Global
"""
TITLE = "Les Editeurs Réunis"
TVA = 1.2

"""
Calcul le prix sans taxe depuis le prix avec.
Arguments:
	- prixTTC : prix toute taxe comprise
Retour: 
	- Prix Hors Taxe (HT)
"""
def calculHT(prixTTC):
	return (prixTTC/TVA)

@app.route("/",methods=["GET"])
def main():
	page_title = TITLE
	return render_template("index.html",page_title=page_title)

# Livre
## Enregistrer

"""
Page pour entrer les informations d'un nouveau livre à enregistrer
"""
@app.route("/enregistrement",methods=["GET","POST"])
def livre_enregistrement():
	page_title = TITLE + "| Enregistrement"
	all_auteur = get_all_auteur()
	all_edition = get_all_edition()
	if request.method == 'GET':
		return render_template("enregistrement_livre.html",page_title=page_title,all_auteur=str(all_auteur),all_edition=str(all_edition))
	else :
		isbn = request.form.get("isbn")
		titre = request.form.get("titre")
		auteurs = request.form.getlist("auteurs")
		langue = {
			"id" : request.form.get("langue_id"),
			"nom": request.form.get("langue_nom")
		}
		edition = request.form.get("edition")
		annee = request.form.get("annee")
		info_isbn = {
			"isbn" : isbn,
			"titre" : titre,
			"auteurs" : auteurs,
			"langue" : langue,
			"edition" : edition,
			"annee" : annee,
		}
		return render_template("enregistrement_livre.html",page_title=page_title,all_auteur=str(all_auteur),all_edition=str(all_edition),info_isbn=info_isbn)


@app.route("/enregistrement/ISBN",methods=["GET"])
def livre_enregistrement_ISBN():
	page_title = TITLE + "| Enregistrement"
	erreur = request.args.get('e')
	isbn = request.args.get('isbn')
	if erreur == None:
		return render_template("enregistrement_livre_ISBN.html",page_title=page_title)
	else:
		return render_template("enregistrement_livre_ISBN.html",page_title=page_title,erreur=erreur,isbn=isbn)

@app.route("/ISBN",methods=["POST"])
def get_ISBN():
	isbn=request.form['isbn'].replace(" ","")
	# Source Regex: https://stackoverdlow.com/questions/41271613/use-regex-to-verify-an-isbn-number
	regex_isbn = r"^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$"
	if re.match(regex_isbn,isbn):
		isbn = isbn.replace("-","")
		# Vérification ISBN : https://en.wikipedia.org/wiki/ISBN#Check_digit
		s = 0
		r = ""
		if len(isbn) == 10:
			for i in range(0,10):
				s += int(isbn[i])*(10-i)
			if s%11!=0:
				return redirect(url_for('livre_enregistrement_ISBN',e="ISBN_invalide", isbn=isbn))
		else:
			for i in range(0,13):
				# Echangé par rapport au calcul puisque l'on commence à 0
				if i%2==0: 
					s+= int(isbn[i])
				else:
					s+= int(isbn[i])*3
			if s%10!=0:
				return redirect(url_for('livre_enregistrement_ISBN',e="ISBN_invalide", isbn=isbn))
	else:
		return redirect(url_for('livre_enregistrement_ISBN',e="ISBN_invalide", isbn=isbn))
	link_book = f"https://openlibrary.org/isbn/{isbn}.json" 
	book_request = requests.get(link_book)
	if book_request.status_code == 404:
		return redirect(url_for('livre_enregistrement_ISBN',e="ISBN_introuvable", isbn=isbn))


	book_json = book_request.json()

	if "languages" in book_json:
		match book_json["languages"][0]["key"][-3:]:
			case "fre":
				info_langue = {"id" : 1, "nom": "Français"}
			case "rus":
				info_langue = {"id" : 2, "nom": "Russe"}
			case "ukr":
				info_langue = {"id" : 3, "nom": "Ukrainien"}
			case "eng":
				info_langue = {"id" : 4, "nom": "Anglais"}
			case "gem":
				info_langue = {"id" : 5, "nom": "Allemand"}
			case _:
				info_langue = {"id" : 6, "nom": "Autre"}
	else:
		info_langue = None

	if "publishers" in book_json:
		info_edition = book_json['publishers'][0]
	else:
		info_edition = None

	if "publish_date" in book_json:
		info_annee = re.findall(r'\d{4}',book_json["publish_date"])[0]
	else:
		info_annee = None

	info_auteurs = []
	if "authors" in book_json:
		for a in book_json["authors"]:
			info_auteurs.append(requests.get(f"https://openlibrary.org{a['key']}.json").json()["name"]) 

	info_isbn = {
		"isbn" : isbn,
		"titre" : book_json['title'],
		"auteurs" : info_auteurs,
		"langue" : info_langue,
		"edition" : info_edition,
		"annee" : info_annee,
	}

	return render_template("isbn_post.html",info_isbn=info_isbn)

"""
Page pour enregistrer dans la base de donnée les informations du nouveau livre
"""
@app.route("/sauvegarde",methods=["POST"])
def livre_sauvegarde():
	isbn=request.form['isbn']
	edition=request.form['edition']
	auteurs=request.form.getlist("auteur")
	auteurs_list = []
	for a in auteurs:
		auteurs_list.append({
			"original" : str(a),
			"traduit" : transcription_russe_vers_france(a),
			})

	titre=request.form['titre']
	titre_traduit = transcription_russe_vers_france(titre)

	prix_TTC=request.form['prix']
	prix_HT = round(calculHT(float(prix_TTC)),2)
	
	livre = {
		"isbn" : isbn,
		"titre" : {
			"orginal" : titre,
			"traduit" : titre_traduit
		},
		"quantite" : int(request.form['quantite']),
		"prix" : {
			"ttc" : float(prix_TTC),
			"ht" : float(prix_HT),
		},
		"langue": int(request.form['langue']),
		"categorie" : int(request.form['categorie']),
		"poid" :  0.0,
		"annee":  int(request.form['annee']),
		"id_edition" : -1,
		"solde" : 0.0,
	}
	poid = request.form['poid']
	if poid:
		livre['poid'] = float(poid)
	solde = request.form['solde']
	if solde:
		livre['solde'] = float(solde)

	livre["id_edition"] = database_enregistrement_edition(edition)
	id_livre = database_enregistrement_livre(livre)
	id_auteurs = database_enregistrement_auteurs(auteurs_list)
	database_enregistrement_lien_livre_auteurs(id_livre,id_auteurs)
	return redirect(f"/livre/{id_livre}")


def livre_modifie_bd(livre):
	sqlite_update = """UPDATE Livre Set  
	ISBN = ?,
	titreOriginal = ?,
	titreTraduit = ?,
	lang = ?,
	edition = ?,
	categorie = ?,
	prixTTC = ?,
	prixHT = ?,
	quantite = ?,
	annee = ?,
	poid = ?,
	solde = ?
	WHERE idLivre = ?
	"""

	sqlite_value = (
		livre["isbn"], 
		livre["titre"]["original"], 
		livre["titre"]["traduit"],
		livre["langue"],
		livre["edition"],
		livre["categorie"],
		livre["prix"]["ttc"],
		livre["prix"]["ht"],
		livre["quantite"],
		livre["annee"],
		livre["poid"],
		livre["solde"],
		livre["id_livre"],
	)
	cursor.execute(sqlite_update,sqlite_value)



@app.route("/modifie",methods=["POST"])
def livre_modifie():
	id_livre = request.form['id']
	isbn=request.form['isbn']
	edition=request.form['edition']
	auteurs=request.form.getlist("auteur")
	auteurs_list = []
	titre=request.form['titre']
	titre_traduit = request.form['titre_traduit']	

	prix_TTC=request.form['prix']
	prix_HT = round(calculHT(float(prix_TTC)),2)
	
	id_edition = database_enregistrement_edition(edition)

	livre = {
		"id_livre" : id_livre,
		"isbn" : isbn,
		"titre" : {
			"original" : titre,
			"traduit" : titre_traduit
		},
		"quantite" : int(request.form['quantite']),
		"prix" : {
			"ttc" : float(prix_TTC),
			"ht" : float(prix_HT),
		},
		"langue": int(request.form['langue']),
		"categorie" : int(request.form['categorie']),
		"poid" :  0.0,
		"annee":  int(request.form['annee']),
		"edition" : id_edition,
		"solde" : 0.0
	}
	poid = request.form['poid']
	if poid:
		livre['poid'] = float(poid)
	solde = request.form['solde']
	if solde:
		livre['solde'] = float(solde)

	livre_modifie_bd(livre)
	
	return redirect(f"/livre/{id_livre}")

"""
Function pour récupérer l'identifiant de la maison d'édition dans l'inventaire.
Enregistre les nouvelles maisons d'éditions.

Arguments:
	- nom_edition (str) : nom de la maison d'édition 
Retour :
	- id_edition (int) : identifiant de la maison d'édition dans la base de donnée
"""
def database_enregistrement_edition(nom_edition : str = ""):
	sqlite_value = (str(nom_edition),)
	sqlite_select ="SELECT * FROM Edition WHERE nomEdition= ? ;"
	cursor.execute(sqlite_select,sqlite_value)
	edition_result = cursor.fetchall()

	if not edition_result:
		# Insert Edition
		sqlite_insert = "INSERT INTO edition (nomEdition) VALUES (?);"
		cursor.execute(sqlite_insert,sqlite_value)
		connection.commit()

		# Get Edition Id
		sqlite_select ="SELECT * FROM Edition WHERE nomEdition= ? ;"
		cursor.execute(sqlite_select,sqlite_value)
		edition_result = cursor.fetchall()

	id_edition = int(edition_result[0][0])
	return id_edition


"""
Function pour récupérer les identifiants de la liste des auteurs 
Arguments:
	- auteurs (list of dir) : Liste des noms auteurs sous forme de dictionnaires (avec le nom original et le nom traduit) 
Retour :
	- id_auteurs_list (list of int) : Liste des identifiants des auteurs
"""
def database_enregistrement_auteurs(auteurs : list):
	id_auteurs_list = []
	for a in auteurs:
		new_id  = database_enregistrement_auteur_unique(a['original'],a['traduit'])
		id_auteurs_list.append(new_id)
	return id_auteurs_list

"""
Function pour récupérer l'identifiant d'un auteur.
Enregistre les auteurs inconnus.
Arguments:
	- auteur_original (str) : Nom de l'auteur comme entré par l'utilisateur 
	- auteur_traduit (str) : Nom de l'auteur passé à l'alphabet latin
Retour :
	- id_auteur : identiant de l'auteur
"""
def database_enregistrement_auteur_unique(auteur_original : str, auteur_traduit : str):
	# Recherche de l'auteur dans la base de donnée
	sqlite_value = (str(auteur_original),)
	sqlite_select ="SELECT * FROM Auteur WHERE nomAuteur= ? ;"
	cursor.execute(sqlite_select,sqlite_value)
	auteur_result = cursor.fetchall()

	if not auteur_result:
		# Si on ne le trouve pas:
		# On l'ajoute
		sqlite_insert = "INSERT INTO auteur (nomAuteur,nomTraduit) VALUES (?,?);"
		sqlite_second_value = (str(auteur_original),str(auteur_traduit))
		cursor.execute(sqlite_insert,sqlite_second_value)
		connection.commit()

		# On relance la recherche
		cursor.execute(sqlite_select,sqlite_value)
		auteur_result = cursor.fetchall()

	id_auteur = int(auteur_result[0][0])
	return id_auteur


"""
Fonction pour enregistrer un nouveau livre
Arguments:
	- livre (dir) : directory avec toutes les informations sur le livre à l'exception de son (ses) auteur(s)
Retour :
	- id_livre (int) : identifiant du livre dans la base de donnée 
"""
def database_enregistrement_livre(livre : dir):
	sqlite_value = (livre['isbn'],livre['titre']['orginal'],livre['titre']['traduit'],
		livre['langue'],livre['id_edition'],livre['categorie'],livre['prix']['ttc'],livre['prix']['ht'],
		livre['quantite'],livre['annee'],livre['poid'],livre['solde'])
	sqlite_insert ="""INSERT INTO Livre 
	(ISBN,titreOriginal,titreTraduit,lang,edition,categorie,prixTTC,prixHT,quantite,annee,poid,solde) 
	VALUES(?,?,?,?,?,?,?,?,?,?,?,?)"""
	cursor.execute(sqlite_insert,sqlite_value)
	connection.commit()
	cursor.execute("SELECT MAX(idLivre) FROM Livre")
	id_livre = cursor.fetchone()[0]
	return id_livre

"""
Fonction pour enregistrer les auteurs d'un livre
Arguments:
	- id_livre (int) : identifiant du nouveau livre
	- id_auteurs (list of int) : identifiants de tout les auteurs
"""
def database_enregistrement_lien_livre_auteurs(id_livre : int,id_auteurs : list):
	sqlite_insert = "INSERT INTO LienAuteurLivre (idLivre,idAuteur) VALUES (?,?)"
	for id_a in id_auteurs:
		sqlite_value = (id_livre,id_a)
		cursor.execute(sqlite_insert,sqlite_value)
		connection.commit()


"""
Fonction qui renvoie la liste de tout les auteurs (nom original)
"""
def get_all_auteur():
	list_auteurs = []
	sqlite_select ="SELECT nomAuteur FROM Auteur "
	cursor.execute(sqlite_select,)
	auteur_result = cursor.fetchall()
	for a in auteur_result:
		list_auteurs.append(a[0])
	return list_auteurs

"""
Fonction qui renvoie la liste de toute les éditions 
"""
def get_all_edition():
	list_edition = []
	sqlite_select ="SELECT nomEdition FROM Edition "
	cursor.execute(sqlite_select,)
	edition_result = cursor.fetchall()
	for e in edition_result:
		list_edition.append(e[0])
	return list_edition

## Page Livre
@app.route("/livre/<id>",methods=["GET"])
def livre_resume(id : int):
	livre = get_info_livre(id)
	if livre is None:
		abort(404)
	page_title = f"{TITLE} | {livre['titre']}"
	return render_template("page_livre.html",page_title=page_title,livre=livre)

## Vente
def vendre(id_livre : int,qtn : int):
	sqlite_update = "UPDATE Livre SET quantite = quantite - ? WHERE idLivre = ?"
	sqlite_value = (qtn,id_livre)
	cursor.execute(sqlite_update,sqlite_value)

@app.route("/vente",methods=["POST"])
def livre_vente():
	id_livre = int(request.form.get('id'))
	nbr_vente = int(request.form.get('vente'))
	vendre(id_livre,nbr_vente)
	return redirect(f"/livre/{id_livre}")

## Modifier
### Utiliser ID pour avoir le livre et ses infos
@app.route("/modification/<id>",methods=["GET"])
def livre_modification(id : int):
	livre = get_info_livre(id)
	if livre is None:
		abort(404)
	page_title = f"{TITLE} | Modification de {livre['titre']}"
	all_auteur = str(get_all_auteur())
	all_edition = str(get_all_edition())

	return render_template('modification_livre.html',page_title=page_title,livre=livre,all_auteur=all_auteur,all_edition=all_edition)

"""
Fonction pour avoir toute les informations sur un livre
Arguments:
	- id (int) : identifiant du livre recherché
Returns:
	- livre (dir) : dictionnaire contenant toutes les informations sur le livre
"""
def get_info_livre(id : int):
	sqlite_select_livre = """SELECT L.ISBN, L.titreOriginal, L.titreTraduit, L.quantite, L.prixTTC, LAN.idLangue, LAN.nomLangue, C.idCategorie, C.nomCategorie, L.poid, L.annee, E.idEdition, E.nomEdition, L.solde
	FROM Livre AS L, Edition AS E, LienAuteurLivre AS LAL, Categorie AS C, Langue AS LAN
	WHERE L.idLivre = ?
	AND LAL.idLivre = L.idLivre
	AND E.idEdition = L.edition 
	AND C.idCategorie = L.categorie
	AND LAN.idLangue = L.lang
	"""
	sqlite_value = (str(id),)
	cursor.execute(sqlite_select_livre,sqlite_value)
	livre_result = cursor.fetchone()

	if livre_result == None:
		return None

	sqlite_select_auteurs = """SELECT A.idAuteur, A.nomAuteur, A.nomTraduit
	FROM Auteur AS A, LienAuteurLivre AS LAL
	WHERE LAL.idLivre = ?
	AND LAL.idAuteur = A.idAuteur
	"""
	cursor.execute(sqlite_select_auteurs,sqlite_value)
	auteurs_result = cursor.fetchall()

	livre = {
		"identifiant" : int(id),
		"isbn" : livre_result[0],
		"titre" : livre_result[1],
		"titre_traduit" : livre_result[2],
		"auteurs" : [],
		"quantite" : livre_result[3],
		"prix_ttc" : livre_result[4],
		"langue": {
			"identifiant" : livre_result[5],
			"nom" : livre_result[6]
		},
		"categorie" : {
			"identifiant" : livre_result[7],
			"nom" : livre_result[8]
		},
		"poid" : livre_result[9],
		"annee": livre_result[10],
		"edition" : {
			"identifiant" : livre_result[11],
			"nom" : livre_result[12],
		},
		"solde" : livre_result[13],
	}

	for auteur in auteurs_result:
		livre["auteurs"].append({
			"id" : auteur[0],
			"nom" : auteur[1],
			"nom_traduit" : auteur[2]
			})

	return livre


## Chercher
@app.route("/recherche/livre",methods=['GET','POST'])
def livre_recherche():
	page_title = f"{TITLE} | Recherche : Titre"
	info_page = {
		"recherche" : "titre",
		"action" : "/recherche/livre",
		"titre" : "Recherche des livres par titre de livre",
	}
	if request.method == 'GET':
		return render_template('recherche.html',page_title=page_title,info=info_page)
	else:
		recherche_titre = request.form.get('titre')
		sqlite_recherche_titre = "SELECT idLivre FROM Livre WHERE titreOriginal LIKE '%' || ? || '%' OR titreTraduit LIKE '%' || ? || '%' "
		sqlite_value = (str(recherche_titre),str(recherche_titre),)
		cursor.execute(sqlite_recherche_titre,sqlite_value)
		recherche_result = cursor.fetchall()
		recherche_list_livre = [get_info_livre(l[0]) for l in recherche_result]
		recherche_list_livre = [i for i in recherche_list_livre if i is not None]
		return render_template('recherche.html',page_title=page_title,info=info_page,list_livre=recherche_list_livre)

## Supprimer
@app.route("/suppression/<id>")
def supprimer_livre(id : int):
	sqlite_value = (str(id),)
	sqlite_delete = "DELETE FROM Livre WHERE idLivre = ?"
	cursor.execute(sqlite_delete,sqlite_value)
	sqlite_delete = "DELETE FROM LienAuteurLivre WHERE idLivre = ?"
	cursor.execute(sqlite_delete,sqlite_value)
	connection.commit()
	return redirect("/")




# Auteur
## Chercher
@app.route("/recherche/auteur",methods=['GET','POST'])
def auteur_recherche():
	page_title = f"{TITLE} | Recherche : Auteur"
	info_page = {
		"recherche" : "auteur",
		"action" : "/recherche/auteur",
		"titre" : "Recherche des livres par auteur",
	}
	if request.method == 'GET':
		return render_template('recherche.html',page_title=page_title,info=info_page)
	else:
		recherche_auteur = request.form.get('auteur')
		sqlite_recherche_auteur = """
		SELECT LAL.idLivre 
		FROM LienAuteurLivre AS LAL, Auteur AS A 
		WHERE LAL.idAuteur = A.idAuteur 
		AND (A.nomAuteur LIKE '%' || ? || '%'
		OR A.nomTraduit LIKE '%' || ? || '%')
		GROUP BY LAL.idLivre
		"""
		sqlite_value = (str(recherche_auteur),str(recherche_auteur),)
		cursor.execute(sqlite_recherche_auteur,sqlite_value)
		recherche_result = cursor.fetchall()
		recherche_list_livre = [get_info_livre(l[0]) for l in recherche_result]
		recherche_list_livre = [i for i in recherche_list_livre if i is not None]
		return render_template('recherche.html',page_title=page_title,info=info_page,list_livre=recherche_list_livre)

# Edition
## Chercher
@app.route("/recherche/edition",methods=['GET','POST'])
def edition_recherche():
	page_title = f"{TITLE} | Recherche : Edition"
	info_page = {
		"recherche" : "edition",
		"action" : "/recherche/edition",
		"titre" : "Recherche des livres par maison d'édition",
	}

	if request.method == 'GET':
		return render_template('recherche.html',page_title=page_title,info=info_page)
	else:
		recherche_edition = request.form.get('edition')
		sqlite_recherche_edition = "SELECT idLivre FROM Livre AS L, Edition AS E WHERE L.edition = E.idEdition AND  E.nomEdition LIKE '%' || ? || '%'"
		sqlite_value = (str(recherche_edition),)
		cursor.execute(sqlite_recherche_edition,sqlite_value)
		recherche_result = cursor.fetchall()
		recherche_list_livre = [get_info_livre(l[0]) for l in recherche_result]
		recherche_list_livre = [i for i in recherche_list_livre if i is not None]
		return render_template('recherche.html',page_title=page_title,info=info_page,list_livre=recherche_list_livre)

# Categorie
## Chercher

"""
Recherche des livres d'une catégorie
"""
@app.route("/recherche/categorie",methods=['GET','POST'])
def categorie_recherche():	
	page_title = f"{TITLE} | Recherche : Categorie"
	info_page = {
		"action" : "/recherche/categorie",
		"dropdown" : {
			"name" : "categorie",
			"content" : get_categories()
		},
		"titre" : "Recherche des livres par catégorie"

	}
	if request.method == 'GET':
		return render_template('recherche_drop.html',page_title=page_title,info=info_page)
	else:
		recherche_categorie = request.form.get('categorie')
		sqlite_recherche_categorie = "SELECT idLivre FROM Livre WHERE categorie = ?"
		sqlite_value = (str(recherche_categorie),)
		cursor.execute(sqlite_recherche_categorie,sqlite_value)
		recherche_result = cursor.fetchall()
		recherche_list_livre = [get_info_livre(l[0]) for l in recherche_result]
		recherche_list_livre = [i for i in recherche_list_livre if i is not None]
		return render_template('recherche_drop.html',page_title=page_title,info=info_page,list_livre=recherche_list_livre)

# Langue
## Chercher
"""
Recherche des livres dans une langue
"""
@app.route("/recherche/langue",methods=['GET','POST'])
def recherche_langue():
	page_title = f"{TITLE} | Recherche : Langue"
	info_page = {
		"action" : "/recherche/langue",
		"dropdown" : {
			"name" : "langue",
			"content" : get_langues()
		},
		"titre" : "Recherche des livres par langue"
	}
	if request.method == 'GET':
		return render_template('recherche_drop.html',page_title=page_title,info=info_page)
	else:
		recherche_langue = request.form.get('langue')
		sqlite_recherche_langue = "SELECT idLivre FROM Livre WHERE lang = ?"
		sqlite_value = (str(recherche_langue),)
		cursor.execute(sqlite_recherche_langue,sqlite_value)
		recherche_result = cursor.fetchall()
		recherche_list_livre = [get_info_livre(l[0]) for l in recherche_result]
		recherche_list_livre = [i for i in recherche_list_livre if i is not None]
		return render_template('recherche_drop.html',page_title=page_title,info=info_page,list_livre=recherche_list_livre)

#ISBN
## Chercher
@app.route("/recherche/ISBN",methods=['GET','POST'])
def isbn_recherche():
	page_title = f"{TITLE} | Recherche : ISBN"
	info_page = {
		"recherche" : "isbn",
		"action" : "/recherche/ISBN",
		"titre" : "Recherche d'un livre par son ISBN",
	}

	if request.method == 'GET':
		return render_template('recherche.html',page_title=page_title,info=info_page)
	else:
		recherche_isbn = request.form.get('isbn').replace(" ","")
		recherche_isbn = recherche_isbn.replace("-","")
		sqlite_recherche_isbn = "SELECT idLivre FROM Livre WHERE ISBN=?"
		sqlite_value = (str(recherche_isbn),)
		cursor.execute(sqlite_recherche_isbn,sqlite_value)
		recherche_result = cursor.fetchall()
		recherche_list_livre = [get_info_livre(l[0]) for l in recherche_result]
		recherche_list_livre = [i for i in recherche_list_livre if i is not None]
		return render_template('recherche.html',page_title=page_title,info=info_page,list_livre=recherche_list_livre)


# Exporter
"""
Fonction pour télécharger le fichier csv du document comptable
"""
@app.route("/telechargement")
def export():
	return Response(
		csvFile(),
		mimetype="text/csv",
		headers={
			"Content-disposition": f"attachment; filename={str(date.today())}-DocumentComptable.csv"
		}
	)

"""
Fonction pour générer le document comptable
Return : 
	- Fichier csv sous la forme d'une chaine de caractère
"""
def csvFile():
	command_sql="""
	SELECT L.idLivre, L.TitreTraduit, GROUP_CONCAT(A.nomTraduit), E.nomEdition, La.nomLangue, C.nomCategorie, L.prixTTC,L.prixHT, L.quantite, L.solde
	FROM Auteur AS A, Categorie AS C, Edition AS E, Langue AS La, Livre AS L , LienAuteurLivre AS LAL
	WHERE A.idAuteur = LAL.idAuteur
	AND LAL.idLivre = L.idLivre
	AND C.idCategorie = L.categorie
	AND E.idEdition = L.edition 
	AND La.idLangue = L.lang
	GROUP BY L.idLivre;
	"""
	cursor.execute(command_sql)
	list_bd = cursor.fetchall()

	csv_fields = ['TITRE','AUTEUR(S)','EDITION','LANGUE','CATEGORIE','PRIX(HT)','PRIX(TTC)','PRIX SOLDE (TTC)','QUANTITE','PRIX GLOBAL (HT)','PRIX GLOBAL (TTC)','PRIX GLOBAL SOLDE (TTC)']
	csv_filename =str(date.today()) +"-DocumentComptable.csv"
	output = io.StringIO()
	writer = csv.DictWriter(output, quoting=csv.QUOTE_NONNUMERIC,fieldnames=csv_fields)
	writer.writeheader()
	for each in list_bd:
		writer.writerow(
			{
			'TITRE':each[1],'AUTEUR(S)':each[2],'EDITION':each[3],'LANGUE':each[4],
			'CATEGORIE':each[5],'PRIX(HT)':each[7],'PRIX(TTC)':each[6],
			'PRIX SOLDE (TTC)':each[6]-((each[9]/100)*each[6]),'QUANTITE':each[8],
			'PRIX GLOBAL (HT)':each[7]*each[8],'PRIX GLOBAL (TTC)':each[6]*each[8], 
			'PRIX GLOBAL SOLDE (TTC)':each[8]*(each[6]-((each[9]/100)*each[6]))
			}
		)
	return output.getvalue()




"""
Error 404 | Redirection après n secondes : https://www.geeksforgeeks.org/python-404-error-handling-in-flask/
"""
@app.errorhandler(404) 
def erreur404(e):
	return render_template("404.html",page_title=TITLE+" | Page non trouvé")

@app.errorhandler(500)
def erreur500(e):
	return "probleme d'execution"

if __name__ == '__main__':
	app.run(host="0.0.0.0", port="8000", debug=True)

