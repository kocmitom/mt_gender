""" Usage:
    <file-name> --ds=DATASET_FILE --bi=IN_FILE --align=ALIGN_FILE --lang=LANG [--debug]
"""
# External imports
import logging
import pdb
from pprint import pprint
from pprint import pformat
from docopt import docopt
from collections import defaultdict, Counter
from operator import itemgetter
from tqdm import tqdm
from typing import List

# Local imports
from languages.spacy_support import SpacyPredictor
#=-----

LANGAUGE_PREDICTOR = {
    "es": SpacyPredictor("es")
}

def get_src_indices(instance: List[str]) -> List[int]:
    """
    (English)
    Determine a list of source side indices pertaining to a
    given instance in the dataset.
    """
    _, src_word_ind, sent = instance
    src_word_ind = int(src_word_ind)
    sent_tok = sent.split(" ")
    if (src_word_ind > 0) and (sent_tok[src_word_ind - 1].lower() in ["the", "an", "a"]):
        src_indices = [src_word_ind -1]
    else:
        src_indices = []
    src_indices.append(src_word_ind)

    return src_indices


def get_translated_professions(alignment_fn: str, ds: List[List[str]], bitext: List[List[str]]) -> List[str]:
    """
    (Language independent)
    Load alignments from file and return the translated profession according to
    source indices.
    """
    # Load files and data structures
    ds_src_sents = list(map(itemgetter(2), ds))
    bitext_src_sents = list(map(itemgetter(0), bitext))

    # Sanity checks
    assert len(ds) == len(bitext)
    mismatched = [ind for (ind, (ds_src_sent, bitext_src_sent)) in enumerate(zip(ds_src_sents, bitext_src_sents))
                  if ds_src_sent != bitext_src_sent]
    if len(mismatched) != 0:
        pdb.set_trace()
        raise AssertionError

    bitext = [[sent.split() for sent in line]
              for line in bitext]

    src_indices = list(map(get_src_indices, ds))

    alignments = []
    for line in open(align_fn):
        cur_align = defaultdict(list)
        for word in line.split():
            src, tgt = word.split("-")
            cur_align[int(src)].append(int(tgt))
        alignments.append(cur_align)

    assert len(bitext) == len(alignments)
    assert len(src_indices) == len(alignments)

    translated_professions = []

    for (src_sent, tgt_sent), alignment, cur_indices in tqdm(zip(bitext, alignments, src_indices)):
        cur_translated_profession = " ".join([tgt_sent[cur_tgt_ind]
                                              for src_ind in cur_indices
                                              for cur_tgt_ind in alignment[src_ind]])
        translated_professions.append(cur_translated_profession)

    return translated_professions

if __name__ == "__main__":
    # Parse command line arguments
    args = docopt(__doc__)
    ds_fn = args["--ds"]
    bi_fn = args["--bi"]
    align_fn = args["--align"]
    lang = args["--lang"]
    debug = args["--debug"]
    if debug:
        logging.basicConfig(level = logging.DEBUG)
    else:
        logging.basicConfig(level = logging.INFO)

    gender_predictor = LANGAUGE_PREDICTOR[lang]

    ds = [line.strip().split("\t") for line in open(ds_fn, encoding = "utf8")]
    bitext = [line.strip().split(" ||| ")
              for line in open(bi_fn, encoding = "utf8")]

    translated_profs = get_translated_professions(align_fn, ds, bitext)
    gender_predictions = [(prof, gender_predictor.get_gender(prof)) for prof in tqdm(translated_profs)]
    uncertain = [elem for elem in gender_predictions
                 if elem[1] is unknown]



    logging.info(list(zip(translated_profs, gender_predictions))[:20])
    c = Counter(map(itemgetter(1), gender_predictions))
    logging.info(str(c))

    logging.info("DONE")