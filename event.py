class Event:
    def __init__(self, date, hour, location, name):
            self.date = date
            self.hour = hour
            self.location = location
            self.name = name

    def __str__(self):
        showHour = False
        if showHour:
            string = self.date + " " + self.hour +\
                    " " + self.location + " " + self.name
        else:
            string = self.date + " " +\
                    " " + self.location + " " + self.name
        return string
