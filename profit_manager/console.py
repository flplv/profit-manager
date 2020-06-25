import profit_manager.operation_model as op
from tabulate import tabulate
import io


def print_books(books: op.Books):
    for ticket, book in sorted(books.items()):
        print("Book for ticket", ticket)
        print()
        print(tabulate(books[ticket], books.book_header))
        if len(book) == 0:
            print("Table is empty because an non supported operation was detected,"
                  " check the database.csv for quadrant changes.")
        else:
            print("              Total profit:", sum([t[-1] for t in books[ticket]]))
        print()
    print()


def print_monthly_profits(profits: op.Books):
    year_profit = 0

    for k in sorted(profits):
        v = profits[k]
        v.sort(key=lambda x: x[0])
        total_profit = sum([t[2] for t in v])
        year_profit += total_profit
        print("Monthly profits for", k)
        print(tabulate(v, headers=['Date', 'Ticket', 'Profit']))
        print("          Month total profit:", total_profit)
        print()

    print("Total profit:", year_profit)
    print()
    print()


def print_database(database: op.Database, title: str):
    print("Database export for", title)
    output = io.StringIO()
    database.serialize(output)
    print(output.getvalue())
    print()
    print()


def print_database_pretty(database: op.Database,  title: str):
    print("Database export for", title)
    table = []
    for ticket, operations in sorted(database.items()):
        entry = [(ticket, date, qty, cost, qty * cost) for date, qty, cost, document in op.expanded(operations)]
        table = table + entry

    print(tabulate(table, headers=['Ticket', 'Date', 'Quantity', 'Unit Cost', 'Total']))
    print("                                      Total:", sum([t[-1] for t in table]))
