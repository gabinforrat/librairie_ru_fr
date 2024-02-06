PRAGMA encoding = "UTF-8"; --  Change encryption en UTF-8 qui supporte les caractères cyriliques https://www.sqlite.org/pragma.html#pragma_encoding

DROP TABLE Auteur;
DROP TABLE Categorie;
DROP TABLE Edition;
DROP TABLE Langue;
DROP TABLE Livre;
DROP TABLE LienAuteurLivre;

CREATE TABLE Auteur(
	idAuteur INTEGER PRIMARY KEY AUTOINCREMENT,
	nomAuteur CHAR(60) NOT NULL,
	nomTraduit CHAR(60)
);

CREATE TABLE Categorie(
	idCategorie INTEGER PRIMARY KEY AUTOINCREMENT,
	nomCategorie CHAR(60) NOT NULL
);

CREATE TABLE Edition(
	idEdition INTEGER PRIMARY KEY AUTOINCREMENT,
	nomEdition CHAR(60) NOT NULL
);

CREATE TABLE Langue(
	idLangue INTEGER PRIMARY KEY AUTOINCREMENT,
	nomLangue CHAR(10) NOT NULL
);

CREATE TABLE Livre(
	idLivre INTEGER PRIMARY KEY AUTOINCREMENT,
	ISBN  INTEGER,
	titreOriginal CHAR(100) NOT NULL,
	titreTraduit CHAR(100),
	lang INTEGER,
	edition INTEGER,
	categorie INTEGER,
	prixTTC REAL,
	prixHT REAL,
	quantite INTEGER,
	annee INTEGER,
	poid REAL,
	FOREIGN KEY(lang)
		REFERENCES Langue(idLangue)
	FOREIGN KEY(edition)
		REFERENCES Edition(idEdition)
	FOREIGN KEY(categorie)
		REFERENCES Categorie(idCategorie)
);

CREATE TABLE LienAuteurLivre(
	idLivre INTEGER,
	idAuteur INTEGER,
	PRIMARY KEY(idLivre,idAuteur)
	FOREIGN KEY(idLivre)
		REFERENCES Livre(idLivre)
	FOREIGN KEY(idAuteur)
		REFERENCES Auteur(idAuteur)
);

-- AUTEUR
INSERT INTO AUTEUR(nomAuteur,nomTraduit) VALUES("Inconnu","Inconnu");

-- CATEGORIE
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(1,"Littérature");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(2,"Traductions");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(3,"Critique littéraire");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(4,"Jeunesse");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(5,"Bande Dessiné");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(6,"Art");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(7,"Linguistique");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(8,"Droit");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(9,"Economie");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(10,"Histoire");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(11,"Philosophie");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(12,"Science");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(13,"Théologie");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(14,"Théatre");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(15,"Poésie");
INSERT INTO CATEGORIE(idCategorie,nomCategorie) VALUES(16,"Divers");

-- LANGUE
INSERT INTO LANGUE(idLangue,nomLangue) VALUES(1,"Français");
INSERT INTO LANGUE(idLangue,nomLangue) VALUES(2,"Russe");
INSERT INTO LANGUE(idLangue,nomLangue) VALUES(3,"Ukrainien");
INSERT INTO LANGUE(idLangue,nomLangue) VALUES(4,"Anglais");
INSERT INTO LANGUE(idLangue,nomLangue) VALUES(5,"Allemand");
INSERT INTO LANGUE(idLangue,nomLangue) VALUES(6,"Autre");