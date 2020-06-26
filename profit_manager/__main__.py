import profit_manager.operation_model as op
import profit_manager.parser as parser
import profit_manager.console as console


if __name__ == "__main__":
    database = op.Database.from_file("./initial_position.csv")
    parser.pdf_parse_from_folder(database, "./")
    books = op.Books.from_database(database)
    profits = op.MonthlyResults.from_books(books)
    sales = op.MonthlySales.from_books(books)
    final_position = op.FinalPosition.from_books(books)

    console.print_books(books)
    console.print_monthly_profits(profits)
    console.print_monthly_sales(sales)
    console.print_database_pretty(final_position, "Final position")

    database.save_to_file("./database.csv")
    final_position.save_to_file("./final_position.csv")
