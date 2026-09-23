from sqlalchemy.orm import Session

from app.models import Usuario


def criar_admin(sessao: Session, nome: str, email: str, senha: str) -> Usuario:
    """Monta um UsuarioCriar com privilegio_usuario="admin"
    e delega ao UsuarioService. Não lê ambiente, não abre sessão,
    não comita.
    """
    raise NotImplementedError


def main() -> None:
    """Lê ADMIN_NOME, ADMIN_EMAIL, ADMIN_SENHA do ambiente (obrigatórias),
    abre uma sessão com transação, chama criar_admin. Em EmailJaCadastrado:
    mensagem no stderr e sys.exit(1). No sucesso: imprime id e e-mail,
    nunca a senha.
    """


if __name__ == "__main__":
    main()
