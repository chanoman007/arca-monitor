from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
import threading
import urllib.request
import time

Window.clearcolor = (0.06, 0.06, 0.06, 1)

SERVICES = [
    {"name": "WSAA", "env": "Homologación", "url": "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl"},
    {"name": "WSAA", "env": "Producción",   "url": "https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl"},
    {"name": "WSFE", "env": "Homologación", "url": "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?wsdl"},
    {"name": "WSFE", "env": "Producción",   "url": "https://servicios1.afip.gov.ar/wsfev1/service.asmx?wsdl"},
]

def check_service(service):
    start = time.time()
    try:
        req = urllib.request.urlopen(service["url"], timeout=5)
        ms = int((time.time() - start) * 1000)
        return {**service, "status": "ONLINE", "ms": ms}
    except Exception as e:
        ms = int((time.time() - start) * 1000)
        return {**service, "status": "OFFLINE", "ms": ms}


class ServiceCard(BoxLayout):
    def __init__(self, service, **kwargs):
        super().__init__(orientation="vertical", padding=14, spacing=6,
                         size_hint_y=None, height=110, **kwargs)
        self.service = service

        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            self.bg_color = Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8])
        self.bind(pos=self._update_rect, size=self._update_rect)

        self.name_label = Label(
            text=f"{service['name']}  {service['env']}",
            font_size="15sp", bold=True, color=(0.9, 0.9, 0.9, 1),
            halign="left", valign="middle", size_hint_y=None, height=30
        )
        self.name_label.bind(size=self.name_label.setter("text_size"))

        self.status_label = Label(
            text="Verificando...",
            font_size="18sp", bold=True, color=(0.6, 0.6, 0.6, 1),
            halign="left", valign="middle", size_hint_y=None, height=36
        )
        self.status_label.bind(size=self.status_label.setter("text_size"))

        self.ms_label = Label(
            text="", font_size="11sp", color=(0.35, 0.35, 0.35, 1),
            halign="left", valign="middle", size_hint_y=None, height=20
        )
        self.ms_label.bind(size=self.ms_label.setter("text_size"))

        self.add_widget(self.name_label)
        self.add_widget(self.status_label)
        self.add_widget(self.ms_label)

    def _update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update(self, result):
        if result["status"] == "ONLINE":
            self.status_label.text = "● ONLINE"
            self.status_label.color = (0, 0.9, 0.46, 1)
        else:
            self.status_label.text = "● OFFLINE"
            self.status_label.color = (1, 0.27, 0.27, 1)
        self.ms_label.text = f"{result['ms']} ms"


class ARCAMonitor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=20, spacing=14, **kwargs)

        title = Label(text="ARCA · Monitor", font_size="22sp", bold=True,
                      color=(1, 1, 1, 1), size_hint_y=None, height=40,
                      halign="left")
        title.bind(size=title.setter("text_size"))

        self.ts_label = Label(text="", font_size="11sp", color=(0.3, 0.3, 0.3, 1),
                              size_hint_y=None, height=20, halign="left")
        self.ts_label.bind(size=self.ts_label.setter("text_size"))

        self.cards = {}
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter("height"))

        for s in SERVICES:
            card = ServiceCard(s)
            self.cards[s["name"] + s["env"]] = card
            grid.add_widget(card)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(grid)

        btn = Button(
            text="Verificar ahora",
            size_hint_y=None, height=46,
            background_color=(0.12, 0.12, 0.12, 1),
            background_normal="",
            color=(0.8, 0.8, 0.8, 1),
            font_size="13sp"
        )
        btn.bind(on_press=lambda x: self.check_all())

        self.add_widget(title)
        self.add_widget(self.ts_label)
        self.add_widget(scroll)
        self.add_widget(btn)

        self.check_all()
        Clock.schedule_interval(lambda dt: self.check_all(), 30)

    def check_all(self):
        threading.Thread(target=self._run_checks, daemon=True).start()

    def _run_checks(self):
        results = [check_service(s) for s in SERVICES]
        self._apply_results(results)

    @mainthread
    def _apply_results(self, results):
        for r in results:
            key = r["name"] + r["env"]
            if key in self.cards:
                self.cards[key].update(r)
        from datetime import datetime
        self.ts_label.text = "Última verificación: " + datetime.now().strftime("%H:%M:%S")


class ARCAApp(App):
    def build(self):
        self.title = "ARCA Monitor"
        return ARCAMonitor()


if __name__ == "__main__":
    ARCAApp().run()
