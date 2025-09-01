from access_parser import AccessParser
from pydantic import BaseModel

from merlindb.logging import log, print_table
from merlindb.models.genisys import model_map as genisys_model_map
from merlindb.models.merlin import MerlinDbModel


def get_mdb(file_path: str) -> AccessParser | None:
    try:
        _db = AccessParser(file_path)
    except Exception as e:
        print(f"Error loading MDB file: {e}")
        return None
    else:
        return _db


def read_row(table_name: str, row: dict, models: dict) -> BaseModel | None:
    if table_name in models.keys():
        return models[table_name](**row)
    else:
        return None


def read_genisys_table(db: AccessParser, table_name: str) -> list[BaseModel] | None:
    table = db.parse_table(table_name)
    col_names = table.keys()
    _rows = []
    return [
        read_row(table_name, item, genisys_model_map)
        for item in table_to_dicts(col_names, table.values())
    ]


#
# def read_dynalite_config(genisys_tables: list[BaseModel]):
#     _config = MerlinDbModel()
#     for genisys_table in genisys_tables:
#         _


def load_all(db: AccessParser) -> dict | None:
    _tables = dict.fromkeys(db.catalog.keys())
    for table_name, v in _tables.items():
        _tables[table_name] = read_genisys_table(db, table_name)
    # _merlin_tables = MerlinDbModel(**{i: v for i, v in _tables.items()})
    _genisys_dict = {
        i: list([x.model_dump() for x in v if x is not None]) for i, v in _tables.items()
    }
    _merlin_tables = MerlinDbModel(**_genisys_dict)
    log.info("Loaded all tables")
    return _merlin_tables.model_dump()


def table_to_dicts(table_cols: list[str], table_rows: list[list]) -> list[dict]:
    """
    Convert table structure to list of dictionaries.

    Args:
        table_cols: List of column names (keys for dictionaries)
        table_rows: List of lists where each inner list contains all values for one column

    Returns:
        List of dictionaries, one per row
    """
    if not table_cols or not table_rows:
        return []

    # Transpose the table_rows to get rows instead of columns
    rows = list(zip(*table_rows, strict=False))

    # Create dictionary for each row
    return [dict(zip(table_cols, row, strict=False)) for row in rows]


def read_tables(db: AccessParser) -> None:
    for k in db.catalog.keys():
        print(f"{k}\n")


# def read_table(db: AccessParser, table_name: str) -> None:
#     table = db.parse_table(table_name)
#     return
#     print_table(
#         table_name,
#         list(table.keys()),
#         [list(map(str, v)) for v in zip(*table.values(), strict=False)],
#     )


def parse_object_type(obj_type: str) -> str:
    match obj_type:
        case "Fan":
            return "ceiling_fan"
        case "ExhaustFan":
            return "exhaust_fan"
        case "Curtain":
            return "curtain"
        case "GeneralSwitch":
            return "heater"
        case _:
            return "unknown"


def get_area_type(obj_types: dict, obj_id: int | None = None):
    if obj_id:
        return obj_types.get(obj_id)
    return "lights"


def get_channel_type(obj_types: dict, obj_id: int | None = None, channel_number: int | None = None):
    if obj_id:
        match obj_types.get(obj_id):
            case "curtain":
                if channel_number == 1:
                    return "curtain_power"
                elif channel_number == 2:
                    return "curtain_direction"
                else:
                    return "curtain_unknown"
            case "heater":
                return "heater_power"
            case "exhaust_fan":
                return "exhaust_fan_power"
            case "ceiling_fan":
                if channel_number == 1:
                    return "ceiling_fan_power"
                elif channel_number == 2:
                    return "ceiling_fan_controller"
                else:
                    return "ceiling_fan_unknown"
            case _:
                return "unknown"
    else:
        return "light"


def read_areas(db: AccessParser) -> None:
    areas = db.parse_table("AreaNames")
    print_table(
        "AreaNames",
        list(areas.keys()),
        [list(map(str, v)) for v in zip(*areas.values(), strict=False)],
    )
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
