import csv
import os


class Date:
    intraday = 0
    day = 0
    month = 0
    year = 0

    @staticmethod
    def from_string(s: str):
        self = Date()
        l = s.split("-")
        self.year = int(l[0])
        self.month = int(l[1])
        self.day = int(l[2])
        if len(l) >= 4:
            self.intraday = int(l[3])
        return self

    def __str__(self):
        return "{:04d}-{:02d}-{:02d}-{:02d}".format(self.year, self.month, self.day, self.intraday)

    def to_date_string(self):
        return "{:04d}-{:02d}-{:02d}".format(self.year, self.month, self.day)

    def month_string(self):
        return "{:04d}-{:02d}".format(self.year, self.month)

    def intraday_copy(self):
        d = Date()
        self.intraday = self.intraday + 1
        d.intraday = self.intraday
        d.year = self.year
        d.month = self.month
        d.day = self.day
        return d

    def __lt__(self, other):
        assert(isinstance(other, Date))
        return str(self) < str(other)


class Operation:
    date = Date()
    delta_quantity = 0
    unit_cost = 0.0
    document = ""

    def __init__(self, date: Date, delta_quantity: int, unit_cost: float, document: str):
        assert(isinstance(date, Date))
        assert(isinstance(delta_quantity, (int, float)))
        assert(isinstance(unit_cost, float))
        assert(isinstance(document, str))
        self.date = date
        self.delta_quantity = delta_quantity
        self.unit_cost = unit_cost
        self.document = document

    def __str__(self):
        return "date={} qty={} unit={} doc={}".format(self.date, self.delta_quantity, self.unit_cost, self.document)

    def expand(self, doc=False):
        return self.date, self.delta_quantity, self.unit_cost, self.document


def expanded(items):
    for item in items:
        yield item.expand()


class Database(dict):

    def add(self, ticket: str, operation: Operation):
        assert (type(operation) == Operation)
        if ticket not in self:
            self[ticket] = []
        self[ticket].append(operation)

    def add_multiple(self, ticket: str, list_of_operations):
        for op in list_of_operations:
            self.add(ticket, op)

    def sort(self):
        for _, v in self.items():
            v.sort(key=lambda x: x.date)

    @staticmethod
    def from_file(file_path: str):
        self = Database()
        if os.path.exists(file_path):
            with open(file_path, newline='') as csv_file:
                reader = csv.reader(csv_file, skipinitialspace=True, quoting=csv.QUOTE_NONNUMERIC)
                for row in reader:
                    if len(row) == 0:
                        continue
                    if len(row) != 5:
                        raise ValueError("Bad database file:", file_path)
                    self.add(row[0].lstrip(" ").rstrip(" "), Operation(Date.from_string(row[1]),
                                               int(row[2]),
                                               float(row[3]),
                                               str(row)))
        return self

    def save_to_file(self, file_path: str):
        with open(file_path, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, skipinitialspace=True, quoting=csv.QUOTE_NONNUMERIC)
            for k in sorted(self):
                writer.writerows([(k,) + v.expand() for v in self[k]])

    def serialize(self, output):
        writer = csv.writer(output, skipinitialspace=True, quoting=csv.QUOTE_NONNUMERIC)
        for k in sorted(self):
            writer.writerows([(k,) + v.expand() for v in self[k]])


class Books(dict):
    book_header = ['Ticket', 'Date', 'Op', 'Qty', '$ Unit', '$ Operation', 'Position',
                   '$ Paid Per Unit', '$ Position', '$ Profit']
    col_map = {
        'ticket': 0,
        'date': 1,
        'purchased_units': 6,
        'paid_per_unit': 7,
        'profit': 9
    }

    def select(self, columns):
        for column in columns:
            assert(column in self.col_map)
        for ticket, v in self.items():
            for book_line in v:
                result = ()
                for column in columns:
                    if column == 'ticket':
                        result = result + (ticket,)
                    else:
                        result = result + (book_line[self.col_map[column]],)
                yield result

    def select_filtered_by_ticket(self, ticket: str, columns):
        for column in columns:
            assert(column in self.col_map)
        for v in self[ticket]:
            for book_line in v:
                result = ()
                for column in columns:
                    if column == 'ticket':
                        result = result + (ticket,)
                    else:
                        result = result + (book_line[self.col_map[column]],)
                yield result

    @staticmethod
    def from_database(database: Database):
        self = Books()
        database.sort()

        for ticket in database:
            operations = database[ticket]
            paid_per_unit = 0
            purchased_units = 0
            book = []

            for date, delta, unit_cost, _ in expanded(operations):
                profit = 0.0
                cost = unit_cost * delta * -1.0

                if delta > 0 and purchased_units >= 0:
                    quadrant = "buy"
                elif delta < 0 and purchased_units >= abs(delta):
                    quadrant = "sell"
                elif delta < 0 and purchased_units <= 0:
                    quadrant = "borrow"
                elif delta > 0 and purchased_units <= abs(delta):
                    quadrant = "return"
                else:
                    quadrant = None

                if not quadrant:
                    book = []
                    break

                elif quadrant == "buy" or quadrant == "borrow":
                    total_position_cost = (purchased_units * paid_per_unit) - cost
                    paid_per_unit = total_position_cost / (purchased_units + delta)

                elif quadrant == "sell" or quadrant == "return":
                    profit = (unit_cost - paid_per_unit) * delta * -1.0

                purchased_units = purchased_units + delta

                book.append((ticket,
                             date,
                             "buy" if delta > 0 else "sell",
                             delta,
                             unit_cost,
                             cost,
                             purchased_units,
                             paid_per_unit,
                             purchased_units * paid_per_unit,
                             profit))

            self[ticket] = book

        return self


class MonthlyResults(dict):

    @staticmethod
    def from_books(books: Books):
        self = MonthlyResults()
        for date, ticket, profit in sorted(books.select(['date', 'ticket', 'profit']), key=lambda x: x[0]):
            if profit == 0:
                continue
            month_string = date.month_string()
            if month_string not in self:
                self[month_string] = []
            self[month_string].append((date, ticket, profit))

        return self


class FinalPosition(Database):
    @staticmethod
    def from_books(books: Books):
        self = FinalPosition()
        position = {}

        for date, ticket, purchased_units, paid_per_unit\
                in sorted(books.select(['date', 'ticket', 'purchased_units', 'paid_per_unit']),
                          key=lambda x: x[0]):
            position[ticket] = (date, purchased_units, paid_per_unit)

        for k, v in position.items():
            if v[1]:
                self.add(k, Operation(v[0], v[1], v[2], "final position"))

        return self
