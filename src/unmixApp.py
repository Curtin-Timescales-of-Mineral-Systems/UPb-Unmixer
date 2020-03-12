from apps.abstract.application import AbstractApplication
from apps.unmix.controller import UnmixTabController


class UPbUnmixerApplication(AbstractApplication):

    def getControllers(self):
        return [self.createController()]

    @staticmethod
    def getTitle():
        return "U-Pb Unmixer"

    @staticmethod
    def getVersion():
        return "0.5"

    @staticmethod
    def createController():
        return UnmixTabController()


if __name__ == '__main__':
    app = UPbUnmixerApplication()
    app.createGUI()
