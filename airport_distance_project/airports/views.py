from django.shortcuts import render
import requests

def airport_distance_view(request):

    context = {}

    if request.method == "POST":

        aeropuerto_origen  = request.POST.get("aeropuerto_origen", "").strip().upper()
        aeropuerto_destino = request.POST.get("aeropuerto_destino", "").strip().upper()

        context["aeropuerto_origen"]  = aeropuerto_origen
        context["aeropuerto_destino"] = aeropuerto_destino

        # VALIDAR LOS DATOS ANTES DE LLAMAR A LA API

        # Validar que ambos campos estén llenos
        if not aeropuerto_origen or not aeropuerto_destino:
            context["error"] = "Debe ingresar ambos códigos de aeropuerto."

        # Validar que los códigos tengan 3 caracteres
        elif len(aeropuerto_origen) != 3 or len(aeropuerto_destino) != 3:
            context["error"] = "Los códigos IATA deben tener exactamente 3 letras."

        # Validar que los códigos contengan solo letras (no números ni símbolos)
        elif not aeropuerto_origen.isalpha() or not aeropuerto_destino.isalpha():
            context["error"] = "Los códigos IATA deben contener solo letras (sin números ni símbolos)."

        # Validar que los aeropuertos no sean iguales
        elif aeropuerto_origen == aeropuerto_destino:
            context["error"] = "El aeropuerto de origen y el de destino no pueden ser el mismo."

        else:
            # LLAMAR A LA API EXTERNA AIRPORTGAP
            try:
                # URL de la API
                base_url = "https://airportgap.com/api/airports/distance"

                # Realizar la petición POST
                response = requests.post(base_url, json={"from": aeropuerto_origen, "to": aeropuerto_destino}, timeout=10)

                # PROCESAR LA RESPUESTA DE LA API
                if response.status_code == 200:
                    datos = response.json()

                    atributos = datos["data"]["attributes"]

                    # Construimos el diccionario "resultado" con los datos que queremos mostrar en el template
                    context["resultado"] = {
                        "aeropuerto_origen": {
                            "codigo":  aeropuerto_origen,
                            "nombre":  atributos["from_airport"]["name"],
                            "ciudad":  atributos["from_airport"]["city"],
                            "pais":    atributos["from_airport"]["country"],
                        },
                        "aeropuerto_destino": {
                            "codigo":  aeropuerto_destino,
                            "nombre":  atributos["to_airport"]["name"],
                            "ciudad":  atributos["to_airport"]["city"],
                            "pais":    atributos["to_airport"]["country"],
                        },
                        "distancia_km":            atributos["kilometers"],
                        "distancia_millas":        atributos["miles"],
                        "distancia_millas_nauticas": atributos["nautical_miles"],
                    }

                elif response.status_code == 422:
                    # 422 significa que la API recibió la petición pero no pudo procesarla
                    # porque los códigos IATA no son válidos (no existen en su base de datos)
                    context["error"] = "Uno o ambos códigos IATA no son válidos. Verifique e intente nuevamente."

                else:
                    # Cualquier otro código inesperado (500, 503, etc.)
                    context["error"] = f"Error en la API externa. Código de respuesta: {response.status_code}"

            except requests.exceptions.Timeout:
                # La API no respondió dentro de los 10 segundos configurados
                context["error"] = "Tiempo de espera agotado. La API tardó demasiado. Intente nuevamente."

            except requests.exceptions.ConnectionError:
                # No se pudo establecer conexión (sin internet, DNS fallido, etc.)
                context["error"] = "Error de conexión. Verifique su conexión a internet e intente nuevamente."

            except Exception as e:
                # Captura cualquier otro error inesperado (error en el JSON, etc.)
                context["error"] = f"Error inesperado: {str(e)}"

    # RENDERIZAR EL TEMPLATE CON EL CONTEXTO
    return render(request, "airport_distance.html", context)