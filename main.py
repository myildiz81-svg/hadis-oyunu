import os
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.image import Image
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager

# Mobil uyumlu ekran boyutu
Window.size = (360, 640)

# --- GİRİŞ EKRANI ---
class WelcomeScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # HATA DÜZELTİLDİ: Çökmeye sebep olan geçersiz komut kaldırıldı, yerine pos_hint ve adaptive_height eklendi.
        layout = MDBoxLayout(
            orientation="vertical", 
            padding=dp(20), 
            spacing=dp(30), 
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            adaptive_height=True
        )
        
        # Oyun Adı
        title = MDLabel(
            text="HADİSLERLE\nKARAKTER EĞİTİMİ",
            halign="center",
            font_style="H4",
            theme_text_color="Primary",
            bold=True
        )
        
        # Slogan
        subtitle = MDLabel(
            text="Doğru kararlar ver, hadisleri öğren!",
            halign="center",
            font_style="Subtitle1",
            theme_text_color="Secondary"
        )

        # Başla Butonu
        start_btn = MDRaisedButton(
            text="HADİ BAŞLAYALIM",
            pos_hint={"center_x": 0.5},
            size_hint=(0.8, None),
            height=dp(50),
            on_release=self.go_to_game
        )

        layout.add_widget(title)
        layout.add_widget(subtitle)
        layout.add_widget(start_btn)
        self.add_widget(layout)

    def go_to_game(self, instance):
        self.manager.current = "game_screen"
        self.manager.get_screen("game_screen").start_level()

# --- OYUN EKRANI ---
class GameScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_level = 0
        self.lives = 3
        self.score = 0
        self.dialog = None
        self.event = None
        
        # Veritabanı
        self.levels = [
            {
                "part1": [f"assets/v1_p1_kare{i}.png" for i in range(1, 5)],
                "part2": [f"assets/v1_p2_kare{i}.png" for i in range(1, 3)],
                "question": "Pazarcı, çürük elmaları müşteriden gizleyerek mi yoksa dürüstçe ayırarak mı satmalı?",
                "options": ["Gizleyip satmalı", "Dürüstçe ayırmalı"],
                "correct_option": 1, 
                "hadith_text": "Bizi aldatan bizden değildir.\n(Müslim, İman, 164)"
            },
            {
                "part1": [f"assets/v2_p1_kare{i}.png" for i in range(1, 5)],
                "part2": [f"assets/v2_p2_kare{i}.png" for i in range(1, 3)],
                "question": "Soğukta bekleyen birini gördüğümüzde, ekmeğimizi onunla paylaşmalı mıyız?",
                "options": ["Evine gitmeli", "Ekmeğini paylaşmalı"],
                "correct_option": 1, 
                "hadith_text": "Komşusu açken tok yatan bizden değildir.\n(İbn Ebî Şeybe, Musannef, 6)"
            },
            {
                "part1": [f"assets/v3_p1_kare{i}.png" for i in range(1, 5)],
                "part2": [f"assets/v3_p2_kare{i}.png" for i in range(1, 3)],
                "question": "Projesi yanlışlıkla kırılan biri, öfkesine yenilip kavga mı etmeli yoksa susmalı mı?",
                "options": ["Kavga etmeli", "Susup sakin kalmalı"],
                "correct_option": 1, 
                "hadith_text": "Öfkelendiğin zaman sus!\n(Müsned, I, 239)"
            },
            {
                "part1": [f"assets/v4_p1_kare{i}.png" for i in range(1, 5)],
                "part2": [f"assets/v4_p2_kare{i}.png" for i in range(1, 3)],
                "question": "Bir işveren, çalışanının hakkını ne zaman ödemelidir?",
                "options": ["Sonra ödemeli", "Hemen ödemeli"],
                "correct_option": 1, 
                "hadith_text": "İşçiye ücretini teri kurumadan veriniz.\n(İbn Mâce, Rehin, 4)"
            },
            {
                "part1": [f"assets/v5_p1_kare{i}.png" for i in range(1, 5)],
                "part2": [f"assets/v5_p2_kare{i}.png" for i in range(1, 3)],
                "question": "Yağmurda mahsur kalmış bir kedi yavrusu gördüğümüzde ona yardım etmeli miyiz?",
                "options": ["Yoluna devam et", "Şemsiyenle koru"],
                "correct_option": 1, 
                "hadith_text": "Yerdekilere merhamet edin ki, gökteki de size merhamet etsin.\n(Tirmizî, Birr, 16)"
            }
        ]

        # Ana Düzen
        self.layout = MDBoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        
        # Üst Panel (Kalpler ve Skor)
        self.top_bar = MDBoxLayout(size_hint_y=0.1, padding=[dp(10), 0])
        
        self.hearts_layout = MDBoxLayout(spacing=dp(5), adaptive_width=True)
        self.update_hearts() # Kalpleri oluştur
        
        self.score_label = MDLabel(text=f"Puan: {self.score}", halign="right", font_style="H6")
        
        self.top_bar.add_widget(self.hearts_layout)
        self.top_bar.add_widget(self.score_label)
        self.layout.add_widget(self.top_bar)

        # Resim Oynatıcı
        self.image_player = Image(allow_stretch=True, keep_ratio=True)
        self.layout.add_widget(self.image_player)

        # Hadis Metni
        self.hadith_label = MDLabel(text="", halign="center", theme_text_color="Custom", text_color=(0, 0.5, 0, 1), font_style="Subtitle1", size_hint_y=None, height=dp(0), opacity=0)
        self.layout.add_widget(self.hadith_label)

        # Buton
        self.next_button = MDRaisedButton(text="Sonraki Hadise Geç", pos_hint={"center_x": 0.5}, opacity=0, disabled=True, on_release=self.next_level)
        self.layout.add_widget(self.next_button)

        self.add_widget(self.layout)

    def update_hearts(self):
        self.hearts_layout.clear_widgets()
        for i in range(self.lives):
            # HATA KORUMASI: Farklı KivyMD sürümlerinde ikon renkleri çökmesin diye her iki parametreyi de verdik.
            heart = MDIconButton(
                icon="heart", 
                theme_text_color="Custom", text_color=(1, 0, 0, 1),
                theme_icon_color="Custom", icon_color=(1, 0, 0, 1)
            )
            self.hearts_layout.add_widget(heart)

    def start_level(self):
        if self.current_level < len(self.levels):
            self.hadith_label.opacity = 0
            self.hadith_label.height = dp(0)
            self.next_button.opacity = 0
            self.next_button.disabled = True
            images = self.levels[self.current_level]["part1"]
            self.play_sequence(images, self.show_question_dialog)
        else:
            self.show_game_over(True)

    def play_sequence(self, images, on_complete_callback):
        if self.event: self.event.cancel()
        self.sequence_images = images
        self.sequence_index = 0
        self.on_complete = on_complete_callback
        self.update_image()
        if len(self.sequence_images) > 1:
            self.event = Clock.schedule_interval(self.next_frame, 4.0)
        else:
            Clock.schedule_once(lambda dt: self.on_complete(), 4.0)

    def next_frame(self, dt):
        self.sequence_index += 1
        if self.sequence_index < len(self.sequence_images):
            self.update_image()
            return True
        else:
            if self.event: self.event.cancel()
            if self.on_complete: self.on_complete()
            return False

    def update_image(self):
        img_path = self.sequence_images[self.sequence_index]
        if os.path.exists(img_path):
            self.image_player.source = img_path

    def show_question_dialog(self):
        level_data = self.levels[self.current_level]
        buttons = []
        for i, option in enumerate(level_data["options"]):
            btn = MDRaisedButton(text=option, on_release=lambda x, idx=i: self.check_answer(idx))
            buttons.append(btn)

        self.dialog = MDDialog(
            title="NE YAPMALISIN?",
            text=level_data["question"],
            buttons=buttons,
            auto_dismiss=False
        )
        self.dialog.open()

    def check_answer(self, selected_index):
        self.dialog.dismiss()
        level_data = self.levels[self.current_level]
        if selected_index == level_data["correct_option"]:
            self.score += 10
            self.score_label.text = f"Puan: {self.score}"
            self.play_sequence(level_data["part2"], self.show_hadith)
        else:
            self.lives -= 1
            self.update_hearts()
            if self.lives <= 0:
                self.show_game_over(False)
            else:
                self.show_question_dialog()

    def show_hadith(self):
        self.hadith_label.text = self.levels[self.current_level]["hadith_text"]
        self.hadith_label.height = dp(80)
        self.hadith_label.opacity = 1
        self.next_button.opacity = 1
        self.next_button.disabled = False

    def next_level(self, instance):
        self.current_level += 1
        self.start_level()

    def show_game_over(self, is_win):
        self.dialog = MDDialog(
            title="TEBRİKLER!" if is_win else "OYUN BİTTİ",
            text=f"Oyun tamamlandı.\nToplam Puanın: {self.score}" if is_win else "Canın kalmadı. Tekrar dene!",
            buttons=[MDFlatButton(text="KAPAT", on_release=lambda x: MDApp.get_running_app().stop())],
            auto_dismiss=False
        )
        self.dialog.open()

# --- UYGULAMA ---
class HadisOyunuApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.theme_style = "Light"
        
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name="welcome_screen"))
        sm.add_widget(GameScreen(name="game_screen"))
        
        return sm

if __name__ == "__main__":
    HadisOyunuApp().run()