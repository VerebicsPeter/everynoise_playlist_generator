import pathlib

data_dir = pathlib.Path(__file__).parent.resolve()

DATABASE_PATH = f"sqlite:///{data_dir}/music.db"
