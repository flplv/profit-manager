import glob
import multiprocessing
import pdfminer.high_level as pdf
import pdfminer.layout as pdflayout
import profit_manager.operation_model as op
import profit_manager.xp_group as xp
import profit_manager.itau as itau

parsers = {"ItaúCorretora de Valores S/A": itau.parse_from_text,
           "CLEAR CORRETORA - GRUPO XP": xp.parse_from_text_clear,
           "XP INVESTIMENTOS CCTVM S/A": xp.parse_from_text_xp}


def extract(pdf_path):
    text = pdf.extract_text(pdf_path, laparams=pdflayout.LAParams(char_margin=1000.0))
    selected_needles = list(filter(lambda needle: needle in text, parsers.keys()))
    if len(selected_needles) == 0:
        print("Pdf", pdf_path, "ignored, not parser for it.")
        return text, None
    parser = parsers[selected_needles[0]]
    print("Loaded", pdf_path, "as", parser.__module__.split(".")[-1])
    return parser, pdf_path, text


def pdf_parse_from_folder(database: op.Database, pdf_folder_path):
    files = [file for file in glob.glob("{}/*.pdf".format(pdf_folder_path))]
    nb_cores = multiprocessing.cpu_count()
    with multiprocessing.Pool(processes=nb_cores) as pool:
        documents = pool.starmap(extract, zip(files))
    results = [d[0](d[1], d[2], database) for d in documents]
