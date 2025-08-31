import typer

from merlindb.utils import get_mdb, read_areas, read_table, read_tables

app = typer.Typer()


@app.command()
def dump(file_path: str):
    db = get_mdb(file_path)
    if db:
        db.print_database()


@app.command()
def table(file_path: str, table_name: str):
    db = get_mdb(file_path)
    if db:
        read_table(db, table_name)


@app.command()
def areas(file_path: str):
    db = get_mdb(file_path)
    if db:
        read_areas(db)


@app.command()
def tables(file_path: str):
    db = get_mdb(file_path)
    if db:
        read_tables(db)
    # print(f"Hello {name}")
