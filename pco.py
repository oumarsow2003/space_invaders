import tkinter as tk
class Alien(object):
    def __init__(self):
        self.id = None
        self.alive = True
        self.speed=20
        self.width=50
        self.img=tk.PhotoImage(file='alien.gif')
    def touched_by(self, canvas,projectile):
        x1, y1, x2, y2 = canvas.bbox(self.id)
        overlapped = canvas.find_overlapping(x1, y1, x2, y2)
        #Si il croise un autre élément
        if len(overlapped)==2:
            #Supression du projectile et de l'alien
            projectile.shooter.fired_bullets.remove(projectile)
            canvas.delete(projectile.id)
            self.alive=False
            #fleet.aliens_fleet.remove(self)
            #canvas.delete(self.id)
   
    def install_in(self, canvas, x, y):
        self.canvas=canvas
        self.id=canvas.create_image(x,y,image=self.img,tags="image") 
    #x1 et x2 corespondent aux abcisses des aliens aux extrémités
    def move_in(self,x2,x3):
        max_w = int(self.canvas.cget("width"))
        self.dy=0
        if x2 > max_w:
            self.speed= -self.speed
            self.dy=10
        elif x3 < 0:
            self.speed = -self.speed
            self.dy=10
        self.canvas.move(self.id, self.speed,self.dy)


class Fleet(object):
    def __init__(self):
        self.aliens_lines = 5
        self.aliens_columns = 10
        self.aliens_inner_gap = 20
        self.alien_x_delta = 5
        self.alien_y_delta = 15
        self.explosion=tk.PhotoImage(file='explosion.gif')
        self.fleet_size =self.aliens_lines * self.aliens_columns
        self.aliens_fleet= [None] * self.fleet_size
        self.x=100
        self.y=100
        self.dx=20
        self.isBottom=False
        for i in range(0,self.fleet_size):
            self.aliens_fleet[i]=Alien()
    def get_width(self):
        return self.aliens_fleet[0].width*(self.aliens_columns+6)+(self.aliens_inner_gap*(self.aliens_columns-1))
    def install_in(self, canvas):
        self.canvas=canvas
        for i in range(0,self.fleet_size):
            self.aliens_fleet[i].install_in(canvas,self.x+75*(i%10),self.y+75*(i//10))  
    def move_in(self):
        max_h = int(self.canvas.cget("height"))
        x1, y1, x2, y2 = self.canvas.bbox("image")
        if y1<max_h:
            for i in self.aliens_fleet:
                i.move_in(x2,x1)
        else:
            self.isBottom=True
    def manage_touched_aliens_by(self,canvas,defender):
        for alien in self.aliens_fleet:
            for bullet in defender.fired_bullets:
                alien.touched_by(canvas,bullet)
            if alien.alive==False:
                x, y,x1, y1 = self.canvas.bbox(alien.id)
                explosion_image=canvas.create_image(x,y,image=self.explosion,tags="images")
                canvas.after(70,canvas.delete,explosion_image)
                self.aliens_fleet.remove(alien)
                canvas.delete(alien.id)
            if len(self.aliens_fleet)==0:
                break
        
class Defender(object):
    def __init__(self,canvas):
        self.id=None
        self.canvas=canvas
        self.width = 20
        self.height = 20
        self.speed= 20
        self.max_fired_bullets = 8
        self.fired_bullets = []
        self.x=Fleet().get_width()
        self.y=700
    def install_in(self):
        self.id = self.canvas.create_rectangle(self.x//2-self.width//2,self.y-self.height,self.x//2-self.width//2+20,self.y-self.height+20,fill="white")
    def fire(self, canvas):
        #nombre de tire ne doit pas etre superieur à 8
        if(len(self.fired_bullets)<=self.max_fired_bullets-1):
            bullet=Bullet(self)
            #ajout de la balle dans fird_bullets
            self.fired_bullets.append(bullet)
            bullet.install_in(canvas)
        
class Bullet(object):
    def __init__(self, shooter):
        self.radius = 5
        self.color = "red"
        self.speed = 8
        self.id = None
        self.shooter = shooter
        self.compt=0
    def install_in(self, canvas):
        x,y,x2,y2=canvas.bbox(self.shooter.id)
        self.id=canvas.create_oval(x+(x2-x)//2-self.radius,y-self.radius,x+(x2-x)//2+self.radius,y+self.radius,fill="red")
    def move_in(self,canvas):
        #On compte le nomdre de mouvements du bullet;32:nombre de mouvements pour atteindre le haut
        if(self.compt<32):
            self.compt+=1
            canvas.move(self.id,0,-25)
class Game(object):
    def __init__(self, frame):
        self
        self.frame = frame
        self.fleet = Fleet()
        self.height =700
        self.width = self.fleet.get_width()
        self.isWon=None
        self.canvas = tk.Canvas(self.frame,width=self.width,height=self.height,bg="black")
        self.canvas.pack()
    def start(self):
        self.fleet=Fleet()
        self.defender = Defender(self.canvas)
        self.defender.install_in()
        self.fleet.install_in(self.canvas)
        self.frame.winfo_toplevel().bind("<Key>", self.keypress)
    def animation(self):
        if(self.isWon!=True):
            self.fleet.move_in()
        self.fleet.manage_touched_aliens_by(self.canvas,self.defender)
        self.move_bullets()
        self.checkStatus()
        if self.isWon==None:
            self.canvas.after(150,self.animation)
    def start_animation(self):
        self.canvas.delete("all")
        self.start()
        self.animation()
    #mouvement du defender et tire des balles
    def keypress(self,event):
        x,y,x2,y2=self.canvas.bbox(self.defender.id)
        if event.keysym=="Left":
            if x2>self.defender.width:
                self.canvas.move(self.defender.id,-20,0)
        elif event.keysym=="Right":
            if x2<self.width-self.defender.width:
                self.canvas.move(self.defender.id,20,0)
        else:
            self.defender.fire(self.canvas)   
        
    #deplacement des bullets
    def move_bullets(self):
        for i in self.defender.fired_bullets:
            i.move_in(self.canvas)
            #pour chaque bullets,on verifie son nombre de mouvement, si il atteint 32, alors il est supprimé
            if i.compt>=32:
                self.defender.fired_bullets.remove(i)
                self.canvas.delete(i.id)
    def checkStatus(self):
        if len(self.fleet.aliens_fleet)==0:
            self.isWon=True
        elif self.fleet.isBottom==True:
            self.isWon=False
        if self.isWon==False:
            self.frame.destroy()
        elif self.isWon==True:
            self.frame.destroy()
    def menu(self):
        self.max_w = int(self.canvas.cget("width"))
        texte="Space Invaders 2.0"
        label=tk.Label(self.canvas, text=texte, font=("Impact", 50), fg='green', bg='black')
        self.canvas.create_window(self.max_w//2,130,window=label)
        txt_ng="New game"
        label=tk.Button(self.canvas, text=txt_ng, font=("Impact", 30), fg='green', bg='black',borderwidth="0",command=self.start_animation)
        self.canvas.create_window(self.max_w//2,300,window=label)
        txt_hs="Highscores"
        label=tk.Button(self.canvas, text=txt_hs, font=("Impact", 30), fg='green', bg='black',borderwidth="0")
        self.canvas.create_window(self.max_w//2,400,window=label)
        txt_quit="Quit"
        label=tk.Button(self.canvas, text=txt_quit, font=("Impact", 30), fg='green', bg='black',borderwidth="0")
        self.canvas.create_window(self.max_w//2,500,window=label)

    def new_game(self):
        self.canvas.delete("all")
        self.Champ = Entry(self.canvas)
        self.canvas.create_window(self.max_w/2,450,window=self.Champ)
        
class SpaceInvaders(object):
    """
     Main Game class
    """
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Invaders")
        self.frame = tk.Frame(self.root)
        self.frame.pack(side="top", fill="both")
        self.game = Game(self.frame)

    def play(self):
        self.game.menu()
        self.root.mainloop()
    

SpaceInvaders().play()