import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import uuid
import sqlite3

class TaskManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Gerenciador de Tarefas StarkCorporation")
        self.master.configure(bg="#474545")  
        self.timer_started = False
        self.timer_stopped = True
        self.current_task_index = None

        self.conn = sqlite3.connect('BaseData.db')
        self.cursor = self.conn.cursor()

        self.create_table_if_not_exists()

        self.tarefa = []
        self.retrieve_tasks_from_database()

        self.label_description = tk.Label(master, text="Descrição:", bg="#474545", fg="white")
        self.label_description.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.entry_description = tk.Entry(master, width=50)
        self.entry_description.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

        self.label_start_date = tk.Label(master, text="Data de Início:", bg="#474545", fg="white")
        self.label_start_date.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.entry_start_date = tk.Entry(master)
        self.entry_start_date.grid(row=1, column=1, padx=5, pady=5)

        self.label_duration = tk.Label(master, text="Duração (dias):", bg="#474545", fg="white")
        self.label_duration.grid(row=1, column=2, padx=5, pady=5, sticky="e")

        self.entry_duration = tk.Entry(master)
        self.entry_duration.grid(row=1, column=3, padx=5, pady=5)

        self.add_button = tk.Button(master, text="Adicionar Tarefa", command=self.add_task)
        self.add_button.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

        self.remove_completed_button = tk.Button(master, text="Remover Tarefas Concluídas", command=self.remover_tarefa_complet)
        self.remove_completed_button.grid(row=4, column=0, columnspan=4, padx=5, pady=5)

        self.history_button = tk.Button(master, text="Histórico", command=self.ver_histotico)
        self.history_button.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

        self.history_button = tk.Button(master, text="Clean DB", command=self.limpar_banco_dados)
        self.history_button.grid(row=6, column=0, columnspan=4, padx=5, pady=5)

        self.tarefa_list_frame = tk.Frame(master, bg="#474545")
        self.tarefa_list_frame.grid(row=7, column=0, columnspan=4, padx=5, pady=5)

        self.legend_frame = tk.Frame(master)
        self.legend_frame.grid(row=8, column=4, padx=5, pady=5, sticky="n")

        self.legend_click_label = tk.Label(self.legend_frame, text="Clique na cor ao lado da tarefa \n para alterar o status ", bg="#474545", fg="white")
        self.legend_click_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)

        self.legend_red_label = tk.Label(self.legend_frame, text="A fazer: vermelho", bg="red", fg="white")
        self.legend_red_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)

        self.legend_yellow_label = tk.Label(self.legend_frame, text="Em andamento: amarelo", bg="yellow", fg="black")
        self.legend_yellow_label.grid(row=3, column=0, sticky="w", padx=5, pady=2)

        self.legend_green_label = tk.Label(self.legend_frame, text="Concluído: verde", bg="green", fg="white")
        self.legend_green_label.grid(row=4, column=0, sticky="w", padx=5, pady=2)

        self.update_tarefa_list()

    def create_table_if_not_exists(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS controle
                               (id INTEGER PRIMARY KEY, description TEXT, start_date TEXT, end_date TEXT, status TEXT)''')
        self.conn.commit()

    def insert_tarefa_to_database(self, tarefa):
        self.cursor.execute("INSERT INTO controle (description, start_date, end_date, status) VALUES (?, ?, ?, ?)",
                            (tarefa["description"], tarefa["start_date"], tarefa["end_date"], tarefa["status"]))
        self.conn.commit()

    def update_tarefa_in_database(self, task):
        self.cursor.execute("UPDATE controle SET status = ? WHERE id = ?", (task["status"], task["id"]))
        self.conn.commit()

    def remove_task_from_database(self, task_id):
        self.cursor.execute("DELETE FROM controle WHERE id = ?", (task_id,))
        self.conn.commit()

    def retrieve_tasks_from_database(self):
        self.cursor.execute("SELECT * FROM controle")
        rows = self.cursor.fetchall()
        for row in rows:
            task = {"id": row[0],
                    "description": row[1],
                    "start_date": row[2],
                    "end_date": row[3],
                    "status": row[4]}
            self.tarefa.append(task)

    def add_task(self):
        description = self.entry_description.get()
        start_date = self.entry_start_date.get()
        duration = int(self.entry_duration.get())

        if description and start_date and duration:
            start_date = datetime.strptime(start_date, "%d/%m/%Y")
            end_date = start_date + timedelta(days=duration)
            task_id = str(uuid.uuid4())  # Gera um ID único para a tarefa
            tarefa = {"id": task_id,
                    "description": description,
                    "start_date": start_date.strftime("%d/%m/%Y"),
                    "end_date": end_date.strftime("%d/%m/%Y"),
                    "status": "A fazer"}
            self.tarefa.append(tarefa)
            self.insert_tarefa_to_database(tarefa)  # Adiciona a tarefa ao banco de dados
            self.update_tarefa_list()
        else:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos.")

    def update_tarefa_list(self):
        for widget in self.tarefa_list_frame.winfo_children():
            widget.destroy()

        for i, task in enumerate(self.tarefa):
            tarefa_descricao = task["description"]
            tarefa_status = task["status"]
            checkbox = tk.Checkbutton(self.tarefa_list_frame, text=tarefa_descricao, variable=tk.BooleanVar(value=tarefa_status == "Concluído"), bg="#474545", fg="white")
            checkbox.grid(row=i, column=0, sticky="w")
            status_color = "red" if tarefa_status == "A fazer" else "yellow" if tarefa_status == "Em andamento" else "green"
            status_ball = tk.Canvas(self.tarefa_list_frame, width=20, height=20, bg="#474545", highlightthickness=0)
            status_ball.grid(row=i, column=1, padx=(10,0))
            status_ball.create_oval(5, 5, 15, 15, fill=status_color, tags=("status_ball", str(i)))
            status_ball.bind("<Button-1>", lambda event, index=i: self.mudar_tarefa_status(event, index))

    def mudar_tarefa_status(self, event, index):
        atual_status = self.tarefa[index]["status"]
        new_status = "Em andamento" if atual_status == "A fazer" else "Concluído" if atual_status == "Em andamento" else "A fazer"
        self.tarefa[index]["status"] = new_status
        self.update_tarefa_in_database(self.tarefa[index])  # Atualiza o status da tarefa no banco de dados
        self.update_tarefa_list()

    def remover_tarefa_complet(self):
        tarefas_concluidas = [tarefa for tarefa in self.tarefa if tarefa["status"] == "Concluído"]
        self.tarefa = [tarefa for tarefa in self.tarefa if tarefa["status"] != "Concluído"]
        self.update_tarefa_list()

    def limpar_banco_dados(self):
        resposta = messagebox.askquestion("Limpar Banco de Dados", "Tem certeza que deseja limpar o banco de dados? Isso apagará todos os dados permanentemente.")
        if resposta == "yes":
            self.cursor.execute("DELETE FROM controle")
            self.conn.commit()
            messagebox.showinfo("Banco de Dados Limpo", "O banco de dados foi limpo com sucesso.")
            self.tarefa = []
            self.update_tarefa_list()

    def ver_histotico(self):
        historico = tk.Toplevel(self.master)
        historico.title("Histórico de Tarefas")

        table = tk.Frame(historico, bg="#474545")
        table.pack(padx=10, pady=10)

        tk.Label(table, text="Descrição", bg="#474545", fg="white", borderwidth=1, relief="solid", width=40).grid(row=0, column=0)
        tk.Label(table, text="Data de Início", bg="#474545", fg="white", borderwidth=1, relief="solid", width=20).grid(row=0, column=1)
        tk.Label(table, text="Prazo", bg="#474545", fg="white", borderwidth=1, relief="solid", width=20).grid(row=0, column=2)
        tk.Label(table, text="Situação", bg="#474545", fg="white", borderwidth=1, relief="solid", width=20).grid(row=0, column=3)

        today = datetime.now().date()
        for i, tarefa in enumerate(self.tarefa):
            inicio_date = datetime.strptime(tarefa["start_date"], "%d/%m/%Y").date()
            duracao = datetime.strptime(tarefa["end_date"], "%d/%m/%Y").date() - inicio_date
            duracao_str = f"{duracao.days} dias"
            situacao = tarefa["status"]
            tk.Label(table, text=tarefa["description"], bg="#474545", fg="white", borderwidth=1, relief="solid", width=40).grid(row=i+1, column=0)
            tk.Label(table, text=inicio_date.strftime("%d/%m/%Y"), bg="#474545", fg="white", borderwidth=1, relief="solid", width=20).grid(row=i+1, column=1)
            tk.Label(table, text=duracao_str, bg="#474545", fg="white", borderwidth=1, relief="solid", width=20).grid(row=i+1, column=2)
            tk.Label(table, text=situacao, bg="#474545", fg="white", borderwidth=1, relief="solid", width=20).grid(row=i+1, column=3)

def main():
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
