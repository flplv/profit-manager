import profit_manager.operation_model as op
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


def process_multiline_text(prefix: str, database: op.Database, date, text):
    # Match operations
    regex = r"1-BOVESPA (C|V) (.*) {10}.* (.*) (.*) (.*) [C|D]"
    matches = re.finditer(regex, text, re.MULTILINE)

    # Save into the database
    for operation_number, match in enumerate(matches, start=1):

        is_sell = True if match.group(1) == "V" else False
        ticket = " ".join([prefix, match.group(2).replace("FRACIONARIO", "VISTA")])
        quantity = int(sn(match.group(3)))
        cost = float(sn(match.group(4)))
        total = float(sn(match.group(5)))

        if abs(total - (cost * quantity)) > 0.01:
            print("  Weirdly, total cost does not match unit cost times quantity...")
            print(" ", match.group())
            print(" Computed total was", cost * quantity)

        operation = op.Operation(date.intraday_copy(),
                                 -quantity if is_sell else quantity,
                                 cost,
                                 match.group())

        database.add(ticket, operation)


def parse_from_text(prefix, pdf_path, text, database):
    date = Date()
    for page in text.split("NOTA DE NEGOCIAÇÃO"):
        regex_date = r"Data pregão\n\n(.*)"
        result = re.findall(regex_date, page, re.MULTILINE)
        if len(result) == 0:
            continue
        candidate_date = Date.from_string(result[0])
        if date.to_date_string() != candidate_date.to_date_string():
            date = candidate_date  # reset the intraday counter only if the date changes
        filtered_pdf = "\n".join([line for line in page.splitlines() if "1-BOVESPA" in line])
        process_multiline_text(prefix, database, date, filtered_pdf)


def parse_from_text_clear(pdf_path, text, database: op.Database):
    assert(isinstance(database, op.Database))
    return parse_from_text("CLEAR", pdf_path, text, database)


def parse_from_text_xp(pdf_path, text, database: op.Database):
    assert(isinstance(database, op.Database))
    return parse_from_text("XP", pdf_path, text, database)