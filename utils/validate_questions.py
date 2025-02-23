import pandas as pd
import streamlit as st

def validate_selection(selected_questions, total_questions):
    # Contar preguntas por clasificación
    classification_count = {}
    for question in selected_questions:
        classification = question['clasificacion']
        if classification not in classification_count:
            classification_count[classification] = 0
        classification_count[classification] += 1
    
    # Crear un DataFrame para mostrar los resultados
    data = []
    for classification, count in classification_count.items():
        percentage = (count / total_questions) * 100
        data.append({"Clasificación": classification, "Número de Preguntas": count, "Porcentaje": f"{percentage:.2f}%"})
    
    df = pd.DataFrame(data)
    
    # Mostrar la tabla en Streamlit
    st.write("Distribución de preguntas seleccionadas:")
    st.table(df)
