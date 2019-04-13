class Flag:
    def __init__(self, name):
        self.name = name

    def get_state_for_request(self, request):
        return False
