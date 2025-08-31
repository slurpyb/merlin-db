from access_parser import AccessParser

from merlindb.logging import print_table


def get_mdb(file_path: str) -> AccessParser | None:
    try:
        _db = AccessParser(file_path)
    except Exception as e:
        print(f"Error loading MDB file: {e}")
        return None
    else:
        return _db


def read_tables(db: AccessParser) -> None:
    for k in db.catalog.keys():
        print(f"{k}\n")


def read_table(db: AccessParser, table_name: str) -> None:
    table = db.parse_table(table_name)
    print_table(
        table_name,
        list(table.keys()),
        [list(map(str, v)) for v in zip(*table.values(), strict=False)],
    )


def read_areas(db: AccessParser) -> None:
    areas = db.parse_table("AreaNames")
    print_table(list(areas.keys()), [list(map(str, v)) for v in zip(*areas.values(), strict=False)])
    # areas_extra = db.parse_msys_table().get("AreaNames")
    # _areas = {}

    # def handle(item: list):
    #     return [str(i).strip() if i is not None else "" for i in item]

    # for k in areas.keys():
    #     table.add_column(k, justify="right", style="cyan", no_wrap=True)
    # for count, pk in enumerate(areas.get("Area_ID")):
    #     print(handle([areas.get(col)[count] for col in areas.keys()]))
    #     table.add_row(*handle([areas.get(col)[count] for col in areas.keys()]))

    # console = Console()
    # console.print(table)
    # for k,v in areas.columns.values():
    #     print(f"{k}: {v} aa")


# # Tables are stored as defaultdict(list) -- table[column][row_index]
# table = db.parse_table("table_name")

# # Pretty print all tables
# db.print_database()
