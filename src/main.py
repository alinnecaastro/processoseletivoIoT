from machine import ADC, Pin
from time import sleep_ms, ticks_ms, ticks_diff


# Configuração do LDR
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)


# Limites observados no Wokwi:
# 800 lux gera aproximadamente 773 no ADC
# 50 lux gera aproximadamente 2531 no ADC
LIMITE_BLOQUEADO = 2000
LIMITE_LIVRE = 1000

# Tempo necessário para considerar micro-parada
TEMPO_MICRO_PARADA_MS = 5000


contador = 0
sensor_bloqueado = False

tempo_inicio_bloqueio = 0
alerta_emitido = False


print("Contador de Producao Inicializado")


while True:
    valor = ldr.read()

    # A peça entrou e bloqueou a luz
    if valor > LIMITE_BLOQUEADO:

        # Executa somente no momento em que o bloqueio começa
        if not sensor_bloqueado:
            sensor_bloqueado = True
            tempo_inicio_bloqueio = ticks_ms()
            alerta_emitido = False

        # Verifica se a peça ficou parada por 5 segundos
        tempo_bloqueado = ticks_diff(
            ticks_ms(),
            tempo_inicio_bloqueio
        )

        if (
            tempo_bloqueado >= TEMPO_MICRO_PARADA_MS
            and not alerta_emitido
        ):
            print("Alerta: Micro-parada detectada!")
            alerta_emitido = True

    # A peça saiu e a luz voltou
    elif valor < LIMITE_LIVRE and sensor_bloqueado:
        contador += 1
        sensor_bloqueado = False
        alerta_emitido = False

        print(f"Peca detectada! Total: {contador}")

    sleep_ms(20)