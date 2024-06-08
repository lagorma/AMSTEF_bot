from config import host, db_name, user, password
import psycopg2


connection = None

try:
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )

    connection.autocommit = True

    # cursor = connection.cursor()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT version();"
        )

        print(f"Server version: {cursor.fetchone()}")

    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE roles(
                role_ID serial PRIMARY KEY,
                name varchar(50) NOT NULL);"""
        )

        cursor.execute(
            """CREATE TABLE access_code(
                customer_ID serial PRIMARY KEY,
                code varchar(50) NOT NULL,
                valid_from TIMESTAMP NOT NULL,
                valid_to TIMESTAMP NOT NULL);"""
        )

        cursor.execute(
            """CREATE TABLE users(
                customer_ID serial PRIMARY KEY,
                name varchar(50) NOT NULL,
                phone_number varchar(15) NOT NULL,
                company_ID serial NOT NULL,
                position varchar(30) NOT NULL,
                deleted_flag BOOLEAN NOT NULL,
                role_ID serial NOT NULL,
                created_dttm TIMESTAMP NOT NULL,
                telegram_ID varchar(20) NOT NULL);"""
        )

        cursor.execute(
            """CREATE TABLE company(
                company_ID serial PRIMARY KEY,
                name varchar(50) NOT NULL,
                inn varchar(50) NOT NULL,
                deleted_flag BOOLEAN NOT NULL,
                created_dttm TIMESTAMP NOT NULL);"""
        )

        cursor.execute(
            """CREATE TABLE test_answer(
                answer_ID serial PRIMARY KEY,
                question_ID serial NOT NULL,
                customer_ID serial NOT NULL,
                created_dttm TIMESTAMP NOT NULL,
                answer_option varchar(20) NOT NULL);"""
        )

        cursor.execute(
            """CREATE TABLE test_question(
                question_ID serial PRIMARY KEY,
                test_type_ID serial NOT NULL,
                question_text varchar(200) NOT NULL,
                created_dttm TIMESTAMP NOT NULL,
                option_ID serial NOT NULL);"""
        )

        cursor.execute(
            """CREATE TABLE options(
                ID serial PRIMARY KEY,
                option_ID serial NOT NULL,
                answer_option varchar(20) NOT NULL,
                answer_text varchar(200) NOT NULL);"""
        )

        cursor.execute(
            """CREATE TABLE test_type(
                test_type_ID serial PRIMARY KEY,
                test_type_name varchar(200) NOT NULL);"""
        )

        cursor.execute(
            """CREATE TABLE message_hist(
                message_ID serial PRIMARY KEY,
                text_message varchar(200) NOT NULL,
                user_ID serial NOT NULL,
                created_dttm TIMESTAMP NOT NULL,
                deleted_flag BOOLEAN NOT NULL,
                author_ID serial NOT NULL);"""
        )

    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         """INSERT INTO Role_dict (name) VALUES ('админ')"""
    #     )
        print("Good")

except Exception as e:
    print("[INFO] Error", e)
finally:
    if connection:
        connection.close()
