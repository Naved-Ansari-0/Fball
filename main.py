from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import WipeTransition
from kivy.graphics import RoundedRectangle, Ellipse
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
from mysql.connector import connect
from kivy.vector import Vector
from kivy.core.audio import SoundLoader
import login_page
import game

from kivy.utils import platform

if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])


localdata = JsonStore("credentials.json")

# Remember to COMMENT Keyboard controls while making apk
# Also comment Window.size in main.py and game.py
# Also remove the opponent_score label from game.kv

Window.size = (360,640)
Window.clearcolor = (197/255,205/255,217/255,1)
Builder.load_file("design.kv")
Builder.load_file("signin.kv")
Builder.load_file("signup.kv")
Builder.load_file("home.kv")
Builder.load_file("setting.kv")
Builder.load_file("game.kv")


logout_sound = SoundLoader.load("audios/quit_app.wav")
logout_sound.volume = localdata.get("volume")["value"]
start_game_sound = SoundLoader.load("audios/start_game.wav")
start_game_sound.volume = localdata.get("volume")["value"]

class Setting(Screen, Widget):
    localdata = JsonStore("credentials.json")

    def ClearCredentials(self):
        localdata.put("details", login = 0, username = "", name = "")
        localdata.put("progress", matches = 0, goals = 0)
        # self.manager.get_screen("HomeWindow").ids.HomeName.text = ""
        # self.ids.SettingID.text = ""
        logout_sound.play()

    def DeleteAccount(self):
        try:
            ID = self.ids.SettingID.text
            conn = connect(
                    host = "",
                    port = 0,
                    database = "",
                    user = "",
                    password = ""
                    )
            cur = conn.cursor()
            cur.execute(f"""
                        DELETE FROM Credentials
                        WHERE Username = "{ID}";
                        """)
            conn.commit()
            cur.close()
            conn.close()
        except:
            try:
                conn.rollback()
            except:
                pass
        else:
            self.ClearCredentials()
            self.manager.transition = WipeTransition()
            self.manager.current = "SignInWindow"


    def ChangeVolume(self):
        localdata.put("volume", value = self.ids.GameSound.value)
        game.goal_sound.volume = self.ids.GameSound.value
        game.shoot_sound.volume = self.ids.GameSound.value
        game.quit_game_sound.volume = self.ids.GameSound.value
        game.mistake_sound.volume = self.ids.GameSound.value
        login_page.enter_sound.volume = self.ids.GameSound.value
        login_page.enter_sound.volume = self.ids.GameSound.value
        logout_sound.volume = self.ids.GameSound.value
        start_game_sound.volume = self.ids.GameSound.value

class Home(Screen):
    localdata = JsonStore("credentials.json")
    ranking = JsonStore("ranking.json")
    # def MakeConnection(self):
    #     game.ConnectOnline()
    def PlayGame(self):
        start_game_sound.play()
        localdata = JsonStore("credentials.json")
        Matches = localdata.get("progress")["matches"]
        Goals = localdata.get("progress")["goals"]
        localdata.put("progress",
                        matches = Matches + 1,
                        goals = Goals
                        )
        self.ids.matches.text = str(localdata.get("progress")["matches"])


    def SyncData(self):
        try:
            localdata = JsonStore("credentials.json")
            Matches = localdata.get("progress")["matches"]
            Goals = localdata.get("progress")["goals"]
            ID = localdata.get("details")["username"]
            conn = connect(
                    host = "",
                    port = 0,
                    database = "",
                    user = "",
                    password = ""
                    )
            cur = conn.cursor()
            cur.execute(f"""
                        UPDATE Credentials SET
                        Goals = {Goals},
                        Matches = {Matches}
                        WHERE Username = "{ID}";
                        """)
            conn.commit()
            cur.close()
            conn.close()
            Clock.schedule_interval(self.StartRotate, 1/30)
            Clock.schedule_once(self.StopRotate, 10)
        except:
            try:
                conn.rollback()
            except:
                pass
        else:
            self.ids.sync.angle -= 90

    def UpdateRanking(self):
        try:
            conn = connect(
                    host = "",
                    port = 0,
                    database = "",
                    user = "",
                    password = ""
                    )
            cur = conn.cursor()
            cur.execute(f"""
                        SELECT Username, Goals, Matches FROM Credentials
                        ORDER BY Goals DESC LIMIT 5;
                        """)
            list = cur.fetchall()
            cur.close()
            conn.close()
        except:
            try:
                conn.rollback()
            except:
                pass
        else:
            self.ids.id1.text = list[0][0]
            self.ids.goals1.text = str(list[0][1])
            self.ids.matches1.text = str(list[0][2])
            self.ids.id2.text = list[1][0]
            self.ids.goals2.text = str(list[1][1])
            self.ids.matches2.text = str(list[1][2])
            self.ids.id3.text = list[2][0]
            self.ids.goals3.text = str(list[2][1])
            self.ids.matches3.text = str(list[2][2])
            self.ids.id4.text = list[3][0]
            self.ids.goals4.text = str(list[3][1])
            self.ids.matches4.text = str(list[3][2])
            self.ids.id5.text = list[4][0]
            self.ids.goals5.text = str(list[4][1])
            self.ids.matches5.text = str(list[4][2])
            ranking = JsonStore("ranking.json")
            ranking.put("1", username = list[0][0],
                               goals = list[0][1],
                               matches = list[0][2]
                         )
            ranking.put("2", username = list[1][0],
                               goals = list[1][1],
                               matches = list[1][2]
                         )
            ranking.put("3", username = list[2][0],
                               goals = list[2][1],
                               matches = list[2][2]
                         )
            ranking.put("4", username = list[3][0],
                               goals = list[3][1],
                               matches = list[3][2]
                         )
            ranking.put("5", username = list[4][0],
                               goals = list[4][1],
                               matches = list[4][2]
                         )


class MyApp(App):
    def build(self):

        sm = ScreenManager()

        if localdata.get("details")["login"] == 1:
            sm.add_widget(Home(name='HomeWindow'))
            sm.add_widget(Setting(name='SettingWindow'))
            sm.add_widget(game.Game(name='GameWindow'))
            sm.add_widget(login_page.SignIn(name='SignInWindow'))
            sm.add_widget(login_page.SignUp(name='SignUpWindow'))
        else:
            sm.add_widget(login_page.SignIn(name='SignInWindow'))
            sm.add_widget(login_page.SignUp(name='SignUpWindow'))
            sm.add_widget(Home(name='HomeWindow'))
            sm.add_widget(game.Game(name='GameWindow'))
            sm.add_widget(Setting(name='SettingWindow'))

        return sm

if __name__ == "__main__":
    MyApp().run()
