# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd 

# st.warning("⏸️ Приложение временно остановлено.")
# st.stop()

# Write directly to the app
st.title(f":cup_with_straw: Customize your smoothie :cup_with_straw: {st.__version__}")
st.write(
  """Choose the fruit you want in your custom Smoothie!
  """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# cnx = st.connection("snowflake")
# session = cnx.session()

try:
    cnx = st.connection("snowflake", type="snowflake")
    session = cnx.session()
except Exception as e:
    st.error("❌ Не удалось подключиться к Snowflake.")
    st.write(f"Ошибка: {e}")
    st.stop()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'),col('search_on'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

# Convert the Snowpark Dataframe to Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()


ingredients_list=st.multiselect(
    "Choose up to five ingredients:",
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    # st.write(ingredients_list)
    # st.text(ingredients_list)
    ingredients_string=''
    for fruit_chosen in ingredients_list:
        ingredients_string+=fruit_chosen
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
        sf_df=st.dataframe(data=smoothiefroot_response.json(),width='stretch')

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    # st.write(my_insert_stmt)
    # st.stop()
    time_to_insert=st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


