 import streamlit as st

   def user_data_input():
       if "start_time" not in st.session_state:
           st.session_state.start_time = None
       
       example_input = st.text_input("Enter something:")
       
       if example_input:
           st.session_state.start_time = example_input
           st.experimental_rerun()

   def main():
       st.title("Prueba de Rerun")
       user_data_input()

   if __name__ == "__main__":
       main()
