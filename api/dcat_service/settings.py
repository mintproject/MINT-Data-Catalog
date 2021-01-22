import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)


class DBSettings:

    def __init__(self, host: str, port: str, user: str, password: str, db_name: str):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user = user
        self.password = password

    @staticmethod
    def from_env() -> 'DBSettings':
        return DBSettings(
            os.environ["DB_HOST"],
            os.environ["DB_PORT"],
            os.environ["DB_USERNAME"],
            os.environ["DB_PASSWORD"],
            os.environ["DB_NAME"]
        )


class Settings:
    instance = None

    def __init__(self, database: DBSettings):
        self.database = database

    @staticmethod
    def get_instance() -> 'Settings':
        if Settings.instance is None:
            Settings.instance = Settings(DBSettings.from_env())

        return Settings.instance


if __name__ == '__main__':
    """Create an environment file based on example file and override some variables"""
    import sys
    from pathlib import Path

    env_dir = Path(sys.argv[1])
    assert env_dir.exists()

    vars = {}
    for env_value in sys.argv[2:]:
        key = env_value.split("=")[0]
        vars[key] = env_value

    new_env_file = []
    assert not (env_dir / ".env").exists(), "cannot override existing .env file"

    with open(env_dir / ".env.example", "r") as f:
        for line in f:
            if line.lstrip().startswith("#") or line.strip() == "":
                new_env_file.append(line)
                continue

            var_name = line[:line.find("=")]
            if var_name in vars:
                new_env_file.append(vars[var_name] + "\n")
            else:
                new_env_file.append(line)

    with open(env_dir / ".env", "w") as f:
        for line in new_env_file:
            f.write(line)
