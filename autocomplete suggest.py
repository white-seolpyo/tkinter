import tkinter as tk


class AutocompleteEntry(tk.Entry):
    def __init__(self, master: tk.Tk, list_text: list[str], value='', *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.list_text = list_text
        self.list_text_match = []

        self.var = tk.StringVar(value=value)
        self.var.trace_add('write', lambda *x: self.on_change(x))
        self.configure(textvariable=self.var)

        self.top = tk.Toplevel(master)
        self.top.wm_withdraw()
        self.top.overrideredirect(True)

        self.bind_master()
        self.bind('<KeyRelease>', lambda x: self.on_keyrelease(x))
        self.bind('<FocusOut>', lambda x: self.on_focus_out(x))

        listboxkwargs = {}
        for i in ('justify', 'font', 'background', 'foreground'):
            if kwargs.get(i): listboxkwargs[i] = kwargs[i]
        self.listbox = tk.Listbox(self.top, **listboxkwargs)

        self.listbox.pack()
        self.listbox.bind('<<ListboxSelect>>', lambda x: self.on_select(x))
        return

    def bind_master(self):
        master = self.winfo_toplevel()
        master.bind('<Configure>', lambda x: self.master_configured(x))
        master.bind_all("<Button-1>", lambda x: self.on_focus_out(x))
        return

    def on_focus_out(self, _):
        self.top.wm_withdraw()
        return

    def set_listbox(self, text: str):
        self.list_text_match = [i for i in self.list_text if text.lower() in i.lower()]
        if self.list_text_match:
            for i in self.list_text_match: self.listbox.insert('end', i)
        return self.list_text_match

    def on_change(self, *_):
        text = self.var.get()
        if not text:
            self.top.wm_withdraw()
            return

        self.listbox.delete(0, 'end')
        matching_text = self.set_listbox(text)
        if not matching_text: self.top.wm_withdraw()
        else:
            self.update_listbox_position()
            self.top.wm_deiconify()
            self.top.tkraise()
        return

    def on_keyrelease(self, e: tk.Event):
        match e.keysym:
            case 'Escape': self.top.wm_withdraw()
            case 'Return':
                cur = self.listbox.curselection()
                if cur:
                    self.var.set(self.listbox.get(cur[0]))
                    self.top.wm_withdraw()
                    self.icursor('end')
            case 'Down':
                if self.top.wm_state():
                    self.top.wm_deiconify()
                    self.top.tkraise()

                cur = self.listbox.curselection()
                self.listbox.select_clear(0, 'end')
                if not cur: index = 0
                else:
                    index = cur[0] + 1
                    try: self.list_text_match[index]
                    except: index = 0
                self.listbox.selection_set(index)
            case 'Up':
                cur = self.listbox.curselection()
                self.listbox.select_clear(0, 'end')
                if not cur: index = self.list_text_match.__len__() - 1
                else:
                    index = cur[0] - 1
                    if index < 0: index = self.list_text_match.__len__() - 1
                    else:
                        try: self.list_text_match[index]
                        except: index = self.list_text_match.__len__() - 1
                self.listbox.selection_set(index)
        return

    def on_select(self, _):
        selection = self.listbox.get(self.listbox.curselection())
        self.var.set(selection)
        self.top.wm_withdraw()
        self.focus_set()
        return

    def master_configured(self, _):
        self.update_listbox_position()
        return

    def update_listbox_position(self):
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        width = self.winfo_width()

        # 각 항목의 실제 높이 계산
        if 0 < self.listbox.size(): item_height = self.listbox.bbox(0)[3]
        # 첫 번째 항목의 높이
        else: item_height = 20 # 기본 높이 설정

        self.top.wm_geometry(f"{width}x{self.listbox.size()*item_height+item_height}+{x}+{y}")

        if self.top.wm_state() == 'withdrawn': return
        self.top.wm_deiconify()
        self.top.tkraise()
        return


root = tk.Tk()
root.title("Autocomplete Entry Example")

frame = tk.Frame(root)
frame.grid(row=0, column=0)

autocomplete_entry = AutocompleteEntry(frame, ["Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", "Grape"])
autocomplete_entry.grid(row=0, column=0)

# 추가 위젯 생성
label = tk.Label(frame, text="Other Widget:")
label.grid(row=1, column=0)
button = tk.Button(frame, text="Click Me")
button.grid(row=1, column=1)
root.mainloop()

