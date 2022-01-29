from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from mysql.connector import connect
from kivy.storage.jsonstore import JsonStore
from kivy.core.audio import SoundLoader

localdata = JsonStore("credentials.json")
Validation_Error = ''
enter_sound = SoundLoader.load("audios/enter_in_app.wav")
enter_sound.volume = localdata.get("volume")["value"]

def ValidateName(Name):
    global Validation_Error
    if Name == '':
        Validation_Error = 'EmptyName'
        return False
    elif len(Name)>30:
        Validation_Error = 'Length'
        return False
    for i in Name:
        val = ord(i)
        if val == ord(' '):
            pass
        elif (val>=65 and val<=90):
            pass
        elif (val>=97 and val<=122):
            pass
        else:
            Validation_Error = 'InvalidName'
            return False
    Validation_Error = ''
    return True

def ValidateUsername(Username):
    global Validation_Error
    if not (len(Username)<=15 and len(Username)>=3):
        Validation_Error = 'Length'
        return False
    for i in Username:
        val = ord(i)
        if val == ord('_'):
            pass
        elif (val>=48 and val<=57):
            pass
        elif (val>=65 and val<=90):
            pass
        elif (val>=97 and val<=122):
            pass
        else:
            Validation_Error = 'InvalidUsername'
            return False
    Validation_Error = ''
    return True

def ValidatePassword(Password):
    global Validation_Error
    if not (len(Password)<=15 and len(Password)>=8):
        Validation_Error = 'Length'
        return False
    for i in Password:
        val = ord(i)
        if (val>=48 and val<=57):
            pass
        elif (val>=65 and val<=90):
            pass
        elif (val>=97 and val<=122):
            pass
        else:
            Validation_Error = 'InvalidPassword'
            return False
    Validation_Error = ''
    return True



class SignIn(Screen):
    def ClearError(self, instance):
        global Validation_Error
        self.ids.sign_in_error.text = ''
        Validation_Error = ''

    def CheckPwd(self, instance):
        id = self.ids.sign_in_id_input.text
        pwd = self.ids.sign_in_pwd_input.text
        flag = -1
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
                    SELECT Password, Name, Matches, Goals FROM Credentials
                    WHERE Username = "{id}";
                    """
                    )
            check = cur.fetchone()
            if check == None:
                flag = 0
            elif check[0] != pwd:
                flag = 1
            else:
                flag = check
            #conn.commit()
            cur.close()
            conn.close()
        except:
            flag = -1
            self.ids.sign_in_error.text = "Unable to connect to the server"
            Clock.schedule_once(self.ClearError,7)
            try:
                conn.rollback()
            except:
                pass
        return flag

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
            self.manager.get_screen("HomeWindow").ids.id1.text = list[0][0]
            self.manager.get_screen("HomeWindow").ids.goals1.text = str(list[0][1])
            self.manager.get_screen("HomeWindow").ids.matches1.text = str(list[0][2])
            self.manager.get_screen("HomeWindow").ids.id2.text = list[1][0]
            self.manager.get_screen("HomeWindow").ids.goals2.text = str(list[1][1])
            self.manager.get_screen("HomeWindow").ids.matches2.text = str(list[1][2])
            self.manager.get_screen("HomeWindow").ids.id3.text = list[2][0]
            self.manager.get_screen("HomeWindow").ids.goals3.text = str(list[2][1])
            self.manager.get_screen("HomeWindow").ids.matches3.text = str(list[2][2])
            self.manager.get_screen("HomeWindow").ids.id4.text = list[3][0]
            self.manager.get_screen("HomeWindow").ids.goals4.text = str(list[3][1])
            self.manager.get_screen("HomeWindow").ids.matches4.text = str(list[3][2])
            self.manager.get_screen("HomeWindow").ids.id5.text = list[4][0]
            self.manager.get_screen("HomeWindow").ids.goals5.text = str(list[4][1])
            self.manager.get_screen("HomeWindow").ids.matches5.text = str(list[4][2])
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


    def ValidateLogIn(self):
        global localdata
        global Validation_Error
        global enter_sound
        if not ValidateUsername(self.ids.sign_in_id_input.text):
            if Validation_Error == 'Length':
                self.ids.sign_in_error.text = "Username length should be (3-15)"
            elif Validation_Error == 'InvalidUsername':
                self.ids.sign_in_error.text = "Username can contain only\nalphabets, numbers, underscore"
            Clock.schedule_once(self.ClearError,5)
        elif not ValidatePassword(self.ids.sign_in_pwd_input.text):
            if Validation_Error == 'Length':
                self.ids.sign_in_error.text = "Password length should be (8-15)"
            elif Validation_Error == 'InvalidPassword':
                self.ids.sign_in_error.text = "Password can contain only\nalphabets and numbers"
            Clock.schedule_once(self.ClearError,5)
        else:
            check = self.CheckPwd(self)
            if check == 0:
                self.ids.sign_in_error.text = "Account not found"
                Clock.schedule_once(self.ClearError,7)
            elif check == 1:
                self.ids.sign_in_error.text = "Wrong Password"
                Clock.schedule_once(self.ClearError,10)
            elif check != -1:
                enter_sound.play()
                Name = check[1]
                Username = self.ids.sign_in_id_input.text
                Password = self.ids.sign_in_pwd_input.text
                Matches = check[2]
                Goals = check[3]
                localdata.put("details",
                                login = 1,
                                username = f"{Username}",
                                name = f"{Name}"
                                )
                localdata.put("progress",
                                matches = Matches,
                                goals = Goals
                                )
                self.UpdateRanking()
                self.ids.sign_in_id_input.text = ''
                self.ids.sign_in_pwd_input.text = ''
                self.manager.get_screen("SignUpWindow").ids.sign_up_name_input.text = ''
                self.manager.get_screen("SignUpWindow").ids.sign_up_id_input.text = ''
                self.manager.get_screen("SignUpWindow").ids.sign_up_pwd_input.text = ''
                self.manager.get_screen("SignUpWindow").ids.sign_up_pwd_input_confirm.text = ''
                self.manager.get_screen("HomeWindow").ids.HomeName.text = Name
                self.manager.get_screen("SettingWindow").ids.SettingID.text = Username
                self.manager.get_screen("HomeWindow").ids.matches.text = str(Matches)
                self.manager.get_screen("HomeWindow").ids.goals.text = str(Goals)
                self.manager.current = 'HomeWindow'

class SignUp(Screen):
    def ClearError(self, instance):
        global Validation_Error
        self.ids.sign_up_error.text = ''
        Validation_Error = ''

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
            self.manager.get_screen("HomeWindow").ids.id1.text = list[0][0]
            self.manager.get_screen("HomeWindow").ids.goals1.text = str(list[0][1])
            self.manager.get_screen("HomeWindow").ids.matches1.text = str(list[0][2])
            self.manager.get_screen("HomeWindow").ids.id2.text = list[1][0]
            self.manager.get_screen("HomeWindow").ids.goals2.text = str(list[1][1])
            self.manager.get_screen("HomeWindow").ids.matches2.text = str(list[1][2])
            self.manager.get_screen("HomeWindow").ids.id3.text = list[2][0]
            self.manager.get_screen("HomeWindow").ids.goals3.text = str(list[2][1])
            self.manager.get_screen("HomeWindow").ids.matches3.text = str(list[2][2])
            self.manager.get_screen("HomeWindow").ids.id4.text = list[3][0]
            self.manager.get_screen("HomeWindow").ids.goals4.text = str(list[3][1])
            self.manager.get_screen("HomeWindow").ids.matches4.text = str(list[3][2])
            self.manager.get_screen("HomeWindow").ids.id5.text = list[4][0]
            self.manager.get_screen("HomeWindow").ids.goals5.text = str(list[4][1])
            self.manager.get_screen("HomeWindow").ids.matches5.text = str(list[4][2])
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

    def ValidateAccountCreation(self):
        global localdata
        global Validation_Error
        global enter_sound
        if not ValidateName(self.ids.sign_up_name_input.text):
            if Validation_Error == 'EmptyName':
                self.ids.sign_up_error.text = "Name field can't be blank"
            elif Validation_Error == 'InvalidName':
                self.ids.sign_up_error.text = "Name can contain only alphabets"
            elif Validation_Error == 'Length':
                self.ids.sign_up_error.text = "Name length can't exceed 30"
            Clock.schedule_once(self.ClearError,5)
        elif not ValidateUsername(self.ids.sign_up_id_input.text):
            if Validation_Error == 'Length':
                self.ids.sign_up_error.text = "Username length should be (3-15)"
            elif Validation_Error == 'InvalidUsername':
                self.ids.sign_up_error.text = "Username can contain only\nalphabets, numbers, underscore"
            Clock.schedule_once(self.ClearError,5)
        elif not ValidatePassword(self.ids.sign_up_pwd_input.text):
            if Validation_Error == 'Length':
                self.ids.sign_up_error.text = "Password length should be (8-15)"
            elif Validation_Error == 'InvalidPassword':
                self.ids.sign_up_error.text = "Password can contain only\nalphabets and numbers"
            Clock.schedule_once(self.ClearError,5)
        elif not ValidatePassword(self.ids.sign_up_pwd_input_confirm.text):
            if Validation_Error == 'Length':
                self.ids.sign_up_error.text = "Password length should be (8-15)"
            elif Validation_Error == 'InvalidPassword':
                self.ids.sign_up_error.text = "Password can contain only\nalphabets and numbers"
            Clock.schedule_once(self.ClearError,5)
        elif not self.ids.sign_up_pwd_input.text == self.ids.sign_up_pwd_input_confirm.text:
            self.ids.sign_up_error.text = "Password not matched"
            Clock.schedule_once(self.ClearError,5)
        else:
            Username = self.ids.sign_up_id_input.text
            Name = self.ids.sign_up_name_input.text
            Password = self.ids.sign_up_pwd_input.text
            flag = 0
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
                        SELECT * FROM Credentials
                        WHERE Username = "{Username}";
                        """
                        )
                check = cur.fetchone()
                if check == None:
                    cur.execute(f"""
                        INSERT INTO Credentials
                        (Username, Name, Password)
                        VALUES
                        ("{Username}", "{Name}", "{Password}");
                        """
                        )
                    flag = 1
                conn.commit()
                cur.close()
                conn.close()
            except:
                self.ids.sign_up_error.text = "Unable to connect to the server"
                Clock.schedule_once(self.ClearError,7)
                try:
                    conn.rollback()
                except:
                    pass
            else:
                if flag == 0:
                    self.ids.sign_up_error.text = "Username already exists"
                    Clock.schedule_once(self.ClearError,7)
                elif flag == 1:
                    enter_sound.play()
                    localdata.put("details",
                                    login = 1,
                                    username = f"{Username}",
                                    name = f"{Name}"
                                    )
                    localdata.put("progress",
                                    matches = 0,
                                    goals = 0
                                    )
                    self.UpdateRanking()
                    self.ids.sign_up_name_input.text = ''
                    self.ids.sign_up_id_input.text = ''
                    self.ids.sign_up_pwd_input.text = ''
                    self.ids.sign_up_pwd_input_confirm.text = ''
                    self.manager.get_screen("SignInWindow").ids.sign_in_id_input.text = ''
                    self.manager.get_screen("SignInWindow").ids.sign_in_pwd_input.text = ''
                    self.manager.get_screen("HomeWindow").ids.HomeName.text = Name
                    self.manager.get_screen("SettingWindow").ids.SettingID.text = Username
                    self.manager.get_screen("HomeWindow").ids.matches.text = str(0)
                    self.manager.get_screen("HomeWindow").ids.goals.text = str(0)
                    self.manager.current = 'HomeWindow'
