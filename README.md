Visão Geral da Solução

Este projeto simula um sistema embarcado para monitoramento de uma linha de produção utilizando um ESP32 no Wokwi. O sistema conta peças, detecta micro-paradas por meio de um sensor de luminosidade (LDR) e permite o reset manual do turno através de um botão. A interação do usuário é feita alterando a luminosidade do sensor e acionando o botão de reset, com todas as informações exibidas no monitor serial.

## Arquitetura do Sistema Embarcado

O `main.py` executa um loop contínuo que lê o sensor de luminosidade e o botão de reset. Quando o LDR identifica o bloqueio e a liberação da luz, uma peça é contabilizada. Se o bloqueio permanecer por cinco segundos, o sistema emite um alerta de micro-parada.

O botão é monitorado para detectar quando foi pressionado e solto. Após a liberação, os contadores e estados do sistema são zerados.

```text
LDR ──► ESP32 ──► Contagem de peças
                 ├─► Alerta de micro-parada
Botão ──────────►└─► Reset do turno

ESP32 ──► Monitor serial
```

O ESP32 centraliza o processamento, recebe os sinais do LDR e do botão e exibe os resultados no monitor serial.

## Componentes Utilizados na Simulação

* **ESP32 DevKit V4:** placa microcontroladora responsável por executar o programa, processar as leituras do sensor e controlar a lógica do sistema.
* **Sensor de Luminosidade (LDR):** utilizado para simular a passagem das peças na esteira. A variação da luminosidade permite realizar a contagem de peças e detectar micro-paradas.
* **Botão (Push Button):** utilizado para realizar o reset manual do turno, zerando os contadores e reiniciando o estado do sistema.
* **Monitor Serial:** exibe as mensagens de inicialização, contagem de peças, alerta de micro-parada e confirmação do reset.

## Decisões Técnicas Relevantes

O código foi organizado com constantes no início, facilitando a alteração de pinos, limites do sensor e tempos de espera. Também foram utilizados estados, como `sensor_bloqueado` e `alerta_emitido`, para evitar contagens ou alertas repetidos.

A temporização foi feita com `ticks_ms()` e `ticks_diff()`, permitindo medir o tempo de bloqueio do sensor sem interromper o funcionamento do programa. Para o botão, foi aplicado um controle simples de debounce, evitando múltiplos resets causados por uma única pressão.

Resultados Obtidos

O sistema funcionou corretamente durante a simulação no Wokwi, realizando a contagem de peças por meio do sensor LDR, detectando micro-paradas quando o sensor permaneceu bloqueado por mais de cinco segundos e executando o reset do turno através do botão.

Todos os requisitos propostos foram atendidos, incluindo os três cenários de teste automatizados. As simulações apresentaram o comportamento esperado, com as mensagens sendo exibidas corretamente no monitor serial e todos os testes da GitHub Actions concluídos com sucesso.

Comentários Adicionais

Durante o desenvolvimento, a principal dificuldade foi compreender o funcionamento da simulação no Wokwi e ajustar o código para atender corretamente aos testes automatizados. Também foi necessário validar os valores do sensor de luminosidade para garantir o comportamento esperado.