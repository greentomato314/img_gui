'''
https://teratail.com/questions/253714?sort=3
ここからスタート
'''
import os
import tkinter.filedialog
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
from math import floor
import csv

iDir = os.path.abspath(os.path.dirname(__file__))
class PILImage:
    def __init__(self, pilimg, canvas, pos):
        self.pos = pos
        self.canvas = canvas
        self.src_image = pilimg
        self.image = None
        self.imageId = None
        self.text = None
        self.scale = 1.0
        self.mouse = (0,0)
        self.points = [[]] #10000*10000で表現。
        self.fontsize = 14
        self.texton = True
        self.color = (255, 0, 0)
        self.W,self.H = self.src_image.size
        self.scalebar = 1
        self.update()

    def update(self):
        # ローカル変数宣言 (self.が大量にあり読みにくい場合)
        imageId = self.imageId
        src_image = self.src_image
        canvas = self.canvas
        scale = self.scale
        x, y = self.pos
        w, h = self.src_image.size 
        canvas.update_idletasks()

        # 以前の画像を消去
        if imageId:
            canvas.delete(imageId)

        # スケール変更後のサイズを計算
        w2, h2 = floor(w*scale), floor(h*scale)
        # リサイズ
        self.img = src_image.resize((w2, h2))
        for i,pls in enumerate(self.points):
            for a,b in pls:
                a1,b1 = a*self.scale//100,b*self.scale//100
                ImageDraw.Draw(self.img).ellipse((a1-5, b1-5, a1+5, b1+5), fill=self.color, outline=self.color)
            if len(pls) == 0:
                continue
            else:
                if self.texton:
                    ImageDraw.Draw(self.img).text((a1,b1), "({:})".format(i+1), fill=self.color,font=ImageFont.truetype("arial.ttf", size=self.fontsize))
                if len(pls) == 1:
                    continue
            for j in range(len(pls)-1):
                a1,b1 = pls[j]
                a2,b2 = pls[j+1]
                a1,b1 = a1*self.scale//100,b1*self.scale//100
                a2,b2 = a2*self.scale//100,b2*self.scale//100
                ImageDraw.Draw(self.img).line((a1, b1, a2, b2), fill=self.color, width=3)

        # 描画更新
        self.image = image = ImageTk.PhotoImage(self.img)
        self.imageId = canvas.create_image(x, y, image=image,anchor="nw")

    def setScale(self, scale):
        bescale = self.scale
        self.scale = scale
        canvas = self.canvas
        canvas.update_idletasks()
        centerw,centerh = canvas.winfo_width()//2,canvas.winfo_height()//2
        x,y = self.pos
        self.pos = (floor((x-centerw)*(scale/bescale)+centerw),floor((y-centerh)*(scale/bescale)+centerh))
        self.update()
    
    def click_left(self, event):
        self.mouse = event.x,event.y

    def click_right(self, event):
        canvas = self.canvas
        x,y = self.pos
        xc,yc = event.x-x,event.y-y
        xp,yp = xc*100/self.scale,yc*100/self.scale
        self.points[-1].append((xp,yp))
        self.update()
    
    def confirm(self):
        self.points.append([])
    
    def zoomIn(self):
        scale = self.scale+0.1
        self.setScale(scale)

    def zoomOut(self):
        scale = self.scale-0.1
        self.setScale(scale)
    
    def zoomInOut(self,event):
        scale = self.scale + event.delta*0.0005
        self.setScale(scale)
    
    def drag(self,event):
        bx,by = self.pos
        x = event.x
        y = event.y
        # 前回からのマウスの移動量の分だけ図形も移動
        self.pos = bx+x-self.mouse[0],by+y-self.mouse[1]
        self.mouse = (x,y)
        self.update()
    
    def move_top(self):
        x,y = self.pos
        self.pos = x,y+self.H//100
        self.update()
    
    def move_bottom(self):
        x,y = self.pos
        self.pos = x,y-self.H//100
        self.update()

    def move_left(self):
        x,y = self.pos
        self.pos = x+self.W//100,y
        self.update()
        
    def move_right(self):
        x,y = self.pos
        self.pos = x-self.H//100,y
        self.update()

class mainFrame():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("画像解析アプリケーション presented by Ijiro")
        self.men = tk.Menu(self.root)
        self.root.config(menu=self.men)
        self.menu_file = tk.Menu(self.root) 
        self.men.add_cascade(label='ファイル', menu=self.menu_file) 
        self.menu_file.add_command(label='開く', command=self.open_file)
        self.menu_file.add_command(label='途中結果確認', command=self.showtable)
        self.menu_file.add_command(label='csv出力', command=self.output_csv)
        self.menu_file.add_command(label='画像出力', command=self.output_img)
        self.operate = tk.Menu(self.root)
        self.img = Image.new('RGB', (500, 300), (128, 128, 128))
        self.create_image()
        self.men.add_cascade(label='操作', menu=self.operate)
        self.operate.add_command(label='スケール設定', command=self.scalebar)
        self.operate.add_command(label='文字設定', command=self.moji)
        self.operate.add_command(label='戻る(b)', command=self.backd)
        self.define_C()
        self.place_command()
        self.image.update()
    
    def define_C(self):
        self.tanni = 'None'
        self.scalenumber = 1.0

    def backd(self):
        if self.image.points:
            if self.image.points[-1]:
                self.image.points[-1].pop()
            else:
                self.image.points.pop()
        self.image.update()
    
    def moji(self):
        dlg_modeless = tk.Toplevel(self.frame)
        dlg_modeless.title("Modeless Dialog")   # ウィンドウタイトル
        dlg_modeless.geometry("200x100")        # ウィンドウサイズ(幅x高さ)
        tk.Label(dlg_modeless,text='文字').place(x=10, y=5)
        txt1 = ttk.Combobox(dlg_modeless,values=['ON','OFF'],width=7)
        txt1.place(x=50, y=5)
        tk.Label(dlg_modeless,text='サイズ').place(x=10, y=35)
        txt2 = tk.Entry(dlg_modeless,width=7)
        txt2.insert(tk.END, str(self.image.fontsize))
        txt2.place(x=50, y=35)
        tk.Label(dlg_modeless,text='色').place(x=10, y=65)
        txt3 = tk.Entry(dlg_modeless,width=11)
        txt3.insert(tk.END, str(self.image.color)[1:-1])
        txt3.place(x=50, y=65)
        def mojiSET():
            F1 = txt1.get()
            if F1 == 'ON':
                self.image.texton = True
            elif F1 == 'OFF':
                self.image.texton = False
            F2 = txt2.get()
            self.image.fontsize = int(F2)
            self.image.color = tuple(map(int,txt3.get().split(',')))
            self.image.update()
            dlg_modeless.destroy()
        ttk.Button(dlg_modeless, text="OK", command=mojiSET).place(x=120, y=65)
    
    def scalebar(self):
        dlg_modeless = tk.Toplevel(self.frame)
        dlg_modeless.title("Modeless Dialog")   # ウィンドウタイトル
        dlg_modeless.geometry("200x100")        # ウィンドウサイズ(幅x高さ)
        tk.Label(dlg_modeless,text='線番号').place(x=10, y=5)
        vals = []
        for i,pls in enumerate(self.image.points):
            if self.calclen(pls) != 0:
                vals.append(str(i+1))
        txt1 = ttk.Combobox(dlg_modeless,values=vals,width=7)
        txt1.place(x=10, y=25)
        tk.Label(dlg_modeless,text='長さ').place(x=10, y=45)
        txt2 = tk.Entry(dlg_modeless,width=7)
        txt2.insert(tk.END, '100')
        txt2.place(x=10, y=65)
        tk.Label(dlg_modeless,text='単位').place(x=70, y=45)
        txt3 = tk.Entry(dlg_modeless,width=7)
        txt3.insert(tk.END, 'nm')
        txt3.place(x=70, y=65)
        def scaleSET():
            ind = int(txt1.get())-1
            ll = self.calclen(self.image.points[ind])
            self.scalenumber = float(txt2.get())/ll
            self.tanni = txt3.get()
            dlg_modeless.destroy()
        ttk.Button(dlg_modeless, text="OK", command=scaleSET).place(x=120, y=65)
    
    def create_image(self):
        w,h = self.img.size
        self.root.geometry("{:}x{:}".format(w,h+150))
        self.root.update_idletasks()
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=1)
        self.canvas = tk.Canvas(self.frame)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.image = PILImage(self.img, self.canvas, pos=(0, 0))
        self.image.update()
    
    def open_file(self):
        fpath = tk.filedialog.askopenfilename(initialdir=iDir)
        self.img = Image.open(fpath)
        self.frame.destroy()
        self.create_image()
        self.place_command()
        self.image.update()
    
    def showtable(self):
        dlg_modeless = tk.Toplevel(self.frame)
        tree = ttk.Treeview(dlg_modeless, columns=('index',"length",self.tanni))
        tree.column('#0',width=0, stretch='no')
        tree.column('index', anchor='center', width=80)
        tree.column("length",anchor='center', width=100)
        tree.column(self.tanni, anchor='center', width=100)
        tree.heading('#0',text='')
        tree.heading('index', text='index',anchor='center')
        tree.heading("length", text="length", anchor='center')
        tree.heading(self.tanni,text=self.tanni, anchor='center')
        for i,pls in enumerate(self.image.points):
            ll = self.calclen(pls)
            tree.insert(parent='', index='end', iid=i ,values=(i+1,ll ,ll*self.scalenumber))
        tree.pack(pady=10)
    
    def key_handler(self,event):
        key = event.keysym
        if key == 'b':self.backd()
        elif key == 'c':self.image.confirm()
        elif key == 'Up':self.image.move_top()
        elif key == 'Down':self.image.move_bottom()
        elif key == 'Left':self.image.move_left()
        elif key == 'Right':self.image.move_right()

    def place_command(self):
        ttk.Button(self.frame, text="確定(c)", command=self.image.confirm).pack(fill=tk.BOTH, expand=0)
        ttk.Button(self.frame, text="+", command=self.image.zoomIn).pack(fill=tk.BOTH, expand=0)
        ttk.Button(self.frame, text="-", command=self.image.zoomOut).pack(fill=tk.BOTH, expand=0)
        ttk.Button(self.frame, text="↑", command=self.image.move_top).pack(side=tk.TOP)
        ttk.Button(self.frame, text="↓", command=self.image.move_bottom).pack(side=tk.BOTTOM)
        ttk.Button(self.frame, text="←", command=self.image.move_left).pack(side=tk.LEFT)
        ttk.Button(self.frame, text="→", command=self.image.move_right).pack(side=tk.RIGHT)
        self.root.bind("<KeyPress>",self.key_handler)
        self.image.canvas.bind('<ButtonPress-1>',self.image.click_left)
        self.image.canvas.bind('<ButtonPress-3>',self.image.click_right)
        self.image.canvas.bind("<MouseWheel>", self.image.zoomInOut)
        self.image.canvas.bind("<Button1-Motion>", self.image.drag)
    
    def calclen(self,pls):
        l = 0
        if len(pls) < 2:
            return 0
        for j in range(len(pls)-1):
            a1,b1 = pls[j]
            a2,b2 = pls[j+1]
            l += ((a1-a2)**2+(b1-b2)**2)**(1/2)
        return l
    
    def output_csv(self):
        filename = tk.filedialog.asksaveasfilename(
            title = "名前を付けて保存",
            filetypes = [("CSV", ".csv")], # ファイルフィルタ
            initialdir = iDir, # 自分自身のディレクトリ
            defaultextension = "csv"
            )
        lens = []
        for i,pls in enumerate(self.image.points):
            ll = self.calclen(pls)
            lens.append([i+1,ll,ll*self.scalenumber])
        with open(filename, 'w',newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["index","length",self.tanni])
            writer.writerows(lens)
    
    def output_img(self):
        filename = tk.filedialog.asksaveasfilename(
            title = "名前を付けて保存",
            filetypes = [("JPG", ".jpg")], # ファイルフィルタ
            initialdir = iDir, # 自分自身のディレクトリ
            defaultextension = "jpg"
            )
        self.image.img.save(filename)


def main():
    MF = mainFrame()
    MF.root.mainloop()

if __name__ == '__main__':
    main()