from datetime import datetime

def get_current_datetime():
    """
    Retorna que dia é hoje e que horas são. Use para se manter atualizado sobre o horário atual.
    """
    
    current_time = datetime.now()
    
    week_day = [
        "Segunda-feira",
        "Terça-feira",
        "Quarta-feira",
        "Quinta-feira",
        "Sexta-feira",
        "Sábado",
        "Domingo"
    ]
    
    print(f"{week_day[current_time.weekday()]}, {current_time.strftime('%d/%m/%Y ás %H:%M')}")
    
    return f"{week_day[current_time.weekday()]}, {current_time.strftime('%d/%m/%Y ás %H:%M')}"