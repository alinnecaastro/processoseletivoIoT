from machine import ADC, Pin
from time import sleep_ms, ticks_ms, ticks_diff


PINO_LDR = 34
PINO_BOTAO = 27

LIMITE_LUZ_BAIXA = 100
LIMITE_LUZ_ALTA = 500

TEMPO_MICRO_PARADA_MS = 5000
DEBOUNCE_BOTAO_MS = 50


ldr = ADC(Pin(PINO_LDR))
ldr.atten(ADC.ATTN_11DB)

botao = Pin(PINO_BOTAO, Pin.IN, Pin.PULL_UP)


total_pecas = 0
sensor_bloqueado = False
inicio_bloqueio = 0
alerta_micro_parada_emitido = False

ultimo_estado_botao = botao.value()
ultima_mudanca_botao = ticks_ms()


def ler_luminosidade():
    """
    Converte aproximadamente a leitura analógica para uma escala
    compatível com os valores de lux usados nos testes do Wokwi.
    """
    leitura = ldr.read()

    # No sensor do Wokwi, mais luz normalmente gera leitura analógica menor.
    # Esta conversão aproxima o valor para uma faixa de 0 a 1000.
    lux_aproximado = int((4095 - leitura) * 1000 / 4095)

    return lux_aproximado


def resetar_turno():
    global total_pecas
    global sensor_bloqueado
    global inicio_bloqueio
    global alerta_micro_parada_emitido

    total_pecas = 0
    sensor_bloqueado = False
    inicio_bloqueio = 0
    alerta_micro_parada_emitido = False

    print("Turno resetado com sucesso. Contadores zerados.")


print("Contador de Producao Inicializado")


while True:
    agora = ticks_ms()
    luminosidade = ler_luminosidade()

    # Detecta o início do bloqueio da luz.
    if luminosidade < LIMITE_LUZ_BAIXA and not sensor_bloqueado:
        sensor_bloqueado = True
        inicio_bloqueio = agora
        alerta_micro_parada_emitido = False

    # Detecta micro-parada após 5 segundos de bloqueio.
    if sensor_bloqueado and not alerta_micro_parada_emitido:
        tempo_bloqueado = ticks_diff(agora, inicio_bloqueio)

        if tempo_bloqueado >= TEMPO_MICRO_PARADA_MS:
            print("Alerta: Micro-parada detectada!")
            alerta_micro_parada_emitido = True

    # A peça só é contabilizada quando a luz volta ao normal.
    if luminosidade > LIMITE_LUZ_ALTA and sensor_bloqueado:
        total_pecas += 1
        sensor_bloqueado = False
        inicio_bloqueio = 0
        alerta_micro_parada_emitido = False

        print("Peca detectada! Total:", total_pecas)

    # Debounce do botão de reset.
    estado_botao = botao.value()

    if estado_botao != ultimo_estado_botao:
        ultima_mudanca_botao = agora
        ultimo_estado_botao = estado_botao

    if ticks_diff(agora, ultima_mudanca_botao) >= DEBOUNCE_BOTAO_MS:
        if estado_botao == 0:
            resetar_turno()

            # Aguarda a liberação do botão sem bloquear o restante do sistema
            # por um tempo excessivo.
            while botao.value() == 0:
                sleep_ms(10)

            ultimo_estado_botao = botao.value()
            ultima_mudanca_botao = ticks_ms()

    sleep_ms(20)