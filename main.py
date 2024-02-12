import textwrap
from datetime import datetime
from abc import ABC, abstractmethod


class Cliente:
    def __init__(self, endereco: str):
        self.endereco = endereco
        self.contas = []

    @staticmethod
    def realizar_transacao(*, conta: 'Conta', transacao: 'Transacao'):
        transacao.registrar(conta=conta)

    def adicionar_conta(self, *, conta: 'Conta'):
        self.contas.append(conta)

    @property
    @abstractmethod
    def nome(self) -> str:
        pass


class PessoaFisica(Cliente):
    def __init__(self, cpf: str, nome: str, data_nascimento: str,
                 endereco: str):
        super().__init__(endereco)
        self.__cpf = cpf
        self.__nome = nome
        self.__data_nascimento = data_nascimento

    def nome(self) -> str:
        return self.__nome


class Conta:
    def __init__(self, *, numero: int,
                 cliente: Cliente):
        self.__saldo = 0
        self.__numero = numero
        self.__agencia = '0001'
        self.__cliente = cliente
        self.__historico = Historico()

    @classmethod
    def nova_conta(cls, cliente: Cliente, numero: int) -> 'Conta':
        return cls(cliente=cliente, numero=numero)

    @property
    def saldo(self) -> float:
        return self.__saldo

    @property
    def numero(self) -> int:
        return self.__numero

    @property
    def agencia(self) -> str:
        return self.__agencia

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def historico(self) -> 'Historico':
        return self.__historico

    def sacar(self, valor: float) -> bool:

        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("Operação falhou! você não tem saldo suficiente.")

        elif valor > 0:
            self.__saldo -= valor
            print("\nSaque realizado com sucesso!")
            return True

        else:
            print("\n Operação falhou! O valor informado é inválido.")

        return False

    def depositar(self, valor: float) -> bool:
        if valor > 0:
            self.__saldo += valor
            print("\nDepósito realizado com sucesso!")

        else:
            print("\nOperação falhou! O valor informado é inválido.")
            return False

        return True


class ContaCorrente(Conta):
    LIMITE_SAQUES: int = 3
    LIMITE: float = 500.00

    def __init__(self, *, numero: int, cliente: Cliente):
        super().__init__(numero=numero, cliente=cliente)

    def sacar(self, valor: float) -> bool:
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self.LIMITE
        excedeu_saques = numero_saques >= self.LIMITE_SAQUES

        if excedeu_limite:
            print("\nOperação falhou! O valor do saque excede o limite.")

        elif excedeu_saques:
            print("\nOperação falhou! Número máximo de saques excedido.")

        else:
            return super().sacar(valor=valor)

        return False

    def __str__(self):
        return f'''
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Títular:\t{self.cliente.nome}
        '''


class Historico:
    def __init__(self):
        self.__transacoes = []

    @property
    def transacoes(self):
        return self.__transacoes

    def adicionar_transacao(self, transacao: 'Transacao'):
        self.__transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%s"
                ),
            }
        )


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self) -> float:
        pass

    @abstractmethod
    def registrar(self, *, conta: Conta) -> None:
        pass


class Saque(Transacao):
    def __init__(self, *, valor: float):
        self.__valor = valor

    @property
    def valor(self) -> float:
        return self.__valor

    def registrar(self, *, conta: Conta) -> None:
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(transacao=self)


class Deposito(Transacao):
    def __init__(self, *, valor: float):
        self.__valor = valor

    @property
    def valor(self) -> float:
        return self.__valor

    def registrar(self, *, conta: Conta) -> None:
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(transacao=self)


###############################################
# Inicio
def menu() -> str:
    display: str = """\n
    =============== MENU ===============
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova Conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(display))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in
                          clientes if cliente.cpf == cpf]

    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente n~ao encontrado! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor=valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor=valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n=============== EXTRATO ===============")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += (f"\n{transacao['tipo']}:\n\t"
                        f"R$ {transacao['valor']:.2f}")

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("============================================")


def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro -"
                     " cidade/sigla estado): ")

    cliente = PessoaFisica(nome, data_nascimento, cpf, endereco)

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente n~ao encontrado, fluxo de criação"
              " de conta encerrado! @@@")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    for conta in contas:
        print("." * 100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("\n@@@ Operação inválida, por favor"
                  "selecione novamente a operação desejada. @@@")


if __name__ == '__main__':
    main()
