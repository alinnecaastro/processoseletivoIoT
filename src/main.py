from machine import ADC, Pin
from time import sleep_ms, ticks_ms, ticks_diff


# ---------------------------------------------------------
# Configuração dos pinos
# ---------------------------------------------------------

PINO_LDR = 34
PINO_BOTAO_RESET = 27

ldr = ADC(Pin(PINO_LDR))
ldr.atten(ADC.ATTN_11DB)

# Botão ligado entre o GPIO 27 e o GND:
# solto = 1
# pressionado = 0
botao_reset = Pin(
    PINO_BOTAO_RESET,
    Pin.IN,
    Pin.PULL_UP
)


# ---------------------------------------------------------
# Configurações
# ---------------------------------------------------------

LIMITE_BLOQUEADO = 2000
LIMITE_LIVRE = 1000

TEMPO_MICRO_PARADA_MS = 5000
TEMPO_DEBOUNCE_MS = 50


# ---------------------------------------------------------
# Variáveis
# ---------------------------------------------------------

contador = 0

sensor_bloqueado = False
tempo_inicio_bloqueio = 0
alerta_emitido = False

botao_foi_pressionado = False
tempo_pressao_botao = 0


print("Contador de Producao Inicializado")


# ---------------------------------------------------------
# Loop principal
# ---------------------------------------------------------

while True:
    agora = ticks_ms()

    valor_ldr = ldr.read()
    estado_botao = botao_reset.value()

    # -----------------------------------------------------
    # Cenários 1 e 2: leitura do sensor
    # -----------------------------------------------------

    if valor_ldr > LIMITE_BLOQUEADO:

        if not sensor_bloqueado:
            sensor_bloqueado = True
            tempo_inicio_bloqueio = agora
            alerta_emitido = False

        tempo_bloqueado = ticks_diff(
            agora,
            tempo_inicio_bloqueio
        )

        if (
            tempo_bloqueado >= TEMPO_MICRO_PARADA_MS
            and not alerta_emitido
        ):
            print("Alerta: Micro-parada detectada!")
            alerta_emitido = True

    elif valor_ldr < LIMITE_LIVRE and sensor_bloqueado:

        contador += 1

        sensor_bloqueado = False
        tempo_inicio_bloqueio = 0
        alerta_emitido = False

        print("Peca detectada! Total:", contador)

    # -----------------------------------------------------
    # Cenário 3: reset manual
    # -----------------------------------------------------

    # Detecta quando o botão foi pressionado
    if estado_botao == 0 and not botao_foi_pressionado:
        botao_foi_pressionado = True
        tempo_pressao_botao = agora

    # Executa o reset quando o botão for solto
    elif estado_botao == 1 and botao_foi_pressionado:

        tempo_pressionado = ticks_diff(
            agora,
            tempo_pressao_botao
        )

        # Ignora ruídos ou toques muito rápidos
        if tempo_pressionado >= TEMPO_DEBOUNCE_MS:

            contador = 0

            sensor_bloqueado = False
            tempo_inicio_bloqueio = 0
            alerta_emitido = False

            print(
                "Turno resetado com sucesso. Contadores zerados."
            )

        botao_foi_pressionado = False

    sleep_ms(20)