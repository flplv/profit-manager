## Profit Manager

Processa as notas de corretagem exportadas das corretoras Clear, XP e Itaú (solicite suporte para a sua corretora via issues) e gera os relatórios de fluxo de caixa, ganhos e posição final. 

## Dependencias

* pip3 install pdfminer.six
* pip3 install tabulate

## Como usar

1) Baixe todas as notas de corretagem na Clear ou Xp (sem senha) e coloque em uma pasta.
2) Na mesma pasta crie um arquivo "initial_position.csv" e preencha com as posições iniciais e injeções de desdobramento 
como a seguir:

```
  "VISTA VIAVAREJO"     , "2019-01-00", 100,   5.01, "p. inicial"
  "VISTA GUARARAPES"    , "2019-05-02", 1000,  0.00, "desdobramento"
```
Os campos do CSV são respectivamente:

    1. Nome da maneira que é exportada da nota de corretagem
    2. Data YYYY-MM-DD
    3. Número de ações (Positivo para compra ou negativo para venda)
    4. Custo da unidade na operação
    5. Uma anotação textual para debug

3) Agora execute o programa na pasta em que os arquivos foram salvos e gerados:

```
$ PYTHONPATH=$PYTHONPATH:/path/to/install/dir python3 /path/to/install/dir/profit_manager
```

Observe a mensagens no console, verifique bem os números para ter certeza que as condições iniciais estão corretas 
e que os PDFs foram carregados corretamente.

Arquivos vão ser gerados: 

- database.csv, para debug
- final_position.csv, para ser usado no ano seguinte ou mês seguinte caso você precise de diferentes períodos de condição inicial

(tanto o database.csv ou o final_position.csv podem ser usados como ponto de partida)

Divirta-se, e... viva o leão!


## TODO

### short avançado
Operações de short não foram testadas o suficiente. Para shorts básicos 
funciona ok.

Shorts básicos são operações que não executaram troca de quadrante, e sim
primeiro a posição vai a zero e depois outra operação é que inverte 
o saldo de ações para positivo ou negativo.

### duplicação de notas
As notas são parseadas às cegas, sem verificar o número da nota contra operação duplicada. 

### Taxas de operação
As taxas não são descontadas dos lucros, nem computadas ou apresentadas nos relatórios.
Em tese, essas taxas poderiam ser descontadas dos lucros antes de pagar impostos, portanto
TODO.
