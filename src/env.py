from dotenv import load_dotenv
from .util import required_env_var

load_dotenv()

bot_token = required_env_var("FLAG_BOT_TOKEN")
sandbox_user = required_env_var("FLAG_BOT_SANDBOX_USER")
