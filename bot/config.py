from dotenv import dotenv_values


def get_token_from_dotenv():
    data = dotenv_values("../.env")
    return data['TELEGRAM_BOT_TOKEN']
