from discord.ext import commands

class AztraError(Exception):
    pass

class NotRegistered(commands.CheckFailure):
    pass

class NotMaster(commands.CheckFailure):
    pass

class GlobaldataAlreadyAdded(AztraError):
    pass

class SentByBotUser(commands.CheckFailure):
    pass

class LockedExtensionUnloading(AztraError):
    pass

class ArpaIsGenius(AztraError):
    pass

class ParamsNotExist(AztraError):
    def __init__(self, param):
        self.param = param
        super().__init__('존재하지 않는 옵션값입니다: {}'.format(param))

class NotGuildChannel(commands.CheckFailure):
    pass

class CmdNameNotFoundInDB(AztraError):
    def __init__(self, extname, cmdid):
        self.id = cmdid
        self.extname = extname
        super().__init__('"{}"확장의 명령어 아이디 "{}"의 이름 또는 별명값이 DB에 존재하지 않습니다'.format(extname, cmdid))

class MissingRequiredArgument(AztraError):
    def __init__(self, param, paramdesc):
        self.param = param
        self.paramdesc = paramdesc
        super().__init__('명령어 파라미터 "{}"({})이 필요합니다'.format(param.name, paramdesc))

class MissingAztraPermissions(commands.CheckFailure):
    def __init__(self, missing_perms):
        self.missing_perms = missing_perms
        super().__init__('Aztra 권한 {} 이 부족합니다.'.format(', '.join(missing_perms)))

class onInspection(commands.CheckFailure):
    pass

class SubcommandNotFound(commands.CheckFailure):
    pass