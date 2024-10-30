class Track:
    def __init__(self, name, artist):
        self.name = name
        self.tags = set()
        self.artist = artist

    def add_tag(self, tag):
        self.tags.add(tag.lower())

    def __str__(self):
        return f"{self.artist} - {self.name}: {', '.join(self.tags)}"

class Artist:
    def __init__(self, name):
        self.name = name
        self.tags = set()

    def add_tag(self, tag):
        self.tags.add(tag.lower())

    def __str__(self):
        return f"{self.name}: {', '.join(self.tags)}"
