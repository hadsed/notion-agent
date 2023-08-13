class Tool:
    def __init__(self):
        pass

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def methods(self):
        raise NotImplementedError

    @property
    def description(self):
        raise NotImplementedError

    def execute(self, *args, **kwargs):
        raise NotImplementedError
