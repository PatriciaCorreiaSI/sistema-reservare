import os
import sys

from sqlalchemy.orm import Session

from app.db import FabricaDeSessao
from app.models import Usuario
from app.schemas.usuario import UsuarioCriar
from app.services.excecoes import EmailJaCadastrado
from app.services.usuario import UsuarioService


def criar_admin(sessao: Session, nome: str, email: str, senha: str) -> Usuario:
    """Monta um UsuarioCriar com privilegio_usuario="admin"
    e delega ao UsuarioService. Não lê ambiente, não abre sessão,
    não comita.
    """
    dados = UsuarioCriar(
        nome_usuario=nome,
        email_usuario=email,
        senha=senha,
        privilegio_usuario="admin",
    )

    servico = UsuarioService(sessao)
    return servico.criar(dados)


def main() -> None:
    """Lê ADMIN_NOME, ADMIN_EMAIL, ADMIN_SENHA do ambiente (obrigatórias),
    abre uma sessão com transação, chama criar_admin. Em EmailJaCadastrado:
    mensagem no stderr e sys.exit(1). No sucesso: imprime id e e-mail,
    nunca a senha.
    """

    nome = os.environ["ADMIN_NOME"]
    email = os.environ["ADMIN_EMAIL"]
    senha = os.environ["ADMIN_SENHA"]

    try:
        with FabricaDeSessao() as sessao, sessao.begin():
            admin = criar_admin(sessao, nome=nome, email=email, senha=senha)
            id_admin = admin.id_usuario
    except EmailJaCadastrado:
        print(f"Erro: já existe um usuário com o e-mail {email}.", file=sys.stderr)
        sys.exit(1)  # código de saída ≠ 0: quem chamou sabe que falhou

    # Só aqui o commit já aconteceu: agora é verdade que o admin existe.
    print(f"Admin criado: id={id_admin}, e-mail={email}")


if __name__ == "__main__":
    main()
