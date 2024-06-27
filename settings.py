def load_dotenv_values(dotenv_path: str) -> dict:
    with open(dotenv_path) as f:
        dotenv_as_dict = {}
        for dotenv_line in f.read().splitlines():
            dotenv_line_as_list = dotenv_line.split("=", 1)
            if len(dotenv_line_as_list) == 2:
                dotenv_as_dict[dotenv_line_as_list[0].strip()] = dotenv_line_as_list[
                    1
                ].strip()
        return dotenv_as_dict


# settings = load_dotenv_values(".env")

# TV_DB_API = settings["TV_DB_API"]
# TOKEN = settings["TOKEN"]
# JWT_EXPIRATION_DATETIME = settings["JWT_EXPIRATION_DATETIME"]

TV_DB_API = "https://api4.thetvdb.com/v4"
TOKEN = ""
JWT_EXPIRATION_DATETIME = 1694924373