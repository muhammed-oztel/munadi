import gi
import json
from datetime import date

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


def load_ezan(json_path: str) -> dict:
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def bugunun_vakitleri(ezan: dict) -> tuple[dict | None, str]:
    bugun = date.today().strftime("%Y-%m-%d")
    return ezan.get(bugun), bugun


class MunadiApp(Gtk.Application):
    def __init__(self, ezan: dict):
        super().__init__(application_id="com.mfo.munadi")
        self.ezan = ezan

    def do_activate(self):
        vakitler, bugun = bugunun_vakitleri(self.ezan)

        window = Gtk.ApplicationWindow(application=self)
        window.set_title("Munadî")
        window.set_default_size(400, 300)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        main_box.set_margin_top(20)
        main_box.set_margin_bottom(20)
        main_box.set_margin_start(20)
        main_box.set_margin_end(20)

        if vakitler:
            baslik = Gtk.Label()
            baslik.set_markup(
                f"<b>Bugünün Ezan Vakitleri</b>\n"
                f"<small>{bugun}  •  {vakitler['hicri']}</small>"
            )
            baslik.set_justify(Gtk.Justification.CENTER)
        else:
            baslik = Gtk.Label(label=f"{bugun} için veri bulunamadı.")

        main_box.append(baslik)

        if vakitler:
            grid = Gtk.Grid()
            grid.set_row_spacing(10)
            grid.set_column_spacing(40)
            grid.set_halign(Gtk.Align.CENTER)

            header_vakit = Gtk.Label()
            header_vakit.set_markup("<b>Vakit</b>")
            header_vakit.set_halign(Gtk.Align.START)

            header_saat = Gtk.Label()
            header_saat.set_markup("<b>Saat</b>")
            header_saat.set_halign(Gtk.Align.END)

            grid.attach(header_vakit, 0, 0, 1, 1)
            grid.attach(header_saat, 1, 0, 1, 1)

            ezan_satirlari = [
                ("İmsak",   vakitler["imsak"]),
                ("Güneş",   vakitler["gunes"]),
                ("Öğle",    vakitler["ogle"]),
                ("İkindi",  vakitler["ikindi"]),
                ("Akşam",   vakitler["aksam"]),
                ("Yatsı",   vakitler["yatsi"]),
            ]

            for i, (vakit, saat) in enumerate(ezan_satirlari):
                lbl_vakit = Gtk.Label()
                lbl_vakit.set_markup(f"{vakit}")
                lbl_vakit.set_halign(Gtk.Align.START)

                lbl_saat = Gtk.Label()
                lbl_saat.set_markup(f"<b>{saat}</b>")
                lbl_saat.set_halign(Gtk.Align.CENTER)

                grid.attach(lbl_vakit, 0, i + 1, 1, 1)
                grid.attach(lbl_saat, 1, i + 1, 1, 1)

            main_box.append(grid)

        window.set_child(main_box)
        window.present()


if __name__ == "__main__":
    ezan = load_ezan("./resources/ezan_istanbul_2026.json")
    app = MunadiApp(ezan)
    app.run(None)