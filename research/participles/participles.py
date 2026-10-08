"""Past participles whose feminine is audible: the masculine ends in a silent
consonant (or in r) and the feminine says it. fait / faite, pris / prise,
ouvert / ouverte, peint / peinte.

FEMININE maps the masculine singular to the feminine singular.
FORMS maps every written form to (masculine singular, gender): "prises" -> ("pris", "f").
"""

FEMININE = {m: m + "e" for m in """
    fait refait défait satisfait
    écrit décrit inscrit prescrit réécrit transcrit retranscrit souscrit
    dit redit interdit prédit contredit maudit
    conduit reconduit construit reconstruit détruit produit reproduit traduit introduit
    réintroduit réduit séduit déduit induit instruit cuit
    ouvert rouvert réouvert couvert recouvert découvert redécouvert offert souffert
    peint repeint éteint atteint teint déteint craint plaint contraint joint rejoint feint
    astreint restreint enfreint
    mort
    pris appris compris repris surpris entrepris réappris
    mis admis commis émis omis permis promis remis soumis transmis compromis
    acquis conquis requis assis rassis inclus clos
""".split()}
FEMININE["dissous"] = "dissoute"

FORMS = {}
for m, f in FEMININE.items():
    FORMS[m] = (m, "m")
    FORMS[m if m.endswith("s") else m + "s"] = (m, "m")
    FORMS[f] = (m, "f")
    FORMS[f + "s"] = (m, "f")
