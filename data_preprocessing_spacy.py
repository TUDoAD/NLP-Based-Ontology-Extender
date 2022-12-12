import spacy


def is_relevant(token):
    # function which test if a token is important by POS
    # NOUN - nouns; PROPN - proper noun; VERB - verbs; ADJ - adjective; NUM - number; PUNCT - punctuation
    pos_tags = ['NOUN', 'PROPN']
    if token.pos_ in pos_tags:
        return True
    else:
        return False


def is_datawaste(token):
    # function which tests if a token is important by comparison
    waste = ['fig', 'figure', 'table', 'tab', 'site', 'min', 'max', 'number', 'vol.%', 'xxx', 'mmo', 'ghsv', 'usy',
             'use', 'article', 'tpr', 'image', 'idh', 'con-', 'scr', 'igm', 'author', 'xps', 'lyst', 'cdpr', 'mpa',
             'ref', 'ppm', 'wt.%', 'cm-1', 'pro-', 'ml-1', 're-', 'rng', 'ptg', 'rsc', 'sbcr', 'sci', 'wiley', 'vch',
             'verlag', 'alyst', 'kgaa', 'h-1', 'w.j', 'xxxx', 'wt-%', 'vol-%', 'rmse', 'adv', 'd.s.a', 'http', 'doi',
             'gao', 'list', 'b.v', 'spr', 's-1', 'mol', 'mol1', 'l-1', 'flh', 'cpst', 'appl', 'ltd', 'tso', 'hydro-',
             'sbe900', 'csl', 'sbp4', 'icp', 'ely', 'tem-', 'dft', 'acs', 'fcc', 'mfr', 'sic', 'kpa', 'igg', 'whsv',
             'cm3', 'bjh', 'tof', 'std.l', 'i', 'ii', 'iii', 'iv', 'v', 'cox', 'pres-', 'sty', 'k.p', '.', 's1a†',
             'technol', 'tion', 'mgo', 'jie', 'liu', 'xrd', 'sng', 'tem', 'tpd', 'nio', 'co.', 'xco2', 'bid', 'ceo2',
             'ldh', 'cnt', 'nimn1al10', 'ce0.5zr0.5o2', 'mcr-2x', 'situ', 'ldhs', 'aubps', 'nial', 'ture', 'gms',
             'h−1', '/kg', 'cm−1', 'alox', 'author', 'sch4', 'ceria', 'ml−1', 'ucr', 'mgal', 'mg2−xal', '-al2o3',
             'mgal2o4', '4.8%ni', '5%pr-12%ni', 'sem', 'mnoy', 'nimn0.5al10', '12%ni', 'perature', 'methana-', 'cepte',
             'la2o3', 'nimnxal10', 'eq', 'nimn2al10', 'cata-', 'ing', 'lee', 'rwgs', 'lyst', 'tcd', 'ftir', 'simakov',
             'com-', 'rh(1%)/', 'gem', 'hrtem', 'cfd', 'mol1', 'aubp', 'l−1', 'g-1', 'sorption', 'usyie', 'ature',
             'kmol', 'ych4', 'conver-', 'kgcat.h', 'ni(co)4', 'emol', '/gj', 'ysz', 'pem', 'dn50', 'liu', 'm-³',
             'go¨rke', 'tive', 'reac-', 'nhs', 'nial2o4', 'aunr', 'ml$g‒1$h‒1', 'sol', 'alyst', 'ccus', 'ence', 'ni/',
             'δh298k', 'ce0.72zr0.28o2', 'ru.tio2', 'rha', 'mcm-41', 'gibb', 'nixmg2−xal', 'ni3fe', 'perfor-', 'gen',
             'tofni', 'edc', 'tivity', '5%sreni', '3m-350', '5%x-12%ni', 'eff', 'gms,0', 'cmol', 'pbs', 'car-', 'cnfs',
             'fax', '+86', 'tel', 'jcpds', 'mg1.6al', '5%baeni', 'c.v', 'mg1.6al', 'pdf', '5%sreni', '5%baeni',
             'perfor-', 'eff', 'cnfs', '2.5%mg', '5%x-12%ni', 'ni-', '5%mgeni', '5%caeni', 'ther-', 'lid', 'hcoo',
             'gcat', 'sreni', 'rhtotal', 'δh0', '3s-350', 'co2]in', 'de-', 'sect', 'r.a', 'nio−mgo', '10b', '15%ni',
             'dagle', 'rh/', '5%gd-12%ni', '5%ce-12%ni', '2p3/2', 'jeol', 'vol%', 'ity', 'calcu-', 'wgs', 'mg0.4al',
             'ni1.6', 'mg1.2al', 'cat-', 'mof', 'zsw', 'mea', 'bulk', '5%la-12%ni', 'ni(15%)/tio2', 'iwi''nix/', 'sor',
             'dis-', 'dh298', 'dh298k', 'ni(no3)2·6h2o', 'ru/', '0.86mn', 'cle', 'centration', 'cal', 'fin', 'fout',
             'oad', 'tsos', 'mol−1', 'eac', 'sro2', 'sbp900_av', '/(mw⁄a', 'wfo', 'sbet', 'vmicro', '3.7%ni', 'ni−mg',
             'mg−ni', 'atm', 'kg(cid:2']
    if token.text in waste:
        return True
    else:
        return False


def preprocessing(pdf_data):
    # function for preprocessing pdf_data with spacy module
    # import spacy library
    #lib = spacy.load('en_core_web_sm')
    lib = spacy.load('de_core_news_md')
    # fix max length
    lib.max_length = 150000000

    # convert text into lower case
    data = pdf_data.lower()

    # create a doc object
    doc = lib(data)

    # create a list of sentences
    sentences = []
    for sentence in doc.sents:
        temp = [sentence]
        sentences.append(temp)

    # deleting unimportant words by POS
    sentences_imp = []
    for sentence in sentences:
        for token in sentence:
            temp = []
            for i in range(len(token)):
                if is_relevant(token[i]):
                    temp.append(token[i])
            sentences_imp.append(temp)

    # deleting unimportant words by comparison
    sentences_imp_2 = []
    for sentence in sentences_imp:
        temp = []
        for token in sentence:
            if not is_datawaste(token):
                temp.append(token)
        sentences_imp_2.append(temp)

    # deleting single letters
    sentences_delsm = []
    for sentence in sentences_imp_2:
        temp = []
        for token in range(len(sentence)):
            if len(sentence[token]) > 2:
                temp.append(sentence[token])
        sentences_delsm.append(temp)

    # lemmatization
    sentences_lem = []
    for sentence in sentences_delsm:
        temp = []
        for i in sentence:
            temp.append(i.lemma_)
        sentences_lem.append(temp)

    # returning preprocessed data
    return sentences_lem
