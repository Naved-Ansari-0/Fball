from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.vector import Vector
from mysql.connector import connect
from kivy.storage.jsonstore import JsonStore
from kivy.core.audio import SoundLoader

Window.size = (360,640)

localdata = JsonStore("credentials.json")
goal_sound = SoundLoader.load("audios/goal.wav")
goal_sound.volume = localdata.get("volume")["value"]
shoot_sound = SoundLoader.load("audios/shoot.wav")
shoot_sound.volume = localdata.get("volume")["value"]
quit_game_sound = SoundLoader.load("audios/quit_game.wav")
quit_game_sound.volume = localdata.get("volume")["value"]
mistake_sound = SoundLoader.load("audios/mistake.wav")
mistake_sound.volume = localdata.get("volume")["value"]


conn = ''
cur = ''

# def ConnectOnline():
#
#     global conn, cur
#     localdata = JsonStore("credentials.json")
#     ID = localdata.get("details")["username"]
#
#     try:
#         conn = connect(
#                 host = "",
#                 port = 0,
#                 database = "",
#                 user = "",
#                 password = ""
#                 )
#         cur = conn.cursor()
#         cur.execute(f"""
#                     INSERT INTO Games (Username)
#                     VALUES
#                     ("{ID}");
#                     """
#                     )
#     except:
#         try:
#             conn.rollback()
#         except:
#             pass
#     else:
#         conn.commit()


class Game(Screen):
    p_trans = 0
    p_pos_ch = min(Window.width/120,Window.height/120)
    p_fps = 1/30
    p_cur_mv = "up"
    opp_response = 0
    opp_active = 0
    opp_trans = 0

    global cur, conn
    global goal_sound, shoot_sound, quit_game_sound, mistake_sound
    global localdata

    # send_f = 1/10
    # def SendPlayerPos(self, instance):
    #         try:
    #             cur.execute(f"""
    #                         UPDATE Games SET
    #                         x = {self.ids.player.center_x},
    #                         y = {self.ids.player.y}
    #                         WHERE Username = "{self.ID}"
    #                         ORDER BY id DESC LIMIT 1;
    #                         """
    #                         )
    #             conn.commit()
    #         except:
    #             try:
    #                 conn.rollback()
    #             except:
    #                 pass


    def EndGame(self):
        quit_game_sound.play()
        self.RestoreControls()
        self.end_motion()
        #self.ids.opponent_score.text = "0"
        self.ids.my_score.text = "0"
        self.ids.ball.center_x = Window.width/2
        self.ids.ball.y = Window.height*53/100
        self.ids.player.center_x = Window.width/2
        self.ids.player.y = Window.height*25/100
        self.ids.player.source = "images/player-back-still.png"
        self.ids.opponent.source = "images/opponent-front-still.png"
        self.ids.opponent.pos = (Window.width*19/40, Window.height*88/100)
        self.opp_response = 0
        self.opp_active = 0
        self.DeactivateOpponent()
        self.move_dirc = "left"
        self.opp_trans = 0


    def HideControls(self):
        self.ids.up_bt.disabled = True
        self.ids.down_bt.disabled = True
        self.ids.left_bt.disabled = True
        self.ids.right_bt.disabled = True
        self.ids.shoot_bt_l.disabled = True
        self.ids.shoot_bt_r.disabled = True
        self.ids.up_bt.background_color = (0,0,0,0)
        self.ids.down_bt.background_color = (0,0,0,0)
        self.ids.left_bt.background_color = (0,0,0,0)
        self.ids.right_bt.background_color = (0,0,0,0)
        self.ids.shoot_bt_l.background_color = (0,0,0,0)
        self.ids.shoot_bt_r.background_color = (0,0,0,0)
        self.ids.shoot_bt_l.text = ""
        self.ids.shoot_bt_r.text = ""
        self.ids.up_img.color = (0,0,0,0)
        self.ids.down_img.color = (0,0,0,0)
        self.ids.left_img.color = (0,0,0,0)
        self.ids.right_img.color = (0,0,0,0)
        self.ids.response_bt.disabled = False
        self.ids.response_bt.text = "Continue"
        self.ids.response_bt.color = (11/255, 100/255, 113/255,1)
        self.ids.response_bt.background_color = (1,1,1,1)
        self.opp_response = 0


    def RestoreControls(self):
        self.ids.up_bt.disabled = False
        self.ids.down_bt.disabled = False
        self.ids.left_bt.disabled = False
        self.ids.right_bt.disabled = False
        self.ids.shoot_bt_l.disabled = False
        self.ids.shoot_bt_r.disabled = False
        self.ids.up_bt.background_color = (1,0,0,1)
        self.ids.down_bt.background_color = (1,0,0,1)
        self.ids.left_bt.background_color = (1,0,0,1)
        self.ids.right_bt.background_color = (1,0,0,1)
        self.ids.shoot_bt_l.background_color = (1,1,1,1)
        self.ids.shoot_bt_r.background_color = (1,1,1,1)
        self.ids.shoot_bt_l.text = "Shoot"
        self.ids.shoot_bt_r.text = "Shoot"
        self.ids.up_img.color = (1,1,1,1)
        self.ids.down_img.color = (1,1,1,1)
        self.ids.left_img.color = (1,1,1,1)
        self.ids.right_img.color = (1,1,1,1)
        self.ids.response_bt.disabled = True
        self.ids.response_bt.text = ""
        self.ids.response_bt.color = (0,0,0,0)
        self.ids.response_bt.background_color = (0,0,0,0)
        self.ids.response.text = ""

        if self.ball_status == "our-goalkeeper":
            self.ids.ball.center_x = Window.width/2
            self.ids.ball.y = Window.height*24/100
            self.ids.player.center_x = Window.width/2
            self.ids.player.y = Window.height*30/100

        elif self.ball_status == "outside-left":
            self.ids.ball.center_x = Window.width*4/50
            self.ids.player.center_x = self.ids.ball.center_x+20
            self.ids.player.y = self.ids.ball.center_y

        elif self.ball_status == "outside-right":
            self.ids.ball.center_x = Window.width*46/50
            self.ids.player.center_x = self.ids.ball.center_x-20
            self.ids.player.y = self.ids.ball.center_y

        elif self.ball_status != "inside":
            self.ids.ball.center_x = Window.width/2
            self.ids.ball.center_y = Window.height*80/100
            self.ids.player.center_x = Window.width/2
            self.ids.player.y = Window.height*60/100

        self.ball_status = "inside"
        self.ball_vel = 0


    def CheckPlayerPos(self, x, y):
        if self.ids.player.pos[1] >  Window.height*55/100:
            self.opp_response = 1
        else:
            self.opp_response = 0
        if y>=Window.height*22/100 and y<=Window.height*88/100 and x>=Window.width*2/50 and x<=Window.width*48/50:
            return True
        else:
            return False

    def CheckBallRolling(self, x, y):
        if y>=Window.height*23/100 and y<=Window.height*87/100 and x>=Window.width*3/50 and x<=Window.width*47/50:
            return True
        else:
            return False

    def CheckBallKick(self, x, y):
        if y>=Window.height*15/100 and y<=Window.height*100/100 and x>=Window.width*0/50 and x<=Window.width*50/50:
            return True
        else:
            return False


    move_dirc = "left"
    def RunOpponent(self, instance):
        if self.opp_response == 1:
            if self.move_dirc == "left":
                self.ids.opponent.pos[0] -= self.p_pos_ch*( self.ids.player.pos[1]/(Window.height*55/100))
                if self.opp_trans % 12 == 0:
                    self.ids.opponent.source = "images/opponent-left-move-1.png"
                elif self.opp_trans % 6 == 0:
                    self.ids.opponent.source = "images/opponent-left-move-2.png"
                elif self.opp_trans % 9 == 0:
                    self.ids.opponent.source = "images/opponent-left-still.png"
                elif self.opp_trans % 3 == 0:
                    self.ids.opponent.source = "images/opponent-left-still.png"
            elif self.move_dirc == "right":
                self.ids.opponent.pos[0] += self.p_pos_ch*( self.ids.player.pos[1]/(Window.height*55/100))
                if self.opp_trans % 12 == 0:
                    self.ids.opponent.source = "images/opponent-right-move-1.png"
                elif self.opp_trans % 6 == 0:
                    self.ids.opponent.source = "images/opponent-right-move-2.png"
                elif self.opp_trans % 9 == 0:
                    self.ids.opponent.source = "images/opponent-right-still.png"
                elif self.opp_trans % 3 == 0:
                    self.ids.opponent.source = "images/opponent-right-still.png"
            if self.ids.opponent.pos[0] < Window.width*17/50:
                self.move_dirc = "right"
            elif self.ids.opponent.pos[0] > Window.width*28/50:
                self.move_dirc = "left"
        else:
            self.ids.opponent.source = "images/opponent-front-still.png"
        self.opp_trans += 1

    def ActivateOpponent(self):
        Clock.schedule_interval(self.RunOpponent, self.p_fps)

    def DeactivateOpponent(self):
        Clock.unschedule(self.RunOpponent)

    def StopOpponent(self):
        o = Vector(self.ids.opponent.center_x,self.ids.opponent.y)
        b = Vector(self.ids.ball.center)
        if o.distance(b) < min(Window.width/13, Window.height/13):
            self.ball_vel = 0
            self.end_motion()
            mistake_sound.play()
            self.ball_status = "opponent-goalkeeper"
            self.ids.response.text = "Ball went to opponent goalkeeper."
            self.ids.player.source = "images/player-back-still.png"
            self.HideControls()


    # UP Motion
    def RunUp(self, instance):
        if self.p_trans % 10 == 0:
            self.ids.player.source = "images/player-back-move-1.png"
        elif self.p_trans % 5 == 0:
            self.ids.player.source = "images/player-back-move-2.png"
        check_y = self.ids.player.y + self.p_pos_ch
        if self.CheckPlayerPos(self.ids.player.center_x, check_y):
            self.ids.player.y += self.p_pos_ch
        p = Vector(self.ids.player.center_x,self.ids.player.y)
        b = Vector(self.ids.ball.center)
        if p.distance(b) < min(Window.width/30, Window.height/30) and p[1] < b[1]:
            ball_y = self.ids.ball.center_y + self.p_pos_ch
            if self.CheckBallRolling(self.ids.ball.center_x, ball_y):
                self.ids.ball.center_y += self.p_pos_ch
                if self.ids.ball.center_x > self.ids.player.center_x:
                    self.ids.ball.angle -=20
                else:
                    self.ids.ball.angle +=20
                self.StopOpponent()

        self.p_trans += 1


    def MoveUp(self):
        if self.opp_active == 0:
            self.opp_active = 1
            self.ActivateOpponent()
        self.end_motion()
        self.p_cur_mv = "up"
        self.p_trans = 0
        self.ids.player.source = "images/player-back-still.png"
        Clock.schedule_interval(self.RunUp, self.p_fps)
        #Clock.schedule_interval(self.SendPlayerPos, self.send_f)
    def StopUp(self):
        Clock.unschedule(self.RunUp)
        #Clock.unschedule(self.SendPlayerPos)
        self.ids.player.source = "images/player-back-still.png"

    # DOWN Motion
    def RunDown(self, instance):
        if self.p_trans % 10 == 0:
            self.ids.player.source = "images/player-front-move-1.png"
        elif self.p_trans % 5 == 0:
            self.ids.player.source = "images/player-front-move-2.png"
        check_y = self.ids.player.y - self.p_pos_ch
        if self.CheckPlayerPos(self.ids.player.center_x, check_y):
            self.ids.player.y -= self.p_pos_ch
        p = Vector(self.ids.player.center_x,self.ids.player.y)
        b = Vector(self.ids.ball.center)
        if p.distance(b) < min(Window.width/30, Window.height/30) and p[1] > b[1]:
            ball_y = self.ids.ball.center_y - self.p_pos_ch
            if self.CheckBallRolling(self.ids.ball.center_x, ball_y):
                self.ids.ball.center_y -= self.p_pos_ch
                if self.ids.ball.center_x > self.ids.player.center_x:
                    self.ids.ball.angle +=20
                else:
                    self.ids.ball.angle -=20
                self.StopOpponent()

        self.p_trans += 1

    def MoveDown(self):
        self.end_motion()
        self.p_cur_mv = "down"
        self.p_trans = 0
        self.ids.player.source = "images/player-front-still.png"
        Clock.schedule_interval(self.RunDown, self.p_fps)
        #Clock.schedule_interval(self.SendPlayerPos, self.send_f)
    def StopDown(self):
        Clock.unschedule(self.RunDown)
        #Clock.unschedule(self.SendPlayerPos)
        self.ids.player.source = "images/player-front-still.png"

    # LEFT Motion
    def RunLeft(self, instance):
        if self.p_trans % 12 == 0:
            self.ids.player.source = "images/player-left-move-1.png"
        elif self.p_trans % 6 == 0:
            self.ids.player.source = "images/player-left-move-2.png"
        elif self.p_trans % 9 == 0:
            self.ids.player.source = "images/player-left-still.png"
        elif self.p_trans % 3 == 0:
            self.ids.player.source = "images/player-left-still.png"
        check_x = self.ids.player.center_x - self.p_pos_ch
        if self.CheckPlayerPos(check_x, self.ids.player.y):
            self.ids.player.center_x -= self.p_pos_ch

        p = Vector(self.ids.player.center_x,self.ids.player.y)
        b = Vector(self.ids.ball.center)
        if p.distance(b) < min(Window.width/30, Window.height/30) and p[0] > b[0]:
            ball_x = self.ids.ball.center_x - self.p_pos_ch
            if self.CheckBallRolling(ball_x, self.ids.ball.center_y):
                self.ids.ball.center_x -= self.p_pos_ch
                self.ids.ball.angle +=20
                self.StopOpponent()

        self.p_trans += 1

    def MoveLeft(self):
        self.end_motion()
        self.p_cur_mv = "left"
        self.p_trans = 0
        self.ids.player.source = "images/player-left-still.png"
        Clock.schedule_interval(self.RunLeft, self.p_fps)
        #Clock.schedule_interval(self.SendPlayerPos, self.send_f)
    def StopLeft(self):
        Clock.unschedule(self.RunLeft)
        #Clock.unschedule(self.SendPlayerPos)
        self.ids.player.source = "images/player-left-still.png"

    # RIGHT Motion
    def RunRight(self, instance):
        if self.p_trans % 12 == 0:
            self.ids.player.source = "images/player-right-move-1.png"
        elif self.p_trans % 6 == 0:
            self.ids.player.source = "images/player-right-move-2.png"
        elif self.p_trans % 9 == 0:
            self.ids.player.source = "images/player-right-still.png"
        elif self.p_trans % 3 == 0:
            self.ids.player.source = "images/player-right-still.png"
        check_x = self.ids.player.center_x + self.p_pos_ch
        if self.CheckPlayerPos(check_x, self.ids.player.y):
            self.ids.player.center_x += self.p_pos_ch

        p = Vector(self.ids.player.center_x,self.ids.player.y)
        b = Vector(self.ids.ball.center)
        if p.distance(b) < min(Window.width/30, Window.height/30) and p[0] < b[0]:
            ball_x = self.ids.ball.center_x + self.p_pos_ch
            if self.CheckBallRolling(ball_x, self.ids.ball.center_y):
                self.ids.ball.center_x += self.p_pos_ch
                self.ids.ball.angle -=20
                self.StopOpponent()

        self.p_trans += 1
    def MoveRight(self):
        self.end_motion()
        self.p_cur_mv = "right"
        self.p_trans = 0
        self.ids.player.source = "images/player-right-still.png"
        Clock.schedule_interval(self.RunRight, self.p_fps)
        #Clock.schedule_interval(self.SendPlayerPos, self.send_f)
    def StopRight(self):
        Clock.unschedule(self.RunRight)
        #Clock.unschedule(self.SendPlayerPos)
        self.ids.player.source = "images/player-right-still.png"


    def end_motion(self):
        Clock.unschedule(self.RunUp)
        Clock.unschedule(self.RunDown)
        Clock.unschedule(self.RunLeft)
        Clock.unschedule(self.RunRight)
        #Clock.unschedule(self.SendPlayerPos)

    #KEYBOARD CONTROLS
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    prev = ''
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'up':
            self.prev = 'up'
            self.end_motion()
            self.MoveUp()
        elif keycode[1] == 'down':
            self.prev = 'down'
            self.end_motion()
            self.MoveDown()
        elif keycode[1] == 'left':
            self.prev = 'left'
            self.end_motion()
            self.MoveLeft()
        elif keycode[1] == 'right':
            self.prev = 'right'
            self.end_motion()
            self.MoveRight()
        elif keycode[1] == 'end':
            self.end_motion()
            if self.prev == 'down':
                self.ids.player.source = "images/player-front-still.png"
            elif self.prev == 'left':
                self.ids.player.source = "images/player-left-still.png"
            elif self.prev == 'right':
                self.ids.player.source = "images/player-right-still.png"
            else:
                self.ids.player.source = "images/player-back-still.png"

        if keycode[1] == '1':
            self.ball_vel = 10
            self.ShootBall()
        elif keycode[1] == '2':
            self.ball_vel = 20
            self.ShootBall()
        elif keycode[1] == '3':
            self.ball_vel = 30
            self.ShootBall()

    ball_vel = 0
    ball_status = "inside"
    def CalTimeBtDown(self, instance):
        self.ball_vel += 1
        if self.ball_vel > 30:
            self.ball_vel = 30
            Clock.unschedule(self.CalTimeBtDown)

    def BoostKick(self):
        self.ball_vel = 0
        Clock.schedule_interval(self.CalTimeBtDown,1/30)

    def BallDeAccUp(self, instance):
        ball_y = self.ids.ball.center_y + self.ball_vel
        if self.CheckBallKick(self.ids.ball.center_x, ball_y) and self.ball_vel > 0:
            self.ids.ball.center_y += self.ball_vel
            self.StopOpponent()
            if self.ids.ball.center_x > self.ids.player.center_x:
                self.ids.ball.angle -= self.ball_vel
            else:
                self.ids.ball.angle += self.ball_vel
            self.ball_vel -= min(Window.width/150,Window.height/150)

            if self.ids.ball.center_y > Window.height*87/100:
                if self.ids.ball.center_y > Window.height*95/100:
                    if self.ids.ball.center_x > Window.width*19/50 and self.ids.ball.center_x < Window.width*31/50:
                        self.ball_status = "goal"
                    else:
                        self.ball_status = "outside-up"
                else:
                    self.ball_status = "opponent-goalkeeper"
        else:
            Clock.unschedule(self.BallDeAccUp)
            if self.ball_status == "goal":
                goal_sound.play()
                localdata = JsonStore("credentials.json")
                Matches = localdata.get("progress")["matches"]
                Goals = localdata.get("progress")["goals"]
                localdata.put("progress",
                                matches = Matches,
                                goals = Goals + 1
                                )
                self.manager.get_screen("HomeWindow").ids.goals.text = str(localdata.get("progress")["goals"])
                self.ids.my_score.text = str( int(self.ids.my_score.text) + 1)
                self.ids.response.text = "Hurry! Goal Scored."
                self.ids.player.source = "images/player-back-still.png"
            elif self.ball_status != "inside":
                mistake_sound.play()
                self.ids.response.text = "Ball went to opponent goalkeeper."
                self.ids.player.source = "images/player-back-still.png"
            if self.ball_status != "inside":
                self.end_motion()
                self.HideControls()

    def BallDeAccDown(self, instance):
        ball_y = self.ids.ball.center_y - self.ball_vel
        if self.CheckBallKick(self.ids.ball.center_x, ball_y) and self.ball_vel > 0:
            self.ids.ball.center_y -= self.ball_vel
            self.StopOpponent()
            if self.ids.ball.center_x > self.ids.player.center_x:
                self.ids.ball.angle += self.ball_vel
            else:
                self.ids.ball.angle -= self.ball_vel
            self.ball_vel -= min(Window.width/150,Window.height/150)

            if self.ids.ball.center_y < Window.height*23/100:
                self.ball_status = "our-goalkeeper"
        else:
            Clock.unschedule(self.BallDeAccDown)
            if self.ball_status == "our-goalkeeper":
                mistake_sound.play()
                self.ids.response.text = "Ball went to our goalkeeper. Click to take it back."
                self.ids.player.source = "images/player-front-still.png"
                self.end_motion()
                self.HideControls()

    def BallDeAccLeft(self, instance):
        ball_x = self.ids.ball.center_x - self.ball_vel
        if self.CheckBallKick(ball_x, self.ids.ball.center_y) and self.ball_vel > 0:
            self.ids.ball.center_x -= self.ball_vel
            self.StopOpponent()
            self.ids.ball.angle += self.ball_vel
            self.ball_vel -= min(Window.width/150,Window.height/150)

            if self.ids.ball.center_x < Window.width*3/50:
                self.ball_status = "outside-left"
        else:
            Clock.unschedule(self.BallDeAccLeft)
            if self.ball_status == "outside-left":
                mistake_sound.play()
                self.ids.response.text = "Ball went out of boundary. Click to bring it back."
                self.ids.player.source = "images/player-left-still.png"
                self.end_motion()
                self.HideControls()

    def BallDeAccRight(self, instance):
        ball_x = self.ids.ball.center_x + self.ball_vel
        if self.CheckBallKick(ball_x, self.ids.ball.center_y) and self.ball_vel > 0:
            self.ids.ball.center_x += self.ball_vel
            self.StopOpponent()
            self.ids.ball.angle -= self.ball_vel
            self.ball_vel -= min(Window.width/150,Window.height/150)

            if self.ids.ball.center_x > Window.width*47/50:
                self.ball_status = "outside-right"
        else:
            Clock.unschedule(self.BallDeAccRight)
            if self.ball_status == "outside-right":
                mistake_sound.play()
                self.ids.response.text = "Ball went out of boundary. Click to bring it back."
                self.ids.player.source = "images/player-right-still.png"
                self.end_motion()
                self.HideControls()

    def ShootBall(self):
        Clock.unschedule(self.CalTimeBtDown)
        self.ball_vel = min(Window.width/10,Window.height/10)*self.ball_vel/30
        p = Vector(self.ids.player.center_x,self.ids.player.y)
        b = Vector(self.ids.ball.center)
        if p.distance(b) < min(Window.width/20, Window.height/20):
            if b[1] > p[1] and self.p_cur_mv == "up":
                shoot_sound.play()
                Clock.schedule_interval(self.BallDeAccUp, 1/30)
            elif b[1] < p[1] and self.p_cur_mv == "down":
                shoot_sound.play()
                Clock.schedule_interval(self.BallDeAccDown, 1/30)
            elif b[0] < p[0] and self.p_cur_mv == "left":
                shoot_sound.play()
                Clock.schedule_interval(self.BallDeAccLeft, 1/30)
            elif b[0] > p[0] and self.p_cur_mv == "right":
                shoot_sound.play()
                Clock.schedule_interval(self.BallDeAccRight, 1/30)
