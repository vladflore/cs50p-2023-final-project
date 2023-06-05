from dotenv import dotenv_values

settings = dotenv_values(".env")

TV_DB_API = settings["TV_DB_API"]
TOKEN = settings["TOKEN"]
JWT_EXPIRATION_DATETIME = settings["JWT_EXPIRATION_DATETIME"]
