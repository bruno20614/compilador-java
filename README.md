# Analisador léxico e sintático LL(1)

Projeto em Python que integra o analisador léxico manual do Trabalho 1 a um analisador sintático preditivo LL(1), sem geradores automáticos.

## Requisitos e execução

Requer Python 3.10 ou superior. Na raiz do projeto, execute:

```powershell
python main.py exemplos/Exemplo1_Sucesso.java --sintatico
```

O programa exibe os tokens, FIRST e FOLLOW, todas as células preenchidas da tabela M, o trace da pilha e o veredito. Para analisar apenas lexicalmente, omita `--sintatico`. Também é possível usar `--buffer-size 16` e `--buffer-view`.

## Exemplos para demonstração

```powershell
python main.py exemplos/Exemplo1_Sucesso.java --sintatico
python main.py exemplos/Exemplo2_ErroTabela.java --sintatico
python main.py exemplos/Exemplo3_ErroPilha.java --sintatico
```

O segundo exemplo produz erro ao esperar o início de um fator após `+`. O terceiro detecta `;` enquanto `)` está no topo da pilha. A recuperação em modo pânico descarta tokens até sincronizar em `;` ou `}` quando possível.

## Gramática e limites

A gramática está declarada em `sintatico.py`; FIRST, FOLLOW e M são calculados dinamicamente a partir dela. Os terminais `id` e `num` são obtidos pelo tipo dos tokens do lexer. `main` é reconhecido pelo lexer como identificador, portanto a produção inicial mantém o `id` do enunciado.

Este trabalho reconhece somente a gramática simplificada fornecida: assinatura `main()` sem argumentos, declarações sem inicialização, tipos `int`/`float`/`char`, atribuições, expressões aritméticas e comparações `==`, `!=`, `<`, `>`. Recursos Java fora dessa gramática serão apontados como inválidos.
