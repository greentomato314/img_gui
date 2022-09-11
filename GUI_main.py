'''
https://teratail.com/questions/253714?sort=3
ここからスタート
'''
import os
import tkinter.filedialog
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
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
        self.mode = 0
        self.points = [] #10000*10000で表現。
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
        for pls in self.points:
            for a,b in pls:
                a1,b1 = a*self.scale//100,b*self.scale//100
                ImageDraw.Draw(self.img).ellipse((a1-5, b1-5, a1+5, b1+5), fill=(255, 0, 0), outline=(255, 0, 0))
            if len(pls) < 2:
                continue
            for j in range(len(pls)-1):
                a1,b1 = pls[j]
                a2,b2 = pls[j+1]
                a1,b1 = a1*self.scale//100,b1*self.scale//100
                a2,b2 = a2*self.scale//100,b2*self.scale//100
                ImageDraw.Draw(self.img).line((a1, b1, a2, b2), fill=(255, 0, 0), width=3)

        # 描画更新
        self.image = image = ImageTk.PhotoImage(self.img)
        self.imageId = canvas.create_image(x, y, image=image,anchor="nw")

        if self.text:
            canvas.delete(self.text)
        a,b = self.mode_display()
        self.text = self.canvas.create_text((self.canvas.winfo_width()//2,self.canvas.winfo_height()-20),font=("",15),text=a,anchor='center',fill=b)

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
        if self.mode == 0:
            canvas = self.canvas
            canvas.update_idletasks()
            centerw,centerh = canvas.winfo_width()//2,canvas.winfo_height()//2
            x,y = self.pos
            self.pos = (x-(event.x-centerw),y-(event.y-centerh))
        if self.mode == 1:
            canvas = self.canvas
            x,y = self.pos
            xc,yc = event.x-x,event.y-y
            xp,yp = xc*100/self.scale,yc*100/self.scale
            self.points[-1].append((xp,yp))
        self.update()

    def click_right(self, event):
        self.change_mode()
    
    def change_mode(self):
        self.mode = self.mode^1
        if self.mode == 1:
            self.points.append([])
        self.update()
    
    def zoomIn(self):
        scale = self.scale+0.1
        self.setScale(scale)

    def zoomOut(self):
        scale = self.scale-0.1
        self.setScale(scale)
    
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
    
    def mode_display(self):
        if self.mode == 0:
            return "移動モード","#00aaee"
        if self.mode == 1:
            return "測定モード","#fa00ff"
    
    def backd(self):
        if self.points:
            if self.points[-1]:
                self.points[-1].pop()
            else:
                self.points.pop()
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
        self.menu_file.add_command(label='csv出力', command=self.output_csv)
        self.menu_file.add_command(label='画像出力', command=self.output_img)
        self.operate = tk.Menu(self.root)
        self.img = Image.new('RGB', (500, 300), (128, 128, 128))
        self.create_image()
        self.men.add_cascade(label='操作', menu=self.operate)
        self.operate.add_command(label='スケール設定', command=self.open_file)
        self.operate.add_command(label='モードの切り替え', command=self.image.change_mode)
        #self.operate.add_command(label='途中結果出力', command=self.image.change_mode)
        self.operate.add_command(label='戻る', command=self.image.backd)
        # 拡大縮小、移動
        self.place_command()
        self.image.update()
    
    def create_image(self):
        w,h = self.img.size
        self.root.geometry("{:}x{:}".format(w,h+200))
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
    
    def place_command(self):
        ttk.Button(self.frame, text="+", command=self.image.zoomIn).pack(fill=tk.BOTH, expand=0)
        ttk.Button(self.frame, text="-", command=self.image.zoomOut).pack(fill=tk.BOTH, expand=0)
        ttk.Button(self.frame, text="change_mode", command=self.image.change_mode).pack(fill=tk.BOTH, expand=0)
        ttk.Button(self.frame, text="↑", command=self.image.move_top).pack(side=tk.TOP)
        ttk.Button(self.frame, text="↓", command=self.image.move_bottom).pack(side=tk.BOTTOM)
        ttk.Button(self.frame, text="←", command=self.image.move_left).pack(side=tk.LEFT)
        ttk.Button(self.frame, text="→", command=self.image.move_right).pack(side=tk.RIGHT)
        self.image.canvas.bind('<ButtonPress-1>',self.image.click_left)
        self.image.canvas.bind('<ButtonPress-3>',self.image.click_right)
    
    def output_csv(self):
        filename = tk.filedialog.asksaveasfilename(
            title = "名前を付けて保存",
            filetypes = [("CSV", ".csv")], # ファイルフィルタ
            initialdir = iDir, # 自分自身のディレクトリ
            defaultextension = "csv"
            )
        lens = []
        for pls in self.image.points:
            l = 0
            if len(pls) < 2:
                lens.append(l)
                continue
            for j in range(len(pls)-1):
                a1,b1 = pls[j]
                a2,b2 = pls[j+1]
                l += ((a1-a2)**2+(b1-b2)**2)**(1/2)
            lens.append([l])
        with open(filename, 'w',newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["length"])
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