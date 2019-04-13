class Flag:
    def __init__(self, name, default=False):
        self.name = name
        self.default = default

    def get_state_for_request(self, request):
        return self.default
