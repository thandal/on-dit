"""Shared reader for the CEFC-ORFEO transcripts (see ils-stems/fetch.sh to download).

    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from orfeo import SPOKEN_FRANCE, documents, sentences, speakers

Each token is the list of .orfeo columns:
    0 id, 1 form, 2 lemma, 3 POS, 4 POS, 5 -, 6 head, 7 deprel, 8 -, 9 -,
    10 start (s), 11 end (s), 12 speaker id
"""
import glob, os, re

# Spoken, recorded in France. Left out: cfpb, valibel (Belgium), ofrom (Switzerland)
# and the written corpora.
SPOKEN_FRANCE = ["cfpp", "clapi", "coralrom", "crfp", "decoda", "fleuron",
                 "frenchoralnarrative", "reunions-de-travail", "tcof", "tufs"]

AUDIO_BASE = "https://repository.ortolang.fr/api/content/cefc-orfeo/latest/oral"


def documents(root, corpora=SPOKEN_FRANCE):
    """Yield (corpus, doc, path) for every .orfeo file."""
    for corpus in corpora:
        for path in sorted(glob.glob(os.path.join(root, corpus, "*.orfeo"))):
            yield corpus, os.path.basename(path)[:-len(".orfeo")], path


def sentences(path):
    """Yield each sentence of an .orfeo file as a list of token column lists."""
    sent = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                if sent:
                    yield sent
                sent = []
            elif not line.startswith("#"):
                cols = line.split("\t")
                if len(cols) >= 13:
                    sent.append(cols)
    if sent:
        yield sent


def speakers(root, corpus, doc):
    """Speaker metadata from the .xml beside the .orfeo: {id: {field: value}}."""
    path = os.path.join(root, corpus, doc + ".xml")
    if not os.path.exists(path):
        return {}
    xml = open(path, encoding="utf-8").read()
    out = {}
    for pid, body in re.findall(r'<person xml:id="([^"]+)">(.*?)</person>', xml, re.S):
        info = {}
        for field in ("sex", "age", "education", "occupation"):
            m = re.search(rf"<{field}>(.*?)</{field}>", body, re.S)
            if m:
                info[field] = " ".join(m.group(1).split())
        m = re.search(r'level="langue_maternelle">(.*?)<', body)
        info["first_language"] = m.group(1).strip() if m else ""
        out[pid] = info
    return out
