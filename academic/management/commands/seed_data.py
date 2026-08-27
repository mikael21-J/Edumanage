from django.core.management.base import BaseCommand
# Ajuste les imports si Niveau/Semestre sont situés ailleurs dans tes modèles
from accounts.models import Niveau  
from academic.models import Filiere, UE, Semestre


class Command(BaseCommand):
    help = "Peuple la base de données avec 10 UE par Niveau pour chaque Filière (120 UE total)"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Insertion des 120 UE dans la base de données..."))

        ues_data = [
            # Code, Intitulé, Crédits, Avec TP, Filière Code, Niveau, Semestre
            
            # =========================================================================
            # 1. INFORMATIQUE (INFO) - 30 UE (10 L1, 10 L2, 10 L3)
            # =========================================================================
            # --- INFO L1 ---
            ("INF111", "Introduction à l'Informatique", 4, False, "INFO", Niveau.L1, Semestre.S1),
            ("INF112", "Logique Formelle", 5, False, "INFO", Niveau.L1, Semestre.S1),
            ("INF121", "Algorithmique I", 6, True, "INFO", Niveau.L1, Semestre.S1),
            ("INF131", "Mathématiques Discrètes", 5, False, "INFO", Niveau.L1, Semestre.S1),
            ("INF141", "Anglais Technique I", 2, False, "INFO", Niveau.L1, Semestre.S1),
            ("INF122", "Algorithmique et Programmation II", 6, True, "INFO", Niveau.L1, Semestre.S2),
            ("INF134", "Architecture des Ordinateurs I", 5, True, "INFO", Niveau.L1, Semestre.S2),
            ("INF142", "Systèmes d'Exploitation I", 5, True, "INFO", Niveau.L1, Semestre.S2),
            ("INF151", "Technologies du Web I", 4, True, "INFO", Niveau.L1, Semestre.S2),
            ("INF162", "Analyse Numérique pour l'Info", 4, False, "INFO", Niveau.L1, Semestre.S2),

            # --- INFO L2 ---
            ("INF201", "Structures de Données", 6, True, "INFO", Niveau.L2, Semestre.S1),
            ("INF203", "Architecture des Ordinateurs II", 5, True, "INFO", Niveau.L2, Semestre.S1),
            ("INF205", "Bases de Données Relationnelles", 6, True, "INFO", Niveau.L2, Semestre.S1),
            ("INF207", "Théorie des Langages & Automates", 5, False, "INFO", Niveau.L2, Semestre.S1),
            ("INF209", "Probabilités & Statistiques pour l'Info", 4, False, "INFO", Niveau.L2, Semestre.S1),
            ("INF212", "Conception Orientée Objet", 6, True, "INFO", Niveau.L2, Semestre.S2),
            ("INF214", "Systèmes d'Exploitation II", 5, True, "INFO", Niveau.L2, Semestre.S2),
            ("INF216", "Introduction aux Réseaux", 5, True, "INFO", Niveau.L2, Semestre.S2),
            ("INF218", "Théorie des Graphes", 4, False, "INFO", Niveau.L2, Semestre.S2),
            ("INF220", "Développement Web Avancé", 4, True, "INFO", Niveau.L2, Semestre.S2),

            # --- INFO L3 ---
            ("INF301", "Réseaux Informatiques & Routage", 6, True, "INFO", Niveau.L3, Semestre.S1),
            ("INF303", "Génie Logiciel & Architecture DDD", 6, True, "INFO", Niveau.L3, Semestre.S1),
            ("INF305", "Bases de Données Avancées & NoSQL", 5, True, "INFO", Niveau.L3, Semestre.S1),
            ("INF307", "Compilation", 5, True, "INFO", Niveau.L3, Semestre.S1),
            ("INF309", "Recherche Opérationnelle & Optimisation", 4, False, "INFO", Niveau.L3, Semestre.S1),
            ("INF312", "Sécurité Informatique & Crypto", 5, True, "INFO", Niveau.L3, Semestre.S2),
            ("INF314", "Systèmes Distribués", 5, True, "INFO", Niveau.L3, Semestre.S2),
            ("INF316", "Introduction à l'IA & Machine Learning", 5, True, "INFO", Niveau.L3, Semestre.S2),
            ("INF318", "Développement d'Applications Mobiles", 5, True, "INFO", Niveau.L3, Semestre.S2),
            ("INF399", "Projet Tutoré & Stage", 6, True, "INFO", Niveau.L3, Semestre.S2),


            # =========================================================================
            # 2. MATHÉMATIQUES (MATH) - 30 UE (10 L1, 10 L2, 10 L3)
            # =========================================================================
            # --- MATH L1 ---
            ("MAT101", "Analyse I : Suites et Fonctions", 6, False, "MATH", Niveau.L1, Semestre.S1),
            ("MAT103", "Algèbre Linéaire I", 6, False, "MATH", Niveau.L1, Semestre.S1),
            ("MAT105", "Arithmétique et Logique", 5, False, "MATH", Niveau.L1, Semestre.S1),
            ("MAT107", "Géométrie Affine", 4, False, "MATH", Niveau.L1, Semestre.S1),
            ("MAT109", "Informatique pour Mathématiciens I", 3, True, "MATH", Niveau.L1, Semestre.S1),
            ("MAT102", "Analyse II : Intégration", 6, False, "MATH", Niveau.L1, Semestre.S2),
            ("MAT104", "Algèbre Linéaire II", 6, False, "MATH", Niveau.L1, Semestre.S2),
            ("MAT106", "Statistique Descriptive", 4, True, "MATH", Niveau.L1, Semestre.S2),
            ("MAT108", "Géométrie Euclidienne", 4, False, "MATH", Niveau.L1, Semestre.S2),
            ("MAT110", "Mécanique Rationnelle", 4, False, "MATH", Niveau.L1, Semestre.S2),

            # --- MATH L2 ---
            ("MAT201", "Analyse III : Séries et Intégrales", 6, False, "MATH", Niveau.L2, Semestre.S1),
            ("MAT203", "Algèbre Générale (Groupes, Anneaux)", 6, False, "MATH", Niveau.L2, Semestre.S1),
            ("MAT205", "Probabilités I", 5, False, "MATH", Niveau.L2, Semestre.S1),
            ("MAT207", "Topologie Généralisée", 5, False, "MATH", Niveau.L2, Semestre.S1),
            ("MAT209", "Analyse Numérique I", 4, True, "MATH", Niveau.L2, Semestre.S1),
            ("MAT202", "Analyse IV : Fonctions de Plus. Var.", 6, False, "MATH", Niveau.L2, Semestre.S2),
            ("MAT204", "Équations Différentielles Ordination", 6, False, "MATH", Niveau.L2, Semestre.S2),
            ("MAT206", "Statistique Inférentielle", 5, True, "MATH", Niveau.L2, Semestre.S2),
            ("MAT208", "Analyse Numérique II", 4, True, "MATH", Niveau.L2, Semestre.S2),
            ("MAT210", "Géométrie Différentielle I", 5, False, "MATH", Niveau.L2, Semestre.S2),

            # --- MATH L3 ---
            ("MAT301", "Mesure et Intégration (Lebesgue)", 6, False, "MATH", Niveau.L3, Semestre.S1),
            ("MAT303", "Théorie des Corps et Galois", 6, False, "MATH", Niveau.L3, Semestre.S1),
            ("MAT305", "Analyse Complexe", 6, False, "MATH", Niveau.L3, Semestre.S1),
            ("MAT307", "Recherche Opérationnelle", 4, True, "MATH", Niveau.L3, Semestre.S1),
            ("MAT309", "Optimisation Convexe", 4, False, "MATH", Niveau.L3, Semestre.S1),
            ("MAT302", "Analyse Fonctionnelle", 6, False, "MATH", Niveau.L3, Semestre.S2),
            ("MAT304", "Équations aux Dérivées Partielles", 6, False, "MATH", Niveau.L3, Semestre.S2),
            ("MAT306", "Processus Stochastiques", 5, False, "MATH", Niveau.L3, Semestre.S2),
            ("MAT308", "Géométrie Différentielle II", 5, False, "MATH", Niveau.L3, Semestre.S2),
            ("MAT399", "Mémoire / Projet de Fin d'Études", 4, False, "MATH", Niveau.L3, Semestre.S2),


            # =========================================================================
            # 3. PHYSIQUE (PHYS) - 30 UE (10 L1, 10 L2, 10 L3)
            # =========================================================================
            # --- PHYS L1 ---
            ("PHY101", "Mécanique du Point Matériel", 6, True, "PHYS", Niveau.L1, Semestre.S1),
            ("PHY103", "Thermodynamique I", 6, True, "PHYS", Niveau.L1, Semestre.S1),
            ("PHY105", "Mathématiques pour la Physique I", 5, False, "PHYS", Niveau.L1, Semestre.S1),
            ("PHY107", "Atomistique et Structure Matière", 4, False, "PHYS", Niveau.L1, Semestre.S1),
            ("PHY109", "Chimie Générale", 3, True, "PHYS", Niveau.L1, Semestre.S1),
            ("PHY102", "Électrostatique et Magnétostatique", 6, True, "PHYS", Niveau.L1, Semestre.S2),
            ("PHY104", "Optique Géométrique", 6, True, "PHYS", Niveau.L1, Semestre.S2),
            ("PHY106", "Mathématiques pour la Physique II", 5, False, "PHYS", Niveau.L1, Semestre.S2),
            ("PHY108", "Électrocinétique", 4, True, "PHYS", Niveau.L1, Semestre.S2),
            ("PHY110", "Informatique Appliquée à la Phys.", 3, True, "PHYS", Niveau.L1, Semestre.S2),

            # --- PHYS L2 ---
            ("PHY201", "Électromagnétisme dans le Vide", 6, True, "PHYS", Niveau.L2, Semestre.S1),
            ("PHY203", "Thermodynamique Statistiques I", 5, False, "PHYS", Niveau.L2, Semestre.S1),
            ("PHY205", "Mécanique des Solides", 5, True, "PHYS", Niveau.L2, Semestre.S1),
            ("PHY207", "Optique Ondulatoire", 5, True, "PHYS", Niveau.L2, Semestre.S1),
            ("PHY209", "Méthodes Mathématiques Phys. I", 4, False, "PHYS", Niveau.L2, Semestre.S1),
            ("PHY202", "Introduction Mécanique Quantique", 6, False, "PHYS", Niveau.L2, Semestre.S2),
            ("PHY204", "Électronique Analogique", 6, True, "PHYS", Niveau.L2, Semestre.S2),
            ("PHY206", "Vibrations et Ondes", 5, True, "PHYS", Niveau.L2, Semestre.S2),
            ("PHY208", "Relativité Restreinte", 4, False, "PHYS", Niveau.L2, Semestre.S2),
            ("PHY210", "Mesures Physiques & Instrumentation", 4, True, "PHYS", Niveau.L2, Semestre.S2),

            # --- PHYS L3 ---
            ("PHY301", "Mécanique Quantique Avancée", 6, False, "PHYS", Niveau.L3, Semestre.S1),
            ("PHY303", "Physique des Matériaux & Solides", 6, True, "PHYS", Niveau.L3, Semestre.S1),
            ("PHY305", "Physique Nucléaire", 5, False, "PHYS", Niveau.L3, Semestre.S1),
            ("PHY307", "Électronique Numérique", 5, True, "PHYS", Niveau.L3, Semestre.S1),
            ("PHY309", "Physique des Fluididité", 4, True, "PHYS", Niveau.L3, Semestre.S1),
            ("PHY312", "Physique Subatomique & Particules", 6, False, "PHYS", Niveau.L3, Semestre.S2),
            ("PHY314", "Physique du Semi-Conducteur", 5, True, "PHYS", Niveau.L3, Semestre.S2),
            ("PHY316", "Optique Quantique et Lasers", 5, True, "PHYS", Niveau.L3, Semestre.S2),
            ("PHY318", "Astrophysique & Cosmologie", 4, False, "PHYS", Niveau.L3, Semestre.S2),
            ("PHY399", "Projet de Laboratoire / Stage", 5, True, "PHYS", Niveau.L3, Semestre.S2),


            # =========================================================================
            # 4. ICT (INFORMATION & COMMUNICATION TECHNOLOGY) - 30 UE (10 L1, 10 L2, 10 L3)
            # =========================================================================
            # --- ICT L1 ---
            ("ICT101", "Introduction aux ICT & Web", 5, True, "ICT", Niveau.L1, Semestre.S1),
            ("ICT103", "Algorithmique et Logique", 6, True, "ICT", Niveau.L1, Semestre.S1),
            ("ICT105", "Fondements des Réseaux", 5, True, "ICT", Niveau.L1, Semestre.S1),
            ("ICT107", "Mathématiques pour l'ICT I", 4, False, "ICT", Niveau.L1, Semestre.S1),
            ("ICT109", "Bureautique et Systèmes", 4, True, "ICT", Niveau.L1, Semestre.S1),
            ("ICT102", "Programmation Python / C", 6, True, "ICT", Niveau.L1, Semestre.S2),
            ("ICT104", "Introduction aux SGBD", 5, True, "ICT", Niveau.L1, Semestre.S2),
            ("ICT106", "Architecture des Équipements ICT", 5, True, "ICT", Niveau.L1, Semestre.S2),
            ("ICT108", "Mathématiques pour l'ICT II", 4, False, "ICT", Niveau.L1, Semestre.S2),
            ("ICT110", "Expression Écrite et Communication", 3, False, "ICT", Niveau.L1, Semestre.S2),

            # --- ICT L2 ---
            ("ICT201", "Administration Système Linux", 6, True, "ICT", Niveau.L2, Semestre.S1),
            ("ICT203", "Conception Web (Front-End/Back-End)", 6, True, "ICT", Niveau.L2, Semestre.S1),
            ("ICT205", "Réseaux d'Entreprise (CCNA 1)", 5, True, "ICT", Niveau.L2, Semestre.S1),
            ("ICT207", "Systèmes de Gestion de BD SQL", 5, True, "ICT", Niveau.L2, Semestre.S1),
            ("ICT209", "Probabilités & Stats appliquées", 4, False, "ICT", Niveau.L2, Semestre.S1),
            ("ICT202", "Développement Mobile (Flutter/React)", 6, True, "ICT", Niveau.L2, Semestre.S2),
            ("ICT204", "Commutation et Routage (CCNA 2)", 5, True, "ICT", Niveau.L2, Semestre.S2),
            ("ICT206", "Services Réseaux (DNS, DHCP, Mail)", 5, True, "ICT", Niveau.L2, Semestre.S2),
            ("ICT208", "Sécurité des SI - Notions de Base", 5, True, "ICT", Niveau.L2, Semestre.S2),
            ("ICT210", "Droit de l'Informatique & Télécoms", 3, False, "ICT", Niveau.L2, Semestre.S2),

            # --- ICT L3 ---
            ("ICT301", "Cloud Computing & DevOps", 6, True, "ICT", Niveau.L3, Semestre.S1),
            ("ICT303", "Cybersécurité Appliquée & Hardening", 6, True, "ICT", Niveau.L3, Semestre.S1),
            ("ICT305", "Réseaux Sans-Fil et Mobiles", 5, True, "ICT", Niveau.L3, Semestre.S1),
            ("ICT307", "Administration Systèmes Windows/Active Directory", 5, True, "ICT", Niveau.L3, Semestre.S1),
            ("ICT309", "Gestion de Projet IT & Agile", 4, False, "ICT", Niveau.L3, Semestre.S1),
            ("ICT302", "Virtualisation et Conteneurisation (Docker)", 5, True, "ICT", Niveau.L3, Semestre.S2),
            ("ICT304", "IoT (Internet des Objets) & Télécoms", 5, True, "ICT", Niveau.L3, Semestre.S2),
            ("ICT306", "Audits et Pare-feu (Firewalls & Tunnels)", 5, True, "ICT", Niveau.L3, Semestre.S2),
            ("ICT308", "Big Data & Introduction Analytics", 4, True, "ICT", Niveau.L3, Semestre.S2),
            ("ICT399", "Projet Professionnel & Stage ICT", 6, True, "ICT", Niveau.L3, Semestre.S2),
        ]

        count = 0
        for code_ue, intitule, credits, avec_tp, fil_code, niv, sem in ues_data:
            filiere_obj = Filiere.objects.get(code_filiere=fil_code)
            _, created = UE.objects.get_or_create(
                code_ue=code_ue,
                defaults={
                    "intitule": intitule,
                    "credits": credits,
                    "avec_tp": avec_tp,
                    "filiere": filiere_obj,
                    "niveau": niv,
                    "semestre": sem,
                },
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"✓ {len(ues_data)} UE ont été traitées (dont {count} nouvelles créées) !"))