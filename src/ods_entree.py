import os
import re
from pathlib import Path
import sqlite3
import pandas as pd
from app import calculHT, database_enregistrement_edition, database_enregistrement_auteurs, database_enregistrement_auteur_unique, database_enregistrement_livre, database_enregistrement_lien_livre_auteurs
from translation_ru_fr import transcription_russe_vers_france

def isNaN(num):
	return num != num

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



sheet = pd.read_excel(f"{str(Path(__file__).parent.parent)}/Entree_Inventaire_Massive.ods", engine="odf")

regex_isbn = r"^(?=(?:\D*\d){10}(?:(?:\D*\d){3})?$)[\d-]+$"

for row in sheet.values:
	livre = {
		"isbn" : "",
		"titre" : {
			"orginal" : "",
			"traduit" : ""
		},
		"quantite" : 0,
		"prix" : {
			"ttc" : 0.0,
			"ht" : 0.0,
		},
		"langue": 0,
		"categorie" : 0,
		"poid" :  0.0,
		"annee":  0,
		"id_edition" : 0,
		"solde" : 0.0,
	}

	# Titre
	if isNaN(row[0]):
		print("[Erreur] Pas de titre")
		print(f"[Erreur] {str(row)}")
		print("[Erreur] Ligne ignoré")
		continue

	livre["titre"]["orginal"] = row[0]
	livre["titre"]["traduit"] = transcription_russe_vers_france(row[0])

	# ISBN
	if not isNaN(row[1]):
		isbn = str(row[1])
		if re.match(regex_isbn,isbn):
			isbn = isbn.replace("-","")
			# Vérification ISBN : https://en.wikipedia.org/wiki/ISBN#Check_digit
			s = 0
			r = ""
			if len(isbn) == 10:
				for i in range(0,10):
					s += int(isbn[i])*(10-i)
				if s%11!=0:
					livre["isbn"] = isbn
				else:
					print("[Erreur] Problème ISBN non validé")
					print(f"[Erreur] ISBN de {livre['titre']['orginal']} ignoré")
			else:
				for i in range(0,13):
					# Echangé par rapport au calcul puisque l'on commence à 0
					if i%2==0: 
						s+= int(isbn[i])
					else:
						s+= int(isbn[i])*3
				if s%10!=0:
					livre["isbn"] = isbn
				else:
					print("[Erreur] Problème ISBN non validé")
					print(f"[Erreur] ISBN de {livre['titre']['orginal']} ignoré")
		else:
			print("[Erreur] Problème ISBN non validé")
			print(f"[Erreur] ISBN de {livre['titre']['orginal']} ignoré")


	# Auteur(s)
	if isNaN(row[2]):
		row[2] = "Inconnu"
	auteurs = row[2].split("/")
	list_auteurs = []
	for auteur in auteurs:
		list_auteurs.append({"original":auteur,"traduit":transcription_russe_vers_france(auteur)})
	id_auteurs = database_enregistrement_auteurs(list_auteurs)

	# Edition
	edition = row[3]
	if isNaN(edition):
		print("[Erreur] Pas de maison d'édition indiquée")
		print(f"[Edition] Entrez l'édition de {livre['titre']['orginal']}")
		edition = str(input(">"))

	livre["id_edition"] = database_enregistrement_edition(edition)

	# Categorie
	if isNaN(row[4]):
		print("[Erreur] Pas de catégorie donnée")
		print("[Categorie] 1  > Littérature")
		print("[Categorie] 2  > Traductions")
		print("[Categorie] 3  > Critique littéraire")
		print("[Categorie] 4  > Jeunesse")
		print("[Categorie] 5  > Bande Dessiné")
		print("[Categorie] 6  > Art")
		print("[Categorie] 7  > Linguistique")
		print("[Categorie] 8  > Droit")
		print("[Categorie] 9  > Economie")
		print("[Categorie] 10 > Histoire")
		print("[Categorie] 11 > Philosophie")
		print("[Categorie] 12 > Science")
		print("[Categorie] 13 > Théologie")
		print("[Categorie] 14 > Théatre")
		print("[Categorie] 15 > Poésie")
		print("[Categorie] 16 > Divers")
		index_input = 0
		while(index_input < 1 or index_input > 16):
			print(f"[Categorie] Entrez l'index de la catégorie pour {livre['titre']['orginal']}")
			try:
				index_input = int(input("> "))
			except ValueError:
				index_input = 0
				print("[Erreur] La valeur doit être un entier")
		livre["categorie"] =  index_input
	else:
		match row[4]:
			case "Littérature":
				livre["categorie"] = 1
			case "Traductions":
				livre["categorie"] = 2
			case "Critique littéraire":
				livre["categorie"] = 3
			case "Jeunesse":
				livre["categorie"] = 4
			case "Bande Dessiné":
				livre["categorie"] = 5
			case "Art":
				livre["categorie"] = 6
			case "Linguistique":
				livre["categorie"] = 7
			case "Droit":
				livre["categorie"] = 8
			case "Economie":
				livre["categorie"] = 9
			case "Histoire":
				livre["categorie"] = 10
			case "Philosophie":
				livre["categorie"] = 11
			case "Science":
				livre["categorie"] = 12
			case "Théologie":
				livre["categorie"] = 13
			case "Théatre":
				livre["categorie"] = 14
			case "Poésie":
				livre["categorie"] = 15
			case _:
				livre["categorie"] = 16


	# Langue
	if isNaN(row[5]):
		print("[Erreur] Pas de langue donnée")
		print(f"[Langue] Entrez l'index de la langue pour {livre['titre']['orginal']}")
		print("[Langue] 1 > Français")
		print("[Langue] 2 > Russe")
		print("[Langue] 3 > Ukrainien")
		print("[Langue] 4 > Anglais")
		print("[Langue] 5 > Allemand")
		print("[Langue] 6 > Autre")
		index_input = 0
		while(index_input < 1 or index_input > 6):
			try:
				index_input = int(input("> "))
			except ValueError:
				index_input = 0
				print("[Erreur] La valeur doit être un entier")
		livre["langue"] =  index_input
	else:
		match row[5]:
			case "Français":
				livre["langue"] = 1
			case "Russe":
				livre["langue"] = 2
			case "Ukrainien":
				livre["langue"] = 3
			case "Anglais":
				livre["langue"] = 4
			case "Allemand":
				livre["langue"] = 5
			case "Autre":
				livre["langue"] = 6

	# Prix TTC
	isTTCnotDefine = isNaN(row[6])
	if isTTCnotDefine:
		print("[Erreur] Pas de prix TTC donnée")
		print(f"[Prix] Entrez le prix de {livre['titre']['orginal']}")
		while isTTCnotDefine:
			try:
				row[6] = float(input(">"))
			except ValueError:
				print("[Erreur] La valeur doit être un nombre")
				continue
			isTTCnotDefine = False

	while row[6] < 0:
		print("[Erreur] Prix entrée négatif")
		print(f"[Prix] Entrez le prix de {livre['titre']['orginal']}")
		try:
			row[6] = float(input(">"))
		except ValueError:
			index_input = -1.0
			print("[Erreur] La valeur doit être positive")


	livre["prix"]["ttc"] = float(row[6])
	livre["prix"]["ht"] = calculHT(livre["prix"]["ttc"])

	# Quantite
	if not isNaN(row[7]):
		livre["quantite"] = int(row[7])

	# Année
	if not isNaN(row[8]):
		livre["annee"] = int(row[8])

	# Poid
	poid = row[9]
	if not isNaN(poid):
		while poid < 0:	
			print("[Erreur] Poid indiqué négatif")
			print(f"[Poid] Entrez le poid de {livre['titre']['orginal']}")
			try:
				poid = float(input(">"))
			except ValueError:
				print("[Erreur] La valeur doit être positive")
		livre["poid"] = poid

	id_livre = database_enregistrement_livre(livre)
	database_enregistrement_lien_livre_auteurs(id_livre,id_auteurs)