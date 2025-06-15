import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re

class IOSStyleAppEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý Kho Công Cụ")

        # Mở cửa sổ ở trạng thái tối đa (maximize)
        self.root.state('zoomed')

        self.root.configure(bg="#F9F9F9")

        self.file_path = tk.StringVar()

        self.font_label = ("Helvetica", 11)
        self.font_entry = ("Helvetica", 11)
        self.font_button = ("Helvetica", 11, "bold")

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TCombobox', padding=6, font=self.font_entry)
        style.configure('Treeview', font=self.font_entry, rowheight=24)
        style.configure('Treeview.Heading', font=("Helvetica", 11, "bold"))

        top_frame = tk.Frame(self.root, bg="#F9F9F9")
        top_frame.pack(fill='x', padx=20, pady=15)

        tk.Label(top_frame, text="File index.html:", bg="#F9F9F9", fg="#8E8E93", font=self.font_label).pack(side=tk.LEFT)
        tk.Entry(top_frame, textvariable=self.file_path, width=55, font=self.font_entry, relief='flat', bd=0, highlightthickness=2, highlightcolor="#5AC8FA").pack(side=tk.LEFT, padx=10, ipady=6)
        ttk.Button(top_frame, text="Duyệt...", command=self.browse_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="Tải danh sách", command=self.load_apps).pack(side=tk.LEFT, padx=5)

        tree_frame = tk.Frame(self.root, bg="#F9F9F9")
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ("type", "name", "link", "desc", "icon")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        self.tree.heading("type", text="Loại")
        self.tree.heading("name", text="Tên")
        self.tree.heading("link", text="Liên kết")
        self.tree.heading("desc", text="Mô tả")
        self.tree.heading("icon", text="Icon URL")

        self.tree.column("type", width=80, anchor='center')
        self.tree.column("name", width=180, anchor='w')
        self.tree.column("link", width=300, anchor='w')
        self.tree.column("desc", width=300, anchor='w')
        self.tree.column("icon", width=0, stretch=False)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill='y')
        self.tree.pack(fill='both', expand=True, side=tk.LEFT)

        self.tree.bind("<Double-1>", self.on_tree_select)

        form_frame = tk.Frame(self.root, bg="#F9F9F9")
        form_frame.pack(fill='x', padx=20, pady=20)

        # Cho phép cột 1 (input) co giãn theo chiều ngang
        form_frame.grid_columnconfigure(1, weight=1)

        tk.Label(form_frame, text="Loại (extension/python):", bg="#F9F9F9", fg="#8E8E93", font=self.font_label).grid(row=0, column=0, sticky='e', pady=10)
        self.type_var = tk.StringVar(value="extension")
        type_combo = ttk.Combobox(form_frame, textvariable=self.type_var, values=["extension", "python"], state="readonly", font=self.font_entry)
        type_combo.grid(row=0, column=1, pady=10, sticky='ew')

        labels = ["Tên App:", "Icon URL:", "Liên kết:", "Mô tả:"]
        self.name_var = tk.StringVar()
        self.icon_var = tk.StringVar()
        self.link_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        vars_ = [self.name_var, self.icon_var, self.link_var, self.desc_var]

        for i, (label, var) in enumerate(zip(labels, vars_), start=1):
            tk.Label(form_frame, text=label, bg="#F9F9F9", fg="#8E8E93", font=self.font_label).grid(row=i, column=0, sticky='e', pady=10)
            ent = tk.Entry(form_frame, textvariable=var, font=self.font_entry, relief='solid', bd=1)
            ent.grid(row=i, column=1, pady=10, sticky='ew')

        btn_frame = tk.Frame(self.root, bg="#F9F9F9")
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="➕ Thêm App", command=self.add_app,
                  width=16, font=self.font_button,
                  bg="#007acc", fg="white", relief='raised', padx=10, pady=5).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="💾 Cập nhật App", command=self.update_app,
                  width=16, font=self.font_button,
                  bg="#00a676", fg="white", relief='raised', padx=10, pady=5).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="🗑️ Xoá App", command=self.delete_app,
                  width=16, font=self.font_button,
                  bg="#d9534f", fg="white", relief='raised', padx=10, pady=5).pack(side=tk.LEFT, padx=10)

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("HTML Files", "*.html")])
        if path:
            self.file_path.set(path)

    def load_apps(self):
        path = self.file_path.get()
        if not path:
            return
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()

        self.tree.delete(*self.tree.get_children())
        self.blocks = []

        pattern = re.compile(
            r'<li>.*?<img src="(.*?)".*?>.*?<a href="(.*?)".*?class="tool-link (.*?)">\s*(.*?)\s*</a>.*?<p class="tool-desc">(.*?)</p>',
            re.DOTALL
        )
        for match in pattern.finditer(html):
            icon_url, link, tool_class, name, desc = match.groups()
            app_type = "extension" if "extension" in tool_class else "python"
            self.blocks.append((match.start(), match.end(), match.group()))
            self.tree.insert("", "end", values=(app_type, name.strip(), link.strip(), desc.strip(), icon_url.strip()))

        self.html = html

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])['values']
        self.type_var.set(values[0])
        self.name_var.set(values[1])
        self.link_var.set(values[2])
        self.desc_var.set(values[3])
        self.icon_var.set(values[4] if len(values) > 4 else "")

    def add_app(self):
        new_li = self.build_li()
        target = "category-extension" if self.type_var.get() == "extension" else "category-python"

        insert_pos = self.html.find(f'<div class="category {target}">')
        ul_pos = self.html.find('<ul class="tools-list">', insert_pos)
        end_ul = self.html.find('</ul>', ul_pos)
        self.html = self.html[:end_ul] + new_li + self.html[end_ul:]

        self.save_and_reload()

    def update_app(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Lỗi", "Vui lòng chọn app cần cập nhật")
            return
        index = self.tree.index(selected[0])
        start, end, old_block = self.blocks[index]
        new_li = self.build_li()

        self.html = self.html[:start] + new_li + self.html[end:]
        self.save_and_reload()

    def delete_app(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Lỗi", "Vui lòng chọn app cần xoá")
            return
        index = self.tree.index(selected[0])
        start, end, old_block = self.blocks[index]

        confirm = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xoá app đã chọn không?")
        if not confirm:
            return

        self.html = self.html[:start] + self.html[end:]
        self.save_and_reload()

    def build_li(self):
        return f'''
      <li>
        <div class="tool-info" style="display:flex; align-items:center; gap:10px;">
          <img src="{self.icon_var.get()}" alt="{self.name_var.get()} Icon" style="width:24px; height:24px;" />
          <a href="{self.link_var.get()}" target="_blank" rel="noopener noreferrer" class="tool-link {'extension-link' if self.type_var.get() == 'extension' else 'python-link'}">
            {self.name_var.get()}
          </a>
        </div>
        <p class="tool-desc">{self.desc_var.get()}</p>
      </li>
'''

    def save_and_reload(self):
        with open(self.file_path.get(), "w", encoding="utf-8") as f:
            f.write(self.html)
        self.load_apps()
        messagebox.showinfo("Thành công", "Đã lưu thay đổi và làm mới danh sách.")

if __name__ == "__main__":
    root = tk.Tk()
    app = IOSStyleAppEditor(root)
    root.mainloop()
