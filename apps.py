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
        self.buttons.add_callback(1, self.app_chooser, min=500)
        self.buttons.add_callback(1, self.app_top_button, max=500)

    async def start(self):
        await self.apps[0].enable()

    def add(self, app):
        self.apps.append(app)

    async def app_chooser(self):
        print("APP CHOOSER")
        if len(self.apps) == 0:
            return

        await self.disable_current_app()

        self.buttons.add_callback(2, self.next_app, max=500)
        self.buttons.add_callback(3, self.previous_app, max=500)

        await self.show_current_app_name()

    async def enable_current_app(self):
        self.buttons.clear_callbacks(2)
        self.buttons.clear_callbacks(3)
        self.display.clear_text()
        print("SWITCHING TO", self.apps[self.current_app].name)
        # self.speaker.beep(200)
        await self.apps[self.current_app].enable()

    async def disable_current_app(self):
        app = self.apps[self.current_app]
        app.disable()
        app.active = False
        app.grab_top_button = False
        self.buttons.clear_callbacks(2)
        self.buttons.clear_callbacks(3)

    async def show_current_app_name(self):
        self.display.display_queue.clear()
        await self.display.animate_text(self.apps[self.current_app].name.upper(), force=True)
        await self.display.show_text(self.apps[self.current_app].name.upper())

    async def next_app(self):
        self.current_app = (self.current_app + 1) % len(self.apps)
        await self.show_current_app_name()

    async def previous_app(self):
        self.current_app = (self.current_app - 1) % len(self.apps)
        await self.show_current_app_name()

    async def app_top_button(self):
        app = self.apps[self.current_app]
        if app.active and app.grab_top_button:
            should_go_next: bool = await app.top_button()
            if should_go_next:
                await self.app_chooser()
            else:
                return
        else:
            await self.enable_current_app()
