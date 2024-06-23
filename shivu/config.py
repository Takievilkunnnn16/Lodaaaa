class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "1643054031"
    sudo_users = "5982968099, 2081927790, 5670095072, 5415089541, 6623052196 6584789596, 6384296585, 1643054031, 5603495353 6988555661"
    GROUP_ID = -1002141403968
    TOKEN = "6763528462:AAFeagpgZIdq3XD67cP_EpBY4DKxn6M4i-o"
    mongo_url = "mongodb+srv://Takievil:takievil098@takievil.uallkel.mongodb.net/?retryWrites=true&w=majority"
    PHOTO_URL = ["https://telegra.ph/file/38e44bfbb08ee120d4664.jpg", "https://telegra.ph/file/54141a6ebef7d07ffe541.jpg", "https://telegra.ph/file/6015785c1f7f721ebdd80.jpg"]
    SUPPORT_CHAT = "Catch_Your_WH_Group"
    UPDATE_CHAT = "Collect_em_support"
    BOT_USERNAME = "Collect_Em_AllBot"
    CHARA_CHANNEL_ID = "-1002069808795"
    api_id = 29593257
    api_hash = "e9a3897c961f8dce2a0a88ab8d3dd843"

    
class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
