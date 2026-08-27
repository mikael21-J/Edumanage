from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


OUTPUT = Path(__file__).with_name('modele_relationnel.pdf')
PAGE_WIDTH, PAGE_HEIGHT = landscape(A3)

ENTITIES = {
    'Faculte': ['id PK', 'code_fac VARCHAR(20) UNIQUE', 'nom_fac VARCHAR(150)'],
    'Departement': ['id PK', 'code_dept VARCHAR(20) UNIQUE', 'nom_dept VARCHAR(150)', 'faculte_id FK'],
    'Filiere': ['id PK', 'code_filiere VARCHAR(20) UNIQUE', 'nom_filiere VARCHAR(150)', 'departement_id FK NULL'],
    'Etudiant': ['matricule PK', 'mot_de_passe VARCHAR(128)', 'nom VARCHAR(100)', 'prenom VARCHAR(100)', 'filiere_id FK NULL', 'niveau L1/L2/L3/M1/M2'],
    'Enseignant': ['matricule PK', 'mot_de_passe VARCHAR(128)', 'nom VARCHAR(100)', 'prenom VARCHAR(100)', 'fonction VARCHAR(100)'],
    'UE': ['code_ue PK', 'intitule VARCHAR(150)', 'credits INTEGER', 'avec_tp BOOLEAN', 'filiere_id FK', 'niveau L1/L2/L3/M1/M2', 'semestre S1/S2'],
    'EnseignantUE': ['id PK', 'enseignant_id FK', 'ue_id FK', 'date_declaration DATETIME', 'UNIQUE enseignant_id + ue_id'],
    'InscriptionUE': ['id PK', 'etudiant_id FK', 'ue_id FK', 'annee_academique VARCHAR(20)', 'date_inscription DATETIME', 'UNIQUE etudiant_id + ue_id + annee'],
    'Classe': ['id PK', 'ue_id FK', 'enseignant_id FK', 'annee_academique VARCHAR(20)', 'UNIQUE ue_id + annee'],
    'Note': ['id PK', 'etudiant_id FK', 'ue_id FK', 'type_evaluation CC/TP/SN/RAT', 'valeur_note DECIMAL(4,2)', 'est_publie BOOLEAN', 'UNIQUE etudiant_id + ue_id + type'],
}

POSITIONS = {
    'Faculte': (70, 570), 'Departement': (330, 570), 'Filiere': (610, 570),
    'Etudiant': (70, 285), 'Enseignant': (350, 285), 'UE': (650, 285),
    'EnseignantUE': (970, 570), 'InscriptionUE': (970, 285), 'Classe': (970, 65), 'Note': (650, 65),
}
BOX_WIDTH = 220
HEADER_HEIGHT = 30
LINE_HEIGHT = 17

RELATIONS = [
    ('Faculte', 'Departement', '1', '0..N'),
    ('Departement', 'Filiere', '1', '0..N'),
    ('Filiere', 'Etudiant', '1', '0..N'),
    ('Filiere', 'UE', '1', '0..N'),
    ('Enseignant', 'EnseignantUE', '1', '0..N'),
    ('UE', 'EnseignantUE', '1', '0..N'),
    ('Etudiant', 'InscriptionUE', '1', '0..N'),
    ('UE', 'InscriptionUE', '1', '0..N'),
    ('Enseignant', 'Classe', '1', '0..N'),
    ('UE', 'Classe', '1', '0..N'),
    ('Etudiant', 'Note', '1', '0..N'),
    ('UE', 'Note', '1', '0..N'),
]


def box_height(fields):
    return HEADER_HEIGHT + 12 + len(fields) * LINE_HEIGHT


def center_of(name):
    x, y = POSITIONS[name]
    return x + BOX_WIDTH / 2, y + box_height(ENTITIES[name]) / 2


def edge_point(name, target):
    x, y = POSITIONS[name]
    tx, ty = center_of(target)
    cx, cy = center_of(name)
    height = box_height(ENTITIES[name])
    if abs(tx - cx) > abs(ty - cy):
        return (x + BOX_WIDTH if tx > cx else x, cy)
    return (cx, y + height if ty > cy else y)


def draw_arrow(pdf, start, end, label, label_offset=(0, 0)):
    pdf.setStrokeColor(colors.HexColor('#8a93a8'))
    pdf.setLineWidth(1.2)
    pdf.line(start[0], start[1], end[0], end[1])
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    left = (end[0] - ux * 9 - uy * 4, end[1] - uy * 9 + ux * 4)
    right = (end[0] - ux * 9 + uy * 4, end[1] - uy * 9 - ux * 4)
    pdf.setFillColor(colors.HexColor('#8a93a8'))
    pdf.line(end[0], end[1], left[0], left[1])
    pdf.line(end[0], end[1], right[0], right[1])
    mx, my = (start[0] + end[0]) / 2 + label_offset[0], (start[1] + end[1]) / 2 + label_offset[1]
    pdf.setFillColor(colors.HexColor('#4f5b73'))
    pdf.setFont('Helvetica', 8)
    pdf.drawCentredString(mx, my, label)


def draw_entity(pdf, name, fields):
    x, y = POSITIONS[name]
    height = box_height(fields)
    pdf.setFillColor(colors.white)
    pdf.setStrokeColor(colors.HexColor('#b9c2d5'))
    pdf.setLineWidth(1)
    pdf.roundRect(x, y, BOX_WIDTH, height, 7, fill=1, stroke=1)
    pdf.setFillColor(colors.HexColor('#004ac6'))
    pdf.roundRect(x, y + height - HEADER_HEIGHT, BOX_WIDTH, HEADER_HEIGHT, 7, fill=1, stroke=0)
    pdf.rect(x, y + height - HEADER_HEIGHT, BOX_WIDTH, 7, fill=1, stroke=0)
    pdf.setFillColor(colors.white)
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(x + 10, y + height - 20, name)
    pdf.setFillColor(colors.HexColor('#26334d'))
    pdf.setFont('Helvetica', 8.5)
    for index, field in enumerate(fields):
        pdf.drawString(x + 10, y + height - HEADER_HEIGHT - 17 - index * LINE_HEIGHT, field)


def build_pdf():
    pdf = canvas.Canvas(str(OUTPUT), pagesize=landscape(A3))
    pdf.setTitle('Modele relationnel EduManage')
    pdf.setAuthor('EduManage')
    pdf.setFillColor(colors.HexColor('#131b2e'))
    pdf.setFont('Helvetica-Bold', 22)
    pdf.drawString(55, PAGE_HEIGHT - 48, 'Modele relationnel - EduManage')
    pdf.setFillColor(colors.HexColor('#5f6678'))
    pdf.setFont('Helvetica', 10)
    pdf.drawString(55, PAGE_HEIGHT - 66, 'Entites, champs principaux et relations du projet')

    for source, target, source_card, target_card in RELATIONS:
        start = edge_point(source, target)
        end = edge_point(target, source)
        offset = (0, 8) if abs(start[0] - end[0]) > abs(start[1] - end[1]) else (12, 0)
        draw_arrow(pdf, start, end, f'{source_card}    {target_card}', offset)

    for name, fields in ENTITIES.items():
        draw_entity(pdf, name, fields)

    pdf.setFillColor(colors.HexColor('#5f6678'))
    pdf.setFont('Helvetica', 8)
    pdf.drawString(55, 28, 'PK = cle primaire | FK = cle etrangere | UNIQUE = contrainte d unicite | 1 et 0..N = cardinalites')
    pdf.save()


if __name__ == '__main__':
    build_pdf()
    print(OUTPUT)
