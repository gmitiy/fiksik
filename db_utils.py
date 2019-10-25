from pymongo import MongoClient
from pymongo.collection import Collection
from simplecrypt import encrypt, decrypt

crypto_password = 'KNzf5XsV0DTtHKruIkWD76IvCqXnEIdp5iMS6Lh4'


class Database(object):
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client['fixik-db']

    def upsert_cred(self, user_id, system, login, passwd, alias=None, ip=None):
        creds: Collection = self.db.creds
        res = creds.update_one({'uid': user_id, 'system': system.upper(), 'alias': alias},
                               {'$set': {
                                   'login': login,
                                   'passwd': encrypt(crypto_password, passwd),
                                   'alias': alias,
                                   'ip': ip
                               }}, upsert=True)
        return res.upserted_id is None

    def get_cred(self, user_id, system):
        creds: Collection = self.db.creds
        res = creds.find_one({'uid': user_id, 'system': system})
        if res:
            return {'login': res['login'], 'passwd': decrypt(crypto_password, res['passwd']).decode('ascii')}
        return None

    def get_cred_by_alias(self, user_id, alias):
        creds: Collection = self.db.creds
        res = creds.find_one({'uid': user_id, 'alias': alias})
        if res:
            return {'login': res['login'], 'passwd': decrypt(crypto_password, res['passwd']).decode('ascii'),
                    'ip': res['ip']}
        return None

    def get_all_cred(self, user_id):
        creds: Collection = self.db.creds
        res = []
        for i in creds.find({"uid": user_id}):
            res.append(i)
        return {'cred': res}


db = Database()
