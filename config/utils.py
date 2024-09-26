from config.config import PREMIUM_GUILD_IDS, TEST_GUILD_IDS

# Prüft, ob eine Guild Zugriff auf Premium-Features hat
def has_premium_access(guild_id):
    return guild_id in PREMIUM_GUILD_IDS or guild_id in TEST_GUILD_IDS
