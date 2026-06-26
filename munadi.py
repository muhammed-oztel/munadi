import gi
import json
from datetime import date, datetime
import os

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_ezan(json_path: str) -> dict:
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)


def bugunun_vakitleri(ezan: dict) -> tuple[dict | None, str]:
    bugun = date.today().strftime("%Y-%m-%d")
    return ezan.get(bugun), bugun


def sonraki_vakit(vakitler: dict) -> tuple[str, str] | None:
    """Bir sonraki vaktin adını ve saatini döndürür."""
    simdiki_saat = datetime.now().strftime("%H:%M")
    siradaki = [
        ("İmsak",  vakitler["imsak"]),
        ("Güneş",  vakitler["gunes"]),
        ("Öğle",   vakitler["ogle"]),
        ("İkindi", vakitler["ikindi"]),
        ("Akşam",  vakitler["aksam"]),
        ("Yatsı",  vakitler["yatsi"]),
    ]
    for ad, saat in siradaki:
        if saat > simdiki_saat:
            return ad, saat
    return None 


def kalan_sure(hedef_saat: str) -> str:
    """HH:MM formatındaki hedefe kaç saat/dakika kaldığını döndürür."""
    simdi = datetime.now()
    hedef = simdi.replace(
        hour=int(hedef_saat[:2]),
        minute=int(hedef_saat[3:]),
        second=0,
        microsecond=0,
    )
    fark = hedef - simdi
    toplam_dakika = int(fark.total_seconds() // 60)
    if toplam_dakika <= 0:
        return "—"
    saat, dakika = divmod(toplam_dakika, 60)
    if saat > 0:
        return f"{saat} sa {dakika} dk"
    return f"{dakika} dk"


class MunadiApp(Gtk.Application):
    def __init__(self, ezan: dict):
        super().__init__(application_id="com.mfo.munadi")
        self.ezan = ezan

    def do_activate(self):
        vakitler, bugun = bugunun_vakitleri(self.ezan)

        window = Gtk.ApplicationWindow(application=self)
        window.set_title("Munadî")
        window.set_default_size(400, 380)

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

        self.saat_label = Gtk.Label()
        self.saat_label.set_markup(
            f"<span font='24' weight='bold'>{datetime.now().strftime('%H:%M:%S')}</span>"
        )
        main_box.append(self.saat_label)

        self.sonraki_label = Gtk.Label()
        self._sonraki_guncelle(vakitler)
        main_box.append(self.sonraki_label)

        if vakitler:
            self.vakit_satirlari = [
                ("İmsak",  vakitler["imsak"]),
                ("Güneş",  vakitler["gunes"]),
                ("Öğle",   vakitler["ogle"]),
                ("İkindi", vakitler["ikindi"]),
                ("Akşam",  vakitler["aksam"]),
                ("Yatsı",  vakitler["yatsi"]),
            ]

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

            self.satir_labelleri = []
            for i, (vakit, saat) in enumerate(self.vakit_satirlari):
                lbl_vakit = Gtk.Label()
                lbl_vakit.set_halign(Gtk.Align.START)

                lbl_saat = Gtk.Label()
                lbl_saat.set_halign(Gtk.Align.CENTER)

                grid.attach(lbl_vakit, 0, i + 1, 1, 1)
                grid.attach(lbl_saat, 1, i + 1, 1, 1)
                self.satir_labelleri.append((lbl_vakit, lbl_saat, vakit, saat))

            self._satir_renklerini_guncelle()
            main_box.append(grid)

        window.set_child(main_box)
        window.present()

        self.vakitler = vakitler
        # Her saniye güncelle
        GLib.timeout_add_seconds(1, self._her_saniye)

    def _sonraki_guncelle(self, vakitler):
        if not vakitler:
            self.sonraki_label.set_markup("")
            return
        sonraki = sonraki_vakit(vakitler)
        if sonraki:
            ad, saat = sonraki
            kalan = kalan_sure(saat)
            self.sonraki_label.set_markup(
                f"<small>Sonraki vakit: <b>{ad} ({saat})</b>  —  <b>{kalan}</b> kaldı</small>"
            )
        else:
            self.sonraki_label.set_markup(
                "<small><i>Bugünün tüm vakitleri geçti.</i></small>"
            )

    def _satir_renklerini_guncelle(self):
        """Aktif (en yakın geçmiş) vakti vurgula."""
        simdiki_saat = datetime.now().strftime("%H:%M")
        aktif_index = -1

        for i, (lbl_vakit, lbl_saat, vakit, saat) in enumerate(self.satir_labelleri):
            if saat <= simdiki_saat:
                aktif_index = i

        for i, (lbl_vakit, lbl_saat, vakit, saat) in enumerate(self.satir_labelleri):
            if i == aktif_index:
                lbl_vakit.set_markup(f"<b><span foreground='#f5a623'>{vakit}</span></b>")
                lbl_saat.set_markup(f"<b><span foreground='#f5a623'>{saat}</span></b>")
            else:
                lbl_vakit.set_markup(f"{vakit}")
                lbl_saat.set_markup(f"<b>{saat}</b>")

    def _her_saniye(self) -> bool:
        self.saat_label.set_markup(
            f"<span font='24' weight='bold'>{datetime.now().strftime('%H:%M:%S')}</span>"
        )
        self._sonraki_guncelle(self.vakitler)
        self._satir_renklerini_guncelle()
        return True


if __name__ == "__main__":
    ezan = load_ezan(os.path.join(BASE_DIR, "resources", "ezan_istanbul_2026.json"))
    app = MunadiApp(ezan)
    app.run(None)