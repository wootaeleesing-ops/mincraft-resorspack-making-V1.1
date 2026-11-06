import base64, io, json, os, re, zipfile, tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from PIL import Image, ImageTk, ImageDraw

APP = "Minecraft Resource Studio"
VERSIONS = {
    "1.21.4": 46, "1.21.3": 42, "1.21.2": 42, "1.21.1": 34,
    "1.21": 34, "1.20.6": 32, "1.20.5": 32, "1.20.4": 22,
    "1.20.2": 18, "1.20.1": 15, "1.20": 15, "1.19.4": 13,
    "1.19.3": 12, "1.19.2": 9, "1.19.1": 9, "1.19": 9,
    "1.18.2": 8, "1.18.1": 8, "1.18": 8, "1.17.1": 7,
    "1.17": 7, "1.16.5": 6, "1.16.2": 6, "1.16.1": 5,
    "1.15.2": 5, "1.14.4": 4, "1.13.2": 4, "1.12.2": 3,
    "1.11.2": 3, "1.10.2": 2, "1.9.4": 2, "1.8.9": 1
}
BG="#111713"; PANEL="#18221c"; PANEL2="#202d25"; BORDER="#2d3c31"
TEXT="#e3eadf"; MUTED="#93a38f"; GREEN="#c8f36a"; GREEN_D="#31452d"
CATS = [("전체 텍스처",""),("블록","block"),("아이템","item"),("엔티티","entity"),
        ("환경","environment"),("파티클","particle"),("GUI","gui"),("기타","other")]

class Studio:
    def __init__(self, root):
        self.root=root; root.title(APP+" V2.0"); root.geometry("1440x880"); root.minsize(1100,700); root.configure(bg=BG)
        self.assets={}; self.selected=None; self.photo=None; self.preview_photo=None
        self.pack_name=tk.StringVar(value="My Resource Pack"); self.description=tk.StringVar(value="Created with Resource Studio")
        self.version=tk.StringVar(value="1.21.4"); self.search=tk.StringVar(); self.category=tk.StringVar(value="")
        self.api_key=tk.StringVar(); self.prompt=tk.StringVar(); self.texture_name=tk.StringVar()
        self.dirty=False; self._build(); self._refresh_grid()
    def label(self,parent,text,**kw):
        return tk.Label(parent,text=text,bg=kw.pop("bg",parent.cget("bg")),fg=kw.pop("fg",TEXT),**kw)
    def button(self,parent,text,command,primary=False):
        return tk.Button(parent,text=text,command=command,bg=GREEN if primary else PANEL2,
            fg="#172015" if primary else TEXT,activebackground=GREEN,activeforeground="#172015",
            relief="flat",bd=0,padx=13,pady=8,cursor="hand2",font=("Segoe UI",9,"bold" if primary else "normal"))
    def _build(self):
        top=tk.Frame(self.root,bg="#0d130f",height=62); top.pack(fill="x"); top.pack_propagate(False)
        self.label(top,"▧  PRISM  /  RESOURCE STUDIO",bg="#0d130f",font=("Segoe UI",15,"bold")).pack(side="left",padx=22)
        self.label(top,"JAVA EDITION  •  LOCAL WORKSPACE",bg="#0d130f",fg=MUTED,font=("Consolas",8)).pack(side="left",padx=12)
        self.button(top,"📂 팩 불러오기",self.load_pack).pack(side="right",padx=(5,18),pady=12)
        self.button(top,"작업 백업",self.backup).pack(side="right",padx=5,pady=12)
        self.button(top,"Minecraft JAR 가져오기",self.load_jar).pack(side="right",padx=5,pady=12)
        shell=tk.Frame(self.root,bg=BG); shell.pack(fill="both",expand=True,padx=12,pady=12)
        self.sidebar=tk.Frame(shell,bg=PANEL,width=205); self.sidebar.pack(side="left",fill="y"); self.sidebar.pack_propagate(False)
        self.label(self.sidebar,"인스턴스 선택",fg=MUTED,font=("Segoe UI",9,"bold")).pack(anchor="w",padx=16,pady=(18,12))
        self.label(self.sidebar,"CURRENT WORKSPACE",fg=MUTED,font=("Consolas",8)).pack(anchor="w",padx=16)
        self.label(self.sidebar,"MAKER",font=("Segoe UI",16,"bold")).pack(anchor="w",padx=16,pady=(4,0))
        self.label(self.sidebar,"JAVA EDITION  •  V2.0",fg=GREEN,font=("Consolas",8)).pack(anchor="w",padx=16,pady=(4,18))
        self.button(self.sidebar,"▦  전체 리소스 메뉴",lambda:self.set_category(""),True).pack(fill="x",padx=12)
        self.label(self.sidebar,"라이브러리",fg=MUTED,font=("Segoe UI",9,"bold")).pack(anchor="w",padx=16,pady=(24,8))
        self.category_buttons=[]
        for title,key in CATS:
            b=tk.Button(self.sidebar,text=title,anchor="w",command=lambda k=key:self.set_category(k),
                bg=PANEL,fg=TEXT,activebackground=GREEN,activeforeground="#172015",relief="flat",bd=0,padx=16,pady=9)
            b.pack(fill="x",padx=8); self.category_buttons.append((b,key))
        self.label(self.sidebar,"팩 설정",fg=MUTED,font=("Segoe UI",9,"bold")).pack(anchor="w",padx=16,pady=(25,8))
        self.label(self.sidebar,"Minecraft 버전",fg=TEXT).pack(anchor="w",padx=16)
        ttk.Combobox(self.sidebar,textvariable=self.version,values=list(VERSIONS),state="readonly").pack(fill="x",padx=12,pady=6)
        self.label(self.sidebar,"팩 이름",fg=TEXT).pack(anchor="w",padx=16,pady=(8,0))
        tk.Entry(self.sidebar,textvariable=self.pack_name,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat").pack(fill="x",padx=12,pady=5,ipady=6)
        self.label(self.sidebar,"팩 설명",fg=TEXT).pack(anchor="w",padx=16,pady=(5,0))
        tk.Entry(self.sidebar,textvariable=self.description,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat").pack(fill="x",padx=12,pady=5,ipady=6)
        self.button(self.sidebar,"＋ PNG 텍스처 추가",self.import_png).pack(fill="x",padx=12,pady=(14,6))
        self.button(self.sidebar,"📦 리소스팩 내보내기",self.export_pack,True).pack(fill="x",padx=12,pady=4)
        center=tk.Frame(shell,bg=BG); center.pack(side="left",fill="both",expand=True,padx=12)
        head=tk.Frame(center,bg=BG); head.pack(fill="x",pady=(2,12))
        self.label(head,"RESOURCE LIBRARY",fg=MUTED,font=("Consolas",8)).pack(anchor="w")
        self.label(head,"리소스 작업실",font=("Segoe UI",22,"bold")).pack(side="left",anchor="w")
        self.button(head,"＋ 새 텍스처",self.new_texture).pack(side="right",padx=4)
        self.button(head,"팩 내보내기 ↗",self.export_pack,True).pack(side="right",padx=4)
        searchrow=tk.Frame(center,bg=BG); searchrow.pack(fill="x",pady=(0,10))
        ent=tk.Entry(searchrow,textvariable=self.search,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",font=("Segoe UI",11))
        ent.pack(fill="x",ipady=11); ent.insert(0,""); self.search.trace_add("write",lambda *_:self._refresh_grid())
        self.count=self.label(center,"텍스처 0개",fg=MUTED,font=("Segoe UI",9)); self.count.pack(anchor="e",pady=(0,5))
        gridwrap=tk.Frame(center,bg=BG); gridwrap.pack(fill="both",expand=True)
        self.canvas=tk.Canvas(gridwrap,bg=BG,highlightthickness=0)
        sb=ttk.Scrollbar(gridwrap,orient="vertical",command=self.canvas.yview)
        self.grid=tk.Frame(self.canvas,bg=BG)
        self.grid.bind("<Configure>",lambda e:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0,0),window=self.grid,anchor="nw")
        self.canvas.configure(yscrollcommand=sb.set); self.canvas.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y")
        self.canvas.bind_all("<MouseWheel>",lambda e:self.canvas.yview_scroll(int(-e.delta/120),"units"))
        self.inspector=tk.Frame(shell,bg=PANEL,width=260); self.inspector.pack(side="right",fill="y"); self.inspector.pack_propagate(False)
        self.label(self.inspector,"INSPECTOR",fg=MUTED,font=("Consolas",8)).pack(anchor="w",padx=16,pady=(18,14))
        self.preview=tk.Label(self.inspector,text="리소스를 선택해\n미리보기",bg="#101712",fg=MUTED,font=("Segoe UI",14),width=24,height=11)
        self.preview.pack(padx=14,fill="x")
        self.ins_name=self.label(self.inspector,"선택된 텍스처 없음",font=("Segoe UI",12,"bold"),wraplength=220)
        self.ins_name.pack(anchor="w",padx=16,pady=(15,5))
        self.ins_path=self.label(self.inspector,"라이브러리에서 항목을 선택하세요",fg=MUTED,wraplength=225,justify="left")
        self.ins_path.pack(anchor="w",padx=16)
        self.ins_size=self.label(self.inspector,"",fg=MUTED); self.ins_size.pack(anchor="w",padx=16,pady=8)
        self.button(self.inspector,"이미지 교체",self.replace_selected).pack(fill="x",padx=14,pady=(12,5))
        self.button(self.inspector,"픽셀 편집기 열기",self.edit_selected).pack(fill="x",padx=14,pady=5)
        self.button(self.inspector,"선택 항목 삭제",self.delete_selected).pack(fill="x",padx=14,pady=5)
        ai=tk.Frame(self.inspector,bg=PANEL2,padx=12,pady=12); ai.pack(fill="x",padx=10,pady=(22,10))
        self.label(ai,"✦ AI TEXTURE LAB",font=("Segoe UI",10,"bold")).pack(anchor="w")
        tk.Entry(ai,textvariable=self.api_key,show="•",bg="#101712",fg=TEXT,insertbackground=TEXT,relief="flat").pack(fill="x",pady=(10,5),ipady=7)
        self.label(ai,"Gemini API 키",fg=MUTED,font=("Segoe UI",8)).pack(anchor="w")
        tk.Entry(ai,textvariable=self.prompt,bg="#101712",fg=TEXT,insertbackground=TEXT,relief="flat").pack(fill="x",pady=7,ipady=7)
        self.button(ai,"AI 텍스처 생성",self.generate_ai,True).pack(fill="x")
        self.status=tk.StringVar(value="준비 완료 · Minecraft JAR 또는 리소스팩 ZIP을 불러오세요.")
        tk.Label(self.root,textvariable=self.status,bg="#0d130f",fg=MUTED,anchor="w",padx=16,pady=8).pack(fill="x")
    def set_category(self,key):
        self.category.set(key); self._refresh_grid()
    def _refresh_grid(self):
        if not hasattr(self,"grid"): return
        for w in self.grid.winfo_children(): w.destroy()
        q=self.search.get().strip().lower()
        items=[(k,v) for k,v in self.assets.items() if (not self.category.get() or self.category.get() in k.lower()) and (not q or q in k.lower())]
        self.count.configure(text=f"텍스처 {len(items):,}개")
        for i,(path,img) in enumerate(items):
            card=tk.Frame(self.grid,bg=PANEL2,highlightthickness=1,highlightbackground=BORDER)
            card.grid(row=i//4,column=i%4,padx=5,pady=5,sticky="nsew")
            thumb=img.copy(); thumb.thumbnail((78,78),Image.Resampling.NEAREST)
            tile=Image.new("RGBA",(96,96),"#26342b"); tile.alpha_composite(thumb,((96-thumb.width)//2,(96-thumb.height)//2))
            photo=ImageTk.PhotoImage(tile)
            b=tk.Button(card,image=photo,bg=PANEL2,activebackground=GREEN,relief="flat",bd=0,command=lambda p=path:self.select(p))
            b.image=photo; b.pack(padx=5,pady=(6,3))
            tk.Label(card,text=os.path.basename(path)[:22],bg=PANEL2,fg=TEXT,font=("Segoe UI",8),width=15).pack(padx=4,pady=(0,2))
            tk.Label(card,text=path[:26],bg=PANEL2,fg=MUTED,font=("Segoe UI",7),width=18).pack(padx=3,pady=(0,6))
        for c in range(4): self.grid.grid_columnconfigure(c,weight=1)
    def select(self,path):
        self.selected=path; img=self.assets[path]
        p=img.copy(); p.thumbnail((220,220),Image.Resampling.NEAREST)
        bg=Image.new("RGBA",(230,230),"#101712"); bg.alpha_composite(p,((230-p.width)//2,(230-p.height)//2))
        self.preview_photo=ImageTk.PhotoImage(bg); self.preview.configure(image=self.preview_photo,text="")
        self.ins_name.configure(text=os.path.basename(path)); self.ins_path.configure(text=path)
        self.ins_size.configure(text=f"{img.width} × {img.height} px  ·  RGBA")
        self.status.set("선택됨: "+path)
    def import_png(self):
        paths=filedialog.askopenfilenames(filetypes=[("PNG 이미지","*.png")])
        for path in paths:
            try:
                name=os.path.basename(path)
                key="assets/minecraft/textures/block/"+name
                self.assets[key]=Image.open(path).convert("RGBA")
                self.selected=key
            except Exception as e: messagebox.showerror("PNG 불러오기 실패",str(e))
        self._refresh_grid()
        if self.selected: self.select(self.selected)
        self.status.set(f"PNG {len(paths)}개를 가져왔습니다.")
    def load_jar(self):
        path=filedialog.askopenfilename(title="Minecraft 버전 JAR 선택",filetypes=[("Minecraft JAR","*.jar"),("ZIP","*.zip")])
        if not path:return
        n=0
        try:
            with zipfile.ZipFile(path) as z:
                for name in z.namelist():
                    if name.startswith("assets/minecraft/textures/") and name.lower().endswith(".png"):
                        try: self.assets[name]=Image.open(io.BytesIO(z.read(name))).convert("RGBA"); n+=1
                        except Exception: pass
            self._refresh_grid(); self.status.set(f"Minecraft 텍스처 {n:,}개를 불러왔습니다.")
            messagebox.showinfo("불러오기 완료",f"{n:,}개 텍스처를 라이브러리에 추가했습니다.")
        except Exception as e: messagebox.showerror("JAR 불러오기 실패",str(e))
    def load_pack(self):
        path=filedialog.askopenfilename(filetypes=[("Resource pack / ZIP","*.zip")])
        if not path:return
        n=0
        try:
            with zipfile.ZipFile(path) as z:
                for name in z.namelist():
                    if name.startswith("assets/") and name.lower().endswith(".png"):
                        try:
                            self.assets[name]=Image.open(io.BytesIO(z.read(name))).convert("RGBA")
                            n+=1
                        except Exception:
                            pass
                if "pack.mcmeta" in z.namelist():
                    meta=json.loads(z.read("pack.mcmeta").decode("utf-8")); self.description.set(meta.get("pack",{}).get("description",""))
            self._refresh_grid(); self.status.set(f"리소스팩에서 {n:,}개 텍스처를 불러왔습니다.")
        except Exception as e:messagebox.showerror("팩 불러오기 실패",str(e))
    def new_texture(self):
        name=tk.simpledialog.askstring("새 텍스처","파일 이름을 입력하세요:",initialvalue="new_texture")
        if not name:return
        name=re.sub(r"[^a-zA-Z0-9_.-]","_",name)
        key=f"assets/minecraft/textures/block/{name}.png"
        self.assets[key]=Image.new("RGBA",(16,16),(100,130,100,255)); self._refresh_grid(); self.select(key)
    def replace_selected(self):
        if not self.selected:return messagebox.showinfo("안내","먼저 텍스처를 선택하세요.")
        path=filedialog.askopenfilename(filetypes=[("PNG 이미지","*.png")])
        if path:
            self.assets[self.selected]=Image.open(path).convert("RGBA"); self.select(self.selected); self._refresh_grid()
    def delete_selected(self):
        if self.selected and messagebox.askyesno("삭제 확인","선택한 텍스처를 작업 공간에서 삭제할까요?"):
            del self.assets[self.selected]; self.selected=None; self.preview.configure(image="",text="리소스를 선택해 미리보기")
            self.ins_name.configure(text="선택된 텍스처 없음"); self.ins_path.configure(text=""); self.ins_size.configure(text=""); self._refresh_grid()
    def edit_selected(self):
        if not self.selected:return messagebox.showinfo("안내","먼저 텍스처를 선택하세요.")
        img=self.assets[self.selected]; win=tk.Toplevel(self.root); win.title("픽셀 편집기"); win.configure(bg=BG)
        scale=max(12,min(28,560//max(img.size))); canvas=tk.Canvas(win,width=img.width*scale,height=img.height*scale,bg="#101712",highlightthickness=0)
        canvas.pack(padx=12,pady=12); color=["#7fbf5b"]
        def redraw():
            canvas.delete("all")
            for y in range(img.height):
                for x in range(img.width):
                    rgba=img.getpixel((x,y)); hx="#%02x%02x%02x"%rgba[:3]
                    canvas.create_rectangle(x*scale,y*scale,(x+1)*scale,(y+1)*scale,fill=hx,outline="#344238")
        def paint(e):
            x,y=e.x//scale,e.y//scale
            if 0<=x<img.width and 0<=y<img.height:
                rgb=tuple(bytes.fromhex(color[0].lstrip("#")))+(255,)
                img.putpixel((x,y),rgb); redraw()
        canvas.bind("<Button-1>",paint); canvas.bind("<B1-Motion>",paint)
        row=tk.Frame(win,bg=BG); row.pack(fill="x",padx=12,pady=(0,12))
        tk.Button(row,text="색상 선택",command=lambda: self._choose_color(color)).pack(side="left")
        tk.Button(row,text="완료",command=lambda:(self._refresh_grid(),self.select(self.selected),win.destroy())).pack(side="right")
        redraw()
    def _choose_color(self,color):
        c=colorchooser.askcolor()[1]
        if c:color[0]=c
    def backup(self):
        path=filedialog.asksaveasfilename(defaultextension=".zip",initialfile="ResourceStudio_Backup.zip",filetypes=[("ZIP","*.zip")])
        if not path:return
        try:
            with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
                for key,img in self.assets.items():
                    b=io.BytesIO(); img.save(b,format="PNG"); z.writestr(key,b.getvalue())
                z.writestr("studio-backup.json",json.dumps({"pack_name":self.pack_name.get(),"description":self.description.get(),"version":self.version.get()},ensure_ascii=False))
            self.status.set("작업 백업 완료: "+path)
        except Exception as e:messagebox.showerror("백업 실패",str(e))
    def export_pack(self):
        if not self.assets:return messagebox.showinfo("내보내기","먼저 Minecraft JAR, 리소스팩 ZIP 또는 PNG 텍스처를 불러오세요.")
        path=filedialog.asksaveasfilename(defaultextension=".zip",initialfile="MyResourcePack.zip",filetypes=[("ZIP","*.zip")])
        if not path:return
        try:
            fmt=VERSIONS.get(self.version.get(),46)
            meta={"pack":{"pack_format":fmt,"description":self.description.get() or self.pack_name.get()}}
            with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
                z.writestr("pack.mcmeta",json.dumps(meta,ensure_ascii=False,indent=2))
                for key,img in self.assets.items():
                    b=io.BytesIO(); img.save(b,format="PNG"); z.writestr(key,b.getvalue())
            messagebox.showinfo("내보내기 완료",f"리소스팩 ZIP을 저장했습니다.\n\n{path}\n\n.minecraft/resourcepacks 폴더에 넣으세요.")
            self.status.set("팩 내보내기 완료: "+path)
        except Exception as e:messagebox.showerror("내보내기 실패",str(e))
    def generate_ai(self):
        key=self.api_key.get().strip(); prompt=self.prompt.get().strip()
        if not key or not prompt:return messagebox.showinfo("AI 텍스처","Gemini API 키와 텍스처 설명을 입력하세요.")
        self.status.set("Gemini 이미지 생성 요청 중..."); self.root.update_idletasks()
        try:
            model="gemini-2.0-flash-preview-image-generation"
            url=f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            body={"contents":[{"parts":[{"text":"Create a square seamless Minecraft pixel-art texture. No text. Request: "+prompt}]}],
                  "generationConfig":{"responseModalities":["TEXT","IMAGE"]}}
            req=Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
            with urlopen(req,timeout=120) as r:data=json.loads(r.read())
            parts=data["candidates"][0]["content"]["parts"]
            encoded=next(p.get("inlineData",{}).get("data") for p in parts if p.get("inlineData"))
            img=Image.open(io.BytesIO(base64.b64decode(encoded))).convert("RGBA")
            name=re.sub(r"[^a-zA-Z0-9_.-]","_",prompt[:24].strip()) or "ai_texture"
            path=f"assets/minecraft/textures/block/{name}.png"; self.assets[path]=img; self._refresh_grid(); self.select(path)
            self.status.set("AI 텍스처 생성 완료")
        except HTTPError as e:
            messagebox.showerror("Gemini API 오류",e.read().decode("utf-8","replace")[:900]); self.status.set("AI 생성 실패")
        except Exception as e:messagebox.showerror("AI 생성 실패",str(e)); self.status.set("AI 생성 실패")

if __name__=="__main__":
    import tkinter.simpledialog
    root=tk.Tk(); app=Studio(root); root.mainloop()
