import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime, timedelta
import time
import threading
from plyer import notification


# Configuração do banco de dados
con = sqlite3.connect("tasks.db")
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    completed INTEGER NOT NULL
)""")
con.commit()

class TaskManager:
    def __init__(self, master):
        self.master = master
        self.master.title("Gerenciador de Tarefas")
        self.master.geometry("600x450")
        self.master.resizable(False, False)

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 12))
        self.style.configure("TButton", font=("Arial", 12))

        self.frame_top = ttk.Frame(self.master)
        self.frame_top.pack(pady=10)

        self.frame_middle = ttk.Frame(self.master)
        self.frame_middle.pack()

        self.frame_bottom = ttk.Frame(self.master)
        self.frame_bottom.pack(side="bottom", pady=10)

        self.create_widgets()
    


    def main():
        root = tk.Tk()
        app = TaskManager(root)

        reminder_thread = threading.Thread(target=send_reminder, daemon=True)
        reminder_thread.start()

        root.mainloop()

    def create_widgets(self):
        self.label_description = ttk.Label(self.frame_top, text="Descrição:")
        self.label_description.grid(row=0, column=0, padx=(10, 0), pady=5)

        self.entry_description = ttk.Entry(self.frame_top, width=40)
        self.entry_description.grid(row=0, column=1, padx=(0, 10), pady=5)

        self.label_date = ttk.Label(self.frame_top, text="Data (DD/MM/AAAA):")
        self.label_date.grid(row=1, column=0, padx=(10, 0), pady=5)

        self.entry_date = ttk.Entry(self.frame_top, width=20)
        self.entry_date.grid(row=1, column=1, padx=(0, 10), pady=5)

        self.label_time = ttk.Label(self.frame_top, text="Hora (HH:MM):")
        self.label_time.grid(row=2, column=0, padx=(10, 0), pady=5)

        self.entry_time = ttk.Entry(self.frame_top, width=20)
        self.entry_time.grid(row=2, column=1, padx=(0, 10), pady=5)

        self.empty_space_left = ttk.Frame(self.frame_top, width=50)  # Ajuste o valor de width aqui
        self.empty_space_left.grid(row=3, column=0)

        self.button_add_task = ttk.Button(self.frame_top, text="Adicionar Tarefa", command=self.add_task)
        self.button_add_task.grid(row=3, column=1, padx=(0, 10), pady=10)  # Remova a opção sticky aqui

        self.treeview = ttk.Treeview(self.frame_middle, columns=("description", "date", "time", "completed"), show="headings", height=8)

        self.treeview.heading("description", text="Descrição")
        self.treeview.heading("date", text="Data")
        self.treeview.heading("time", text="Hora")
        self.treeview.heading("completed", text="Realizada")

        self.treeview.column("description", width=200)
        self.treeview.column("date", width=100)
        self.treeview.column("time", width=100)
        self.treeview.column("completed", width=100)

        self.treeview.pack(padx=10, pady=(0, 10))
        # Cria um novo frame para o rodapé
        self.footer_frame = ttk.Frame(self.master)
        self.footer_frame.pack(side="bottom", pady=(0, 10))

        

# Adiciona um label com seu nome no rodapé
        self.footer_label = ttk.Label(self.footer_frame, text="Criado Por William Simas ©", font=("Arial", 10))
        self.footer_label.pack()

        self.load_tasks()

        self.empty_space = ttk.Frame(self.frame_bottom, height=5)  # Ajuste o valor de height aqui
        self.empty_space.pack(side="top", fill="x")

        self.button_frame = ttk.Frame(self.frame_bottom)
        self.button_frame.pack(pady=0)

        self.button_complete_task = ttk.Button(self.button_frame, text="Marcar como Realizada", command=self.complete_task)
        self.button_complete_task.grid(row=0, column=0, padx=10, pady=0)

        self.button_delete_task = ttk.Button(self.button_frame, text="Excluir Tarefa", command=self.delete_task)
        self.button_delete_task.grid(row=0, column=1, padx=10, pady=0)
    def load_tasks(self):
        self.treeview.delete(*self.treeview.get_children())
        cur.execute("SELECT * FROM tasks")
        rows = cur.fetchall()

        for row in rows:
            completed = "Sim" if row[4] else "Não"
            self.treeview.insert("", "end", values=(row[1], row[2], row[3], completed), tags=(row[0],))

    def add_task(self):
        description = self.entry_description.get()
        date = self.entry_date.get()
        time = self.entry_time.get()

        if not description or not date or not time:
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return

        cur.execute("INSERT INTO tasks (description, date, time, completed) VALUES (?, ?, ?, 0)", (description, date, time))
        con.commit()

        self.load_tasks()
        self.entry_description.delete(0, tk.END)
        self.entry_date.delete(0, tk.END)
        self.entry_time.delete(0, tk.END)

    def complete_task(self):
        selected_item = self.treeview.selection()

        if not selected_item:
            messagebox.showerror("Erro", "Selecione uma tarefa para marcar como realizada.")
            return

        task_id = self.treeview.item(selected_item[0], "tags")[0]
        cur.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        con.commit()

        self.load_tasks()

    def delete_task(self):
        selected_item = self.treeview.selection()

        if not selected_item:
            messagebox.showerror("Erro", "Selecione uma tarefa para excluir.")
            return

        if messagebox.askyesno("Excluir Tarefa", "Tem certeza de que deseja excluir a tarefa selecionada?"):
            task_id = self.treeview.item(selected_item[0], "tags")[0]
            cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            con.commit()

            self.load_tasks()
def send_reminder():
    reminder_minutes_before = 10  
    reminder_interval = timedelta(minutes=reminder_minutes_before)

    while True:
        cur.execute("SELECT * FROM tasks WHERE completed = 0")
        tasks = cur.fetchall()
        current_datetime = datetime.now()

        for task in tasks:
            task_date = datetime.strptime(task[2], "%d/%m/%Y").date()
            task_time = datetime.strptime(task[3], "%H:%M").time()
            task_datetime = datetime.combine(task_date, task_time)

            if task_datetime - reminder_interval <= current_datetime < task_datetime:
                notification.notify(
                    title="Lembrete de Tarefa",
                    message=f"Tarefa: {task[1]}",
                    app_name="Gerenciador de Tarefas",
                    timeout=10
                )

        time.sleep(60)

def main():
    root = tk.Tk()
    app = TaskManager(root)
    reminder_thread = threading.Thread(target=send_reminder)
    reminder_thread.setDaemon(True)
    reminder_thread.start()
    root.mainloop()

if __name__ == "__main__":
    main()