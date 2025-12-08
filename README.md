# Spotify Agent -- Guía de Ejecución

Este proyecto requiere una autenticación inicial con Spotify para poder
funcionar correctamente.\
Sigue los pasos detallados a continuación.

------------------------------------------------------------------------

## 🚀 Primer inicio: Autenticación con Spotify

0.  Borrar archivo `.cache-spotify` si existe.


1.  Ejecuta el script principal:

    ``` bash
    python spotify_agent.py
    ```

2.  La primera vez aparecerá un mensaje similar a:

        Please navigate here:
        https://accounts.spotify.com/authorize?client_id=...&response_type=code...

    👉 **Copia esa URL y ábrela en tu navegador.**

3.  Inicia sesión en Spotify y acepta los permisos.\
    Serás redirigido a una URL como:

        http://127.0.0.1:8888/callback?code=AQB4h7...

4.  **Copia el valor del parámetro `code`** de esa URL.

5.  Vuelve a la terminal y ejecuta de nuevo:

    ``` bash
    python spotify_agent.py
    ```

------------------------------------------------------------------------

## ▶️ Ejecución del programa principal

En otra terminal, lanza:

``` bash
python main.py
```

## ▶️ Ejecución del panel web

En otra terminal, lanza:

``` bash
python api/device_panel.py
```

------------------------------------------------------------------------

## ✔️ ¡Listo!

Una vez autenticado por primera vez, el agente podrá interactuar con
Spotify automáticamente usando las credenciales generadas.

# FLUJO DE EJECUCIÓN

1. El agente escucha por MQTT los eventos de los intents con la funcion `on_text_detected`.
2. Si el intent es reconocido, se llama a la funcion `match_intent` que consulta los patterns y devuelve el intent y los slots.
3. Se llama a la funcion `handle` que ejecuta la accion correspondiente.
4. La accion publica un evento MQTT que es escuchado por el agente de Spotify o el que le corresponde.


## COMO AÑADIR UN NUEVO INTENT

1. Añade una nueva entrada en el array `_PATTERNS` en el archivo `intents.py`.
2. En  el archivo actions.py define una nueva función que implemente el intent y publique el evento MQTT correspondiente.
3. El agente de Spotify o el que le corresponde se encarga de ejecutar la accion porque se habra suscrito a los eventos MQTT que publica `actions.py`.