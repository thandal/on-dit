"""Present-tense forms of the verbs checked: lemma -> (ils form, singular forms).

The first form in each singular list is the il form, used as the short-stem
pronunciation when scoring audio."""

TWO_STEM = {
    # 4.2, first table: ils form = long stem, singular = long stem minus its consonant
    "partir": ("partent", "part pars"), "sortir": ("sortent", "sort sors"),
    "dormir": ("dorment", "dort dors"), "servir": ("servent", "sert sers"),
    "sentir": ("sentent", "sent sens"), "mentir": ("mentent", "ment mens"),
    "finir": ("finissent", "finit finis"), "choisir": ("choisissent", "choisit choisis"),
    "réussir": ("réussissent", "réussit réussis"), "grandir": ("grandissent", "grandit grandis"),
    "lire": ("lisent", "lit lis"), "dire": ("disent", "dit dis"),
    "écrire": ("écrivent", "écrit écris"), "conduire": ("conduisent", "conduit conduis"),
    "connaître": ("connaissent", "connaît connait connais"),
    "attendre": ("attendent", "attend attends"), "entendre": ("entendent", "entend entends"),
    "répondre": ("répondent", "répond réponds"), "vendre": ("vendent", "vend vends"),
    "perdre": ("perdent", "perd perds"), "descendre": ("descendent", "descend descends"),
    "rendre": ("rendent", "rend rends"), "mettre": ("mettent", "met mets"),
    "permettre": ("permettent", "permet permets"), "vivre": ("vivent", "vit vis"),
    "suivre": ("suivent", "suit suis"), "plaire": ("plaisent", "plaît plait plais"),
    "savoir": ("savent", "sait sais"),
    # 4.2, second table: the vous form also changes vowel
    "venir": ("viennent", "vient viens"), "devenir": ("deviennent", "devient deviens"),
    "revenir": ("reviennent", "revient reviens"), "tenir": ("tiennent", "tient tiens"),
    "obtenir": ("obtiennent", "obtient obtiens"), "prendre": ("prennent", "prend prends"),
    "comprendre": ("comprennent", "comprend comprends"),
    "apprendre": ("apprennent", "apprend apprends"),
    "pouvoir": ("peuvent", "peut peux"), "vouloir": ("veulent", "veut veux"),
    "devoir": ("doivent", "doit dois"), "boire": ("boivent", "boit bois"),
    "recevoir": ("reçoivent", "reçoit reçois"),
}

CORE = {
    "être": ("sont", "est suis es"), "avoir": ("ont", "a ai as"),
    "aller": ("vont", "va vais vas"), "faire": ("font", "fait fais"),
}

ALL = {**TWO_STEM, **CORE}

# form -> [(lemma, "long" | "short")]
FORMS = {}
for lemma, (long_, short) in ALL.items():
    for f in long_.split():
        FORMS.setdefault(f, []).append((lemma, "long"))
    for f in short.split():
        FORMS.setdefault(f, []).append((lemma, "short"))
FORMS["suis"] = [("suivre", "short")]  # after ils/il, suis is suivre, not être

# Control: one-form verbs whose il form ends in a consonant that is always said
# (il reste, il pense). Scored as "form" against "form minus its last sound", they
# show how often the method misses a final consonant that is really there.
CONTROL = ("reste pense aime parle passe donne trouve arrive demande garde regarde "
           "achète explique raconte monte compte cherche laisse porte quitte rentre "
           "coûte change mange travaille").split()
