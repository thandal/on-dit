"""Verb forms for the subjunctive count.

A token is counted only if its subjunctive and its present indicative sound
different for the person used:

- OWN: verbs with their own subjunctive stem (6.5's six, plus vouloir, falloir,
  valoir, pleuvoir). Different for every person, except j'ai / j'aie, which many
  speakers say the same way; those are set aside.
- TWO_STEM: two-stem verbs (4.2). The subjunctive takes the long stem, so it
  differs from the present for je, tu, il, on (qu'il parte / il part) but not for
  ils (qu'ils partent / ils partent).
- With vous (and nous), every verb differs: que vous partiez / vous partez.

Verbs whose subjunctive sounds like the present for every singular person
(all -er verbs, voir, croire, courir, mourir, rire, ouvrir...) aren't counted.
"""

OWN = {
    "être": ("sois soit soient soyons soyez soye soyes", "suis es est sommes êtes sont"),
    "avoir": ("aie aies ait aient ayons ayez", "ai as a avons avez ont"),
    "aller": ("aille ailles aillent allions alliez", "vais vas va allons allez vont"),
    "faire": ("fasse fasses fassent fassions fassiez", "fais fait faisons faites font"),
    "refaire": ("refasse refasses refassent", "refais refait refont"),
    "pouvoir": ("puisse puisses puissent puissions puissiez", "peux peut pouvons pouvez peuvent"),
    "savoir": ("sache saches sachent sachions sachiez", "sais sait savons savez savent"),
    "vouloir": ("veuille veuilles veuillent voulions vouliez", "veux veut voulons voulez veulent"),
    "falloir": ("faille", "faut"),
    "valoir": ("vaille vaillent", "vaut vaux valent"),
    "pleuvoir": ("pleuve", "pleut"),
}

# lemma: (ils form, singular present forms). Subjunctive je/tu/il = ils form minus -nt.
TWO_STEM = {
    "partir": ("partent", "part pars"), "repartir": ("repartent", "repart repars"),
    "sortir": ("sortent", "sort sors"), "ressortir": ("ressortent", "ressort ressors"),
    "dormir": ("dorment", "dort dors"), "endormir": ("endorment", "endort endors"),
    "servir": ("servent", "sert sers"), "sentir": ("sentent", "sent sens"),
    "ressentir": ("ressentent", "ressent ressens"), "mentir": ("mentent", "ment mens"),
    "finir": ("finissent", "finit finis"), "choisir": ("choisissent", "choisit choisis"),
    "réussir": ("réussissent", "réussit réussis"), "grandir": ("grandissent", "grandit grandis"),
    "réfléchir": ("réfléchissent", "réfléchit réfléchis"), "remplir": ("remplissent", "remplit remplis"),
    "agir": ("agissent", "agit agis"), "réagir": ("réagissent", "réagit réagis"),
    "établir": ("établissent", "établit établis"), "fournir": ("fournissent", "fournit fournis"),
    "investir": ("investissent", "investit investis"), "définir": ("définissent", "définit définis"),
    "garantir": ("garantissent", "garantit garantis"), "saisir": ("saisissent", "saisit saisis"),
    "réunir": ("réunissent", "réunit réunis"), "aboutir": ("aboutissent", "aboutit aboutis"),
    "nourrir": ("nourrissent", "nourrit nourris"), "vieillir": ("vieillissent", "vieillit vieillis"),
    "ralentir": ("ralentissent", "ralentit ralentis"), "avertir": ("avertissent", "avertit avertis"),
    "obéir": ("obéissent", "obéit obéis"), "punir": ("punissent", "punit punis"),
    "lire": ("lisent", "lit lis"), "relire": ("relisent", "relit relis"), "élire": ("élisent", "élit élis"),
    "dire": ("disent", "dit dis"), "redire": ("redisent", "redit redis"),
    "interdire": ("interdisent", "interdit interdis"), "suffire": ("suffisent", "suffit suffis"),
    "écrire": ("écrivent", "écrit écris"), "décrire": ("décrivent", "décrit décris"),
    "inscrire": ("inscrivent", "inscrit inscris"),
    "conduire": ("conduisent", "conduit conduis"), "produire": ("produisent", "produit produis"),
    "réduire": ("réduisent", "réduit réduis"), "traduire": ("traduisent", "traduit traduis"),
    "construire": ("construisent", "construit construis"), "détruire": ("détruisent", "détruit détruis"),
    "introduire": ("introduisent", "introduit introduis"),
    "connaître": ("connaissent", "connaît connait connais"),
    "reconnaître": ("reconnaissent", "reconnaît reconnait reconnais"),
    "paraître": ("paraissent", "paraît parait parais"),
    "apparaître": ("apparaissent", "apparaît apparait apparais"),
    "disparaître": ("disparaissent", "disparaît disparait disparais"),
    "naître": ("naissent", "naît nait nais"),
    "plaire": ("plaisent", "plaît plait plais"), "taire": ("taisent", "tait tais"),
    "attendre": ("attendent", "attend attends"), "entendre": ("entendent", "entend entends"),
    "répondre": ("répondent", "répond réponds"), "vendre": ("vendent", "vend vends"),
    "perdre": ("perdent", "perd perds"), "descendre": ("descendent", "descend descends"),
    "rendre": ("rendent", "rend rends"), "défendre": ("défendent", "défend défends"),
    "dépendre": ("dépendent", "dépend dépends"), "tendre": ("tendent", "tend tends"),
    "étendre": ("étendent", "étend étends"), "prétendre": ("prétendent", "prétend prétends"),
    "correspondre": ("correspondent", "correspond corresponds"),
    "confondre": ("confondent", "confond confonds"), "fondre": ("fondent", "fond fonds"),
    "mettre": ("mettent", "met mets"), "remettre": ("remettent", "remet remets"),
    "permettre": ("permettent", "permet permets"), "promettre": ("promettent", "promet promets"),
    "admettre": ("admettent", "admet admets"), "transmettre": ("transmettent", "transmet transmets"),
    "battre": ("battent", "bat bats"), "débattre": ("débattent", "débat débats"),
    "vivre": ("vivent", "vit vis"), "survivre": ("survivent", "survit survis"),
    "suivre": ("suivent", "suit suis"), "poursuivre": ("poursuivent", "poursuit poursuis"),
    "venir": ("viennent", "vient viens"), "revenir": ("reviennent", "revient reviens"),
    "devenir": ("deviennent", "devient deviens"), "parvenir": ("parviennent", "parvient parviens"),
    "intervenir": ("interviennent", "intervient interviens"),
    "prévenir": ("préviennent", "prévient préviens"), "convenir": ("conviennent", "convient conviens"),
    "souvenir": ("souviennent", "souvient souviens"),
    "tenir": ("tiennent", "tient tiens"), "obtenir": ("obtiennent", "obtient obtiens"),
    "retenir": ("retiennent", "retient retiens"), "maintenir": ("maintiennent", "maintient maintiens"),
    "appartenir": ("appartiennent", "appartient appartiens"), "contenir": ("contiennent", "contient contiens"),
    "prendre": ("prennent", "prend prends"), "comprendre": ("comprennent", "comprend comprends"),
    "apprendre": ("apprennent", "apprend apprends"), "reprendre": ("reprennent", "reprend reprends"),
    "surprendre": ("surprennent", "surprend surprends"),
    "entreprendre": ("entreprennent", "entreprend entreprends"),
    "devoir": ("doivent", "doit dois"), "boire": ("boivent", "boit bois"),
    "recevoir": ("reçoivent", "reçoit reçois"), "apercevoir": ("aperçoivent", "aperçoit aperçois"),
    "décevoir": ("déçoivent", "déçoit déçois"),
    "craindre": ("craignent", "craint crains"), "plaindre": ("plaignent", "plaint plains"),
    "rejoindre": ("rejoignent", "rejoint rejoins"), "joindre": ("joignent", "joint joins"),
    "atteindre": ("atteignent", "atteint atteins"), "éteindre": ("éteignent", "éteint éteins"),
    "peindre": ("peignent", "peint peins"),
    "convaincre": ("convainquent", "convainc convaincs"),
    "résoudre": ("résolvent", "résout résous"),
    "interrompre": ("interrompent", "interrompt interromps"),
}

# Future stems that aren't the infinitive (used to spot futur and conditionnel).
FUT_STEM = {
    "être": "ser", "avoir": "aur", "aller": "ir", "faire": "fer", "refaire": "refer",
    "pouvoir": "pourr", "savoir": "saur", "vouloir": "voudr", "falloir": "faudr",
    "valoir": "vaudr", "pleuvoir": "pleuvr", "devoir": "devr", "recevoir": "recevr",
    "apercevoir": "apercevr", "décevoir": "décevr", "voir": "verr", "revoir": "reverr",
    "envoyer": "enverr", "courir": "courr", "mourir": "mourr",
}
for _l in TWO_STEM:
    if _l.endswith("venir"):
        FUT_STEM[_l] = _l[:-5] + "viendr"
    elif _l.endswith("tenir"):
        FUT_STEM[_l] = _l[:-5] + "tiendr"


def fut_stem(lemma):
    if lemma in FUT_STEM:
        return FUT_STEM[lemma]
    return lemma[:-1] if lemma.endswith("re") else lemma


# Lemma corrections: the tagger lemmatizes faut as faillir and aille as ailler.
LEMMA_FIX = {"faillir": "falloir", "ailler": "aller", "saurer": "savoir"}

# form -> (lemma, "subj" | "pres", forms only for these persons or None)
FORMS = {}
for _l, (_subj, _pres) in OWN.items():
    for _f in _subj.split():
        FORMS[_f] = (_l, "subj")
    for _f in _pres.split():
        FORMS.setdefault(_f, (_l, "pres"))
for _l, (_ils, _sg) in TWO_STEM.items():
    _s = _ils[:-2]
    FORMS.setdefault(_s, (_l, "subj"))
    FORMS.setdefault(_s + "s", (_l, "subj"))
    for _f in _sg.split():
        FORMS.setdefault(_f, (_l, "pres"))
    FORMS.setdefault(_ils, (_l, "same"))  # ils partent: subjunctive = present
FORMS["suis"] = ("être", "pres")
FORMS["vit"] = ("vivre", "pres")

DISTINCT = set(OWN) | set(TWO_STEM)


def classify(form, lemma, person):
    """Return (lemma, mood, counted).

    mood: subj, pres, imparfait, futur, conditionnel, same (sounds the same in
    both moods for this person), other. counted: whether the token goes in the
    subjunctive / indicative count.
    """
    form = form.lower()
    lemma = LEMMA_FIX.get(lemma, lemma)
    plural = person in ("ils", "pl")
    if form in FORMS:
        lem, mood = FORMS[form]
        if mood == "same":
            return lem, "same", False
        if lem == "avoir" and person == "je" and form in ("ai", "aie"):
            return lem, mood, False  # j'ai / j'aie: same sound for many speakers
        if lem in TWO_STEM and plural:
            return lem, mood, False  # ils + two-stem: not comparable
        return lem, mood, True
    stem = fut_stem(lemma)
    for end in ("ai", "as", "a", "ons", "ez", "ont"):
        if form == stem + end:
            return lemma, "futur", lemma in DISTINCT or person in ("vous", "nous")
    for end in ("ais", "ait", "aient", "ions", "iez"):
        if form == stem + end:
            return lemma, "conditionnel", lemma in DISTINCT or person in ("vous", "nous")
    if person in ("vous", "nous"):
        sub, ind = ("iez", "ez") if person == "vous" else ("ions", "ons")
        if form.endswith(("y" + ind, "y" + sub, "i" + sub)) or lemma.endswith(("ier", "rire")):
            return lemma, "same", False  # voyez / voyiez, étudiez / étudiiez: same sound
        if lemma in OWN and form.endswith(sub):
            return lemma, "imparfait", True  # étiez, aviez, faisiez...
        if form.endswith(sub) and not (lemma.endswith(("ier", "rire")) and not form.endswith("i" + sub)):
            return lemma, "subj", True  # also the imparfait form for most verbs
        if form.endswith(ind) or form in ("êtes", "faites", "dites"):
            return lemma, "pres", True
        return lemma, "other", False
    if lemma in DISTINCT and form.endswith(("ais", "ait", "aient")):
        return lemma, "imparfait", True
    if lemma in DISTINCT:
        return lemma, "other", False
    return lemma, "same", False
