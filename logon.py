class Logon:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __str__(self):
        return 'login [{}] password [{}]'.format(self.login, self.password)
