from buttons import Buttons
from display import Display
from speaker import Speaker


class App:
    def __init__(self, name):
        self.name = name
        self.active = False
        self.grab_top_button = False

    def top_button(self):
        print("top_button not implemented for " + self.name)


class Apps:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.display = Display(scheduler)
        self.buttons = Buttons(scheduler)
        self.speaker = Speaker(scheduler)
        self.apps = []
        self.current_app = 0
        self.buttons.add_callback(1, self.next, max=500)
        self.buttons.add_callback(1, self.previous, min=500)
        self.buttons.add_callback(1, self.exit, min=500)

    async def start(self):
        await self.apps[0].enable()

    def add(self, app):
        # if len(self.apps) == 0:
        #     await app.enable()
        self.apps.append(app)

    async def next(self):
        print("NEXT")
        if len(self.apps) == 0:
            return

        app = self.apps[self.current_app]
        if app.active and app.grab_top_button:
            app.top_button()
            return

        self.apps[self.current_app].disable()
        self.buttons.clear_callbacks(2)
        self.buttons.clear_callbacks(3)
        self.display.clear_text()
        self.current_app = (self.current_app + 1) % len(self.apps)
        print("SWITCHING TO", self.apps[self.current_app].name)
        self.speaker.beep(200)
        await self.apps[self.current_app].enable()

    async def previous(self):
        print("PREVIOUS")
        if len(self.apps) > 0:
            self.apps[self.current_app].disable()
            self.current_app = (self.current_app - 1) % len(self.apps)
            self.apps[self.current_app].enable()

    async def exit(self):
        if len(self.apps) > 0:
            self.apps[self.current_app].disable()
            self.current_app = 0
            self.apps[self.current_app].enable()
