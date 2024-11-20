import pathlib

data_dir = pathlib.Path(__file__).parent.resolve()

DATABASE_PATH = f"sqlite+aiosqlite:///{data_dir}/music.db"
