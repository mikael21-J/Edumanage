-- Schema SQL SQLite correspondant aux modeles metier Django EduManage.
-- Ce fichier est documentaire et n'est pas execute automatiquement par Django.

PRAGMA foreign_keys = ON;

CREATE TABLE academic_faculte (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_fac VARCHAR(20) NOT NULL UNIQUE,
    nom_fac VARCHAR(150) NOT NULL
);

CREATE TABLE academic_departement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_dept VARCHAR(20) NOT NULL UNIQUE,
    nom_dept VARCHAR(150) NOT NULL,
    faculte_id INTEGER NOT NULL,
    FOREIGN KEY (faculte_id) REFERENCES academic_faculte(id) ON DELETE CASCADE
);

CREATE TABLE academic_filiere (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_filiere VARCHAR(20) NOT NULL UNIQUE,
    nom_filiere VARCHAR(150) NOT NULL,
    departement_id INTEGER,
    FOREIGN KEY (departement_id) REFERENCES academic_departement(id) ON DELETE CASCADE
);

CREATE TABLE accounts_etudiant (
    matricule VARCHAR(50) PRIMARY KEY,
    mot_de_passe VARCHAR(128) NOT NULL DEFAULT '',
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    date_naissance DATE NOT NULL,
    lieu_naissance VARCHAR(100) NOT NULL,
    region VARCHAR(20) NOT NULL CHECK (region IN (
        'ADAMAOUA', 'CENTRE', 'EST', 'EXTREME_NORD', 'LITTORAL',
        'NORD', 'NORD_OUEST', 'OUEST', 'SUD', 'SUD_OUEST'
    )),
    filiere_id INTEGER,
    niveau VARCHAR(2) NOT NULL CHECK (niveau IN ('L1', 'L2', 'L3', 'M1', 'M2')),
    FOREIGN KEY (filiere_id) REFERENCES academic_filiere(id) ON DELETE CASCADE
);

CREATE TABLE accounts_enseignant (
    matricule VARCHAR(50) PRIMARY KEY,
    mot_de_passe VARCHAR(128) NOT NULL DEFAULT '',
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    fonction VARCHAR(100) NOT NULL
);

CREATE TABLE academic_ue (
    code_ue VARCHAR(20) PRIMARY KEY,
    intitule VARCHAR(150) NOT NULL,
    credits INTEGER NOT NULL CHECK (credits >= 0),
    avec_tp BOOLEAN NOT NULL DEFAULT 0,
    filiere_id INTEGER NOT NULL,
    niveau VARCHAR(2) NOT NULL CHECK (niveau IN ('L1', 'L2', 'L3', 'M1', 'M2')),
    semestre VARCHAR(2) NOT NULL CHECK (semestre IN ('S1', 'S2')),
    FOREIGN KEY (filiere_id) REFERENCES academic_filiere(id) ON DELETE CASCADE
);

CREATE TABLE academic_enseignantue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enseignant_id VARCHAR(50) NOT NULL,
    ue_id VARCHAR(20) NOT NULL,
    date_declaration DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (enseignant_id, ue_id),
    FOREIGN KEY (enseignant_id) REFERENCES accounts_enseignant(matricule) ON DELETE CASCADE,
    FOREIGN KEY (ue_id) REFERENCES academic_ue(code_ue) ON DELETE CASCADE
);

CREATE TABLE pedagogy_inscriptionue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id VARCHAR(50) NOT NULL,
    ue_id VARCHAR(20) NOT NULL,
    annee_academique VARCHAR(20) NOT NULL DEFAULT '2025-2026',
    date_inscription DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (etudiant_id, ue_id, annee_academique),
    FOREIGN KEY (etudiant_id) REFERENCES accounts_etudiant(matricule) ON DELETE CASCADE,
    FOREIGN KEY (ue_id) REFERENCES academic_ue(code_ue) ON DELETE CASCADE
);

CREATE TABLE pedagogy_classe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ue_id VARCHAR(20) NOT NULL,
    enseignant_id VARCHAR(50) NOT NULL,
    annee_academique VARCHAR(20) NOT NULL DEFAULT '2025-2026',
    UNIQUE (ue_id, annee_academique),
    FOREIGN KEY (ue_id) REFERENCES academic_ue(code_ue) ON DELETE CASCADE,
    FOREIGN KEY (enseignant_id) REFERENCES accounts_enseignant(matricule) ON DELETE CASCADE
);

CREATE TABLE pedagogy_note (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id VARCHAR(50) NOT NULL,
    ue_id VARCHAR(20) NOT NULL,
    type_evaluation VARCHAR(3) NOT NULL CHECK (type_evaluation IN ('CC', 'TP', 'SN', 'RAT')),
    valeur_note DECIMAL(4,2) CHECK (valeur_note >= 0 AND valeur_note <= 20),
    est_publie BOOLEAN NOT NULL DEFAULT 0,
    UNIQUE (etudiant_id, ue_id, type_evaluation),
    FOREIGN KEY (etudiant_id) REFERENCES accounts_etudiant(matricule) ON DELETE CASCADE,
    FOREIGN KEY (ue_id) REFERENCES academic_ue(code_ue) ON DELETE CASCADE
);
