import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# ─────────────────────────────────────────────
# Dados de usuários (poderia vir de um banco de dados)
# ─────────────────────────────────────────────
usuarios = {
    "professor": {"senha": "1234", "tipo": "professor"},
    "aluno1":    {"senha": "1234", "tipo": "aluno"},
    "aluno2":    {"senha": "1234", "tipo": "aluno"},
}

# Variável global que guarda o tipo do usuário logado
tipo_usuario_atual = None
usuario_atual = None

# ─────────────────────────────────────────────
# FUNÇÕES DE NEGÓCIO
# ─────────────────────────────────────────────

def verificar_situacao(nota1, nota2):
    media = (nota1 + nota2) / 2
    if media >= 7.0:
        situacao = "Aprovado"
    elif media >= 5.0:
        situacao = "Em Recuperação"
    else:
        situacao = "Reprovado"
    return media, situacao


def salvar_dados():
    dados = []
    for line in treeMedias.get_children():
        valores = treeMedias.item(line)["values"]
        dados.append(valores)

    colunas = ("Aluno", "Nota1", "Nota2", "Média", "Situação")
    df = pd.DataFrame(data=dados, columns=colunas)
    df.to_excel("planilhaAlunos.xlsx", index=False, engine="openpyxl")
    print("Dados salvos com sucesso.")


def carregar_dados():
    """Carrega os dados do Excel filtrando por tipo de usuário."""
    try:
        df = pd.read_excel("planilhaAlunos.xlsx")
        treeMedias.delete(*treeMedias.get_children())

        if tipo_usuario_atual == "professor":
            # Professor vê todos os alunos
            for _, row in df.iterrows():
                treeMedias.insert("", "end", values=(
                    row["Aluno"], row["Nota1"], row["Nota2"], row["Média"], row["Situação"]
                ))
        else:
            # Aluno vê apenas os próprios dados
            df_aluno = df[df["Aluno"] == usuario_atual]
            for _, row in df_aluno.iterrows():
                treeMedias.insert("", "end", values=(
                    row["Aluno"], row["Nota1"], row["Nota2"], row["Média"], row["Situação"]
                ))
    except FileNotFoundError:
        print("Nenhum dado encontrado. Iniciando com tabela vazia.")


def cadastrar_aluno():
    # BUG CORRIGIDO #1: usa a variável global tipo_usuario_atual
    if tipo_usuario_atual != "professor":
        messagebox.showwarning("Acesso Negado", "Somente professores podem adicionar alunos.")
        return

    try:
        nome = txtNome.get().strip()
        if not nome:
            messagebox.showwarning("Atenção", "O nome do aluno não pode estar vazio.")
            return

        nota1 = float(txtNota1.get())
        nota2 = float(txtNota2.get())

        media, situacao = verificar_situacao(nota1, nota2)
        treeMedias.insert("", "end", values=(nome, nota1, nota2, f"{media:.2f}", situacao))
        salvar_dados()

    except ValueError:
        messagebox.showerror("Erro", "Digite valores numéricos válidos para as notas.")
    finally:
        txtNome.delete(0, "end")
        txtNota1.delete(0, "end")
        txtNota2.delete(0, "end")


def excluir_aluno():
    # BUG CORRIGIDO #1: usa a variável global tipo_usuario_atual
    if tipo_usuario_atual != "professor":
        messagebox.showwarning("Acesso Negado", "Somente professores podem excluir registros.")
        return

    selected_item = treeMedias.selection()
    if not selected_item:
        messagebox.showerror("Erro", "Nenhum aluno selecionado para exclusão.")
        return

    treeMedias.delete(selected_item)
    salvar_dados()  # BUG CORRIGIDO #2: indentação corrigida — agora está dentro da função


def atualizar_interface_por_permissao():
    """Mostra ou oculta widgets de acordo com o tipo de usuário."""
    if tipo_usuario_atual == "professor":
        # Professor vê campos de cadastro e botão excluir
        frame_cadastro.pack(pady=5)
        btnExcluir.pack(pady=2)
    else:
        # Aluno não vê os controles de edição
        frame_cadastro.pack_forget()
        btnExcluir.pack_forget()


# ─────────────────────────────────────────────
# TELA DE LOGIN
# ─────────────────────────────────────────────

def abrir_tela_login():
    login_win = tk.Toplevel()
    login_win.title("Login")
    login_win.geometry("300x200")
    login_win.grab_set()  # Impede interação com a janela principal enquanto login está aberto

    tk.Label(login_win, text="Usuário:").pack(pady=(20, 0))
    entry_usuario = tk.Entry(login_win)
    entry_usuario.pack()

    tk.Label(login_win, text="Senha:").pack(pady=(10, 0))
    entry_senha = tk.Entry(login_win, show="*")
    entry_senha.pack()

    def validar_login():
        global tipo_usuario_atual, usuario_atual

        usuario = entry_usuario.get().strip()
        senha = entry_senha.get()

        if usuario in usuarios and usuarios[usuario]["senha"] == senha:
            tipo_usuario_atual = usuarios[usuario]["tipo"]
            usuario_atual = usuario
            login_win.destroy()
            iniciar_sistema()   # BUG CORRIGIDO #4: iniciar_sistema agora é chamado APÓS os widgets existirem
        else:
            messagebox.showerror("Erro", "Credenciais inválidas!", parent=login_win)

    tk.Button(login_win, text="Entrar", command=validar_login).pack(pady=10)


def iniciar_sistema():
    """Chamada após login bem-sucedido: exibe a janela principal e carrega os dados."""
    janela.deiconify()
    atualizar_interface_por_permissao()
    carregar_dados()


# ─────────────────────────────────────────────
# JANELA PRINCIPAL + WIDGETS
# BUG CORRIGIDO #3 e #5: todos os widgets são criados ANTES do mainloop,
# e o mainloop fica no final do código.
# ─────────────────────────────────────────────

janela = tk.Tk()
janela.title("Sistema de Cadastro de Alunos")
janela.geometry("820x600")
janela.withdraw()  # Oculta até o login ser concluído

# ── Frame de cadastro (visível apenas para professor) ──
frame_cadastro = tk.Frame(janela)

lblNome = tk.Label(frame_cadastro, text="Nome do Aluno:")
lblNome.pack()
txtNome = tk.Entry(frame_cadastro, bd=3)
txtNome.pack(pady=(0, 4))

lblNota1 = tk.Label(frame_cadastro, text="Nota 1:")
lblNota1.pack()
txtNota1 = tk.Entry(frame_cadastro)
txtNota1.pack(pady=(0, 4))

lblNota2 = tk.Label(frame_cadastro, text="Nota 2:")
lblNota2.pack()
txtNota2 = tk.Entry(frame_cadastro)
txtNota2.pack(pady=(0, 4))

btnCadastrar = tk.Button(frame_cadastro, text="Cadastrar Aluno", command=cadastrar_aluno)
btnCadastrar.pack(pady=4)

# ── Tabela de resultados ──
frame_tabela = tk.Frame(janela)
frame_tabela.pack(padx=10, pady=10, fill="both", expand=True)

colunas = ("Aluno", "Nota1", "Nota2", "Média", "Situação")
treeMedias = ttk.Treeview(frame_tabela, columns=colunas, show="headings")

for coluna in colunas:
    treeMedias.heading(coluna, text=coluna)
    treeMedias.column(coluna, width=120)

scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=treeMedias.yview)
treeMedias.configure(yscrollcommand=scrollbar.set)

treeMedias.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# ── Botão excluir (visível apenas para professor) ──
btnExcluir = tk.Button(janela, text="Excluir Aluno", command=excluir_aluno)

# ─────────────────────────────────────────────
# INICIALIZAÇÃO
# BUG CORRIGIDO #5: mainloop fica no FINAL, após toda a definição de widgets e funções
# ─────────────────────────────────────────────
abrir_tela_login()
janela.mainloop()


import pandas as pd

df = pd.read_excel("planilhaAlunos.xlsx")

print(f"Total de alunos: {len(df)}\n")
print(df.to_string(index=False))