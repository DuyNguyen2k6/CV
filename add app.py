# add_app_gui_v2.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re

class AppEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý Kho Công Cụ trong index.html")
        self.root.geometry("800x600")

        self.file_path = tk.StringVar()

        self.setup_ui()

    def setup_ui(self):
        # Chọn file
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)
        tk.Label(top_frame, text="File index.html:").pack(side=tk.LEFT)
        tk.Entry(top_frame, textvariable=self.file_path, width=60).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Duyệt...", command=self.browse_file).pack(side=tk.LEFT)
        tk.Button(top_frame, text="Tải danh sách", command=self.load_apps).pack(side=tk.LEFT, padx=10)

        # Treeview
        columns = ("type", "name", "link", "desc")
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        self.tree.heading("type", text="Loại")
        self.tree.heading("name", text="Tên")
        self.tree.heading("link", text="Liên kết")
        self.tree.heading("desc", text="Mô tả")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree.bind("<Double-1>", self.on_tree_select)

        # Form chỉnh sửa/thêm mới
        form = tk.Frame(self.root)
        form.pack(pady=10)
        self.type_var = tk.StringVar(value="extension")
        self.name_var = tk.StringVar()
        self.icon_var = tk.StringVar()
        self.link_var = tk.StringVar()
        self.desc_var = tk.StringVar()

        for i, (label, var) in enumerate([
            ("Loại (extension/python):", self.type_var),
            ("Tên App:", self.name_var),
            ("Icon URL:", self.icon_var),
            ("Liên kết:", self.link_var),
            ("Mô tả:", self.desc_var)
        ]):
            tk.Label(form, text=label).grid(row=i, column=0, sticky="e")
            tk.Entry(form, textvariable=var, width=60).grid(row=i, column=1, padx=5, pady=2)

        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=10)
        tk.Button(action_frame, text="Thêm App", command=self.add_app).pack(side=tk.LEFT, padx=5)
        tk.Button(action_frame, text="Cập nhật App đã chọn", command=self.update_app).pack(side=tk.LEFT, padx=5)

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("HTML Files", "*.html")])
        if path:
            self.file_path.set(path)

    def load_apps(self):
        path = self.file_path.get()
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()

        self.tree.delete(*self.tree.get_children())
        self.blocks = []

        pattern = re.compile(r'<li>.*?<a href="(.*?)".*?class="tool-link (.*?)">\s*(.*?)\s*</a>.*?<p class="tool-desc">(.*?)</p>', re.DOTALL)
        for match in pattern.finditer(html):
            link, tool_class, name, desc = match.groups()
            app_type = "extension" if "extension" in tool_class else "python"
            self.blocks.append((match.start(), match.end(), match.group()))
            self.tree.insert("", "end", values=(app_type, name.strip(), link.strip(), desc.strip()))

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

        # icon không hiển thị trong bảng nên đặt trống
        self.icon_var.set("")

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
    app = AppEditor(root)
    root.mainloop()