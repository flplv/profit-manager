import profit_manager.operation_model as op
from tika import parser
import glob
import re


class Date(op.Date):
    @staticmethod
    def from_string(s):  # Input format: dd/mm/yyyy
        self = Date()
        d, m, y = s.split("/")
        self.year = int(y)
        self.month = int(m)
        self.day = int(d)
        return self


def sn(s):
    s = s.replace('.', '')
    s = s.replace(',', '.')
    return s


def process_multiline_text(database: op.Database, date, text):
    assert(isinstance(database, op.Database))

    # Match operations
    regex = r"1-BOVESPA (C|V) (.*) {10}.* (.*) (.*) (.*) [C|D]"
    matches = re.finditer(regex, text, re.MULTILINE)

    # Save into the database
    for operation_number, match in enumerate(matches, start=1):

        is_sell = True if match.group(1) == "V" else False
        ticket = match.group(2)
        quantity = int(sn(match.group(3)))
        cost = float(sn(match.group(4)))
        total = float(sn(match.group(5)))

        if abs(total - (cost * quantity)) > 0.01:
            print("  Weirdly, total cost does not match unit cost times quantity...")
            print(" ", match.group())
            print(" Computed total was", cost * quantity)

        operation = op.Operation(date,
                                 -quantity if is_sell else quantity,
                                 cost,
                                 match.group())

        database.add(ticket, operation)


def pdf_parse_one(database: op.Database, pdf_path):
    assert(isinstance(database, op.Database))

    print("Parsing", pdf_path)

    pages = parser.from_file(pdf_path)['content'].split("Negócios realizados")

    for page in pages:
        regex_date = r"Data pregão\n\n(.*)"
        result = re.findall(regex_date, page, re.MULTILINE)
        if len(result) == 0:
            continue
        date = Date.from_string(result[0])
        filtered_pdf = "\n".join([line for line in page.splitlines() if "1-BOVESPA" in line])
        process_multiline_text(database, date, filtered_pdf)


def pdf_parse_from_folder(database: op.Database, pdf_folder_path):
    for file in glob.glob("{}/*.pdf".format(pdf_folder_path)):
        pdf_parse_one(database, file)
