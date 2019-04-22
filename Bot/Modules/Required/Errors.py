class InsufficientParameterException(Exception):
    """Insufficient Parameters given for Command"""
    def init(self, command):
        self.command = command

    def __str__(self):
        return "Command %s called with insufficient Parameters" % command

class UnexpectedBotClosure(Exception):
    """One Bot Instance Unexpectedly close"""
    def init(self, name):
        self.name = name

    def __str__(self):
        return "Bot for Channel %s unexpectedly closed" % self.name
