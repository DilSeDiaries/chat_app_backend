import traceback
import pandas as pd
from DBConnection import DBConnection
import json
import os
DBConnection = DBConnection()
import ast  # Import the ast module for literal evaluation


class MethodCalls:
    def __init__(self):
        self.DBConnection = DBConnection

    def createUser(self,name,email):
        conn = None
        try:

            conn = self.DBConnection.init_db()
            cursor = conn.cursor()
            # cursor.execute('''
            #         CREATE TABLE IF NOT EXISTS users (
            #             id INTEGER PRIMARY KEY AUTOINCREMENT,
            #             name TEXT NOT NULL,
            #             email TEXT NOT NULL
            #         )
            #     ''')
            sql_user_valid = f"""select * from users where name='{name}' and email='{email}';"""
            sql_user_valid_df = pd.read_sql(sql_user_valid,conn)
            if len(sql_user_valid_df)>0:
                return {
                    'status': False,
                    'msg': 'User is already exist'
                }
            cursor.execute('INSERT INTO users (name, email) VALUES (?, ?)', (name, email))
            conn.commit()
            # df = pd.read_sql("select * from users",conn)
            # print(df)
            return {
                'status':True,
                'msg':'User is created Successfully'
            }
        except Exception as ex:
            print(traceback.print_exc())
            return {
                'status': False,
                'msg': f'{str(traceback.print_exc())}'
            }
        finally:
            if conn:
                conn.close()

    def loginUser(self,name,email):
        conn = None
        try:
            conn = self.DBConnection.init_db()
            user_validation = f"""select * from users where name='{name}' and email='{email}'"""
            user_validation_df = pd.read_sql(user_validation,conn)
            print(user_validation_df)
            if len(user_validation_df)>0:
                return {
                    'msg':'valid user!',
                    'status':True
                    }
            else:
                return {
                    'msg': 'No user with given name!',
                    'status': False
                }
        except Exception as ex:
            print(traceback.print_exc())
            print(str(ex))
            return {
                'status': False,
                'msg': f'{str(traceback.print_exc())}'
            }
        finally:
            if conn:
                conn.close()

    def createPost(self,data,image,name,email):
        conn = None
        try:
            conn = self.DBConnection.init_db()
            data = json.loads(data)
            cursor = conn.cursor()
            sql_data = f"""INSERT INTO post (name, email, data)
                           VALUES ('{name}','{email}' ,"{data}" );"""
            print("sql_data",sql_data)
            cursor.execute(sql_data)
            inserted_id = cursor.lastrowid
            conn.commit()
            UPLOAD_FOLDER = 'Images'
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            subfolder = os.path.join(UPLOAD_FOLDER, f'{inserted_id}')
            os.makedirs(subfolder, exist_ok=True)
            for file in image:
                save_path = os.path.join(subfolder, file.filename)
                file.save(save_path)
            return {
                'status':True,
                'msg':'post created successfully'
            }
        except Exception as ex:
            print(traceback.print_exc())
            print(str(ex))
            return {
                'status': False,
                'msg': f'{str(traceback.print_exc())}'
            }
        finally:
            if conn:
                conn.close()
    def getAllPost(self):
        try:
            def convert_to_dict(column_value):
                try:
                    return ast.literal_eval(column_value)
                except Exception as e:
                    print(f"Error converting: {column_value}. Error: {e}")
                    return None

            db_conn = self.DBConnection.init_db()
            sql_posts = f"""select * from post"""
            df_posts = pd.read_sql(sql_posts,db_conn)
            df_posts["data"] = df_posts["data"].apply(convert_to_dict)
            df_posts['like_by'] = df_posts["like_by"].apply(convert_to_dict)


            sql_posts_comm = f"""select * from post_comment"""
            df_posts_comm = pd.read_sql(sql_posts_comm, db_conn)

            grouped = (
                df_posts_comm.groupby('post_id')
                .apply(lambda x: x[['comment_by', 'comment_context']].to_dict(orient='records'))
                .reset_index(name='comments')
            )

            merged_df = pd.merge(df_posts, grouped, on='post_id', how='left')
            merged_df = merged_df.fillna({'comments': ''})
            merged_df['comment_status'] = False
            merged_df = merged_df.to_dict(orient='records')
            return {
                'status':True,
                'data': merged_df
            }
            # df_posts = df_posts.to_dict(orient='records')
            #
            # return {
            #     'status':True,
            #     'data': df_posts
            # }
        except Exception as ex:
            print(traceback.print_exc())




    def DBConnectionChanges(self):
        conn = None
        try:
            conn = self.DBConnection.init_db()
            # sql = f"""drop table post"""
            # sql = f"""
            #     CREATE TABLE post (
            #     post_id INTEGER PRIMARY KEY AUTOINCREMENT,
            #     name VARCHAR(100) NOT NULL,
            #     email VARCHAR(100) NOT NULL,
            #     data JSON NOT NULL,
            #     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
            #        """
            # cursor = conn.cursor()
            # cursor.execute(sql)
            # conn.commit()
            # sql = f"""select * from post"""
            # data = pd.read_sql(sql,conn)
            # print(data['post_id'])
        except Exception as ex:
           print(traceback.print_exc())
        finally:
           if conn:
               conn.close()
    def likePostCall(self,post_id,name):
        conn = None
        try:
            conn = self.DBConnection.init_db()
            cursor = conn.cursor()

            # Fetch the current 'like_by' JSON column
            cursor.execute("SELECT like_by FROM post WHERE post_id = ?", (post_id,))
            row = cursor.fetchone()

            if row:
                # Load the existing JSON array into a Python list
                like_by = json.loads(row[0]) if row[0] else []

                # Append the new name to the list
                like_by.append(name)

                # Convert the Python list back to a JSON string
                updated_like_by = json.dumps(like_by)

                # Update the 'like_by' column with the new JSON array
                cursor.execute("""
                    UPDATE post
                    SET like_by = ?
                    WHERE post_id = ?
                """, (updated_like_by, post_id))

                # Commit the changes
                conn.commit()
            return {
                'status': True,
                'msg': 'Successfully saved!'
            }
        except Exception as ex:
            print(traceback.print_exc())
            return {
                'status': False,
                'msg': str(traceback.print_exc())
            }
        finally:
            if conn:
                conn.close()

    def commentsPost(self,post_id, name, comment_context):
        conn = None
        try:
            conn = self.DBConnection.init_db()
            cursor = conn.cursor()
            sql_query = f"""INSERT INTO post_comment (post_id, comment_by, comment_context)
                           VALUES ('{post_id}','{name}' ,"{comment_context}" );"""
            cursor.execute(sql_query)
            conn.commit()
            return {
                'status':True,
                'msg':'comment successfully saved'
            }
        except Exception as ex:
            print(traceback.print_exc())
        finally:
            if conn:
                conn.close()

    def updateProfileCall(self,email,name,new_name):
        conn = None
        try:
            conn = self.DBConnection.init_db()
            cursor = conn.cursor()
            sql_query = f"""UPDATE users SET name = '{new_name}' where name = '{name}' and email='{email}' and name!='{new_name}'"""
            print(sql_query)
            cursor.execute(sql_query)
            conn.commit()
            if cursor.rowcount > 0:
                return {
                    'status': True,
                    'msg': 'Profile successfully saved'
                }
            else:
                return {
                    'status': False,
                    'msg': 'No matching record found to update'
                }
        except Exception as ex:
            print(traceback.print_exc())
            return {
                'status': False,
                'msg': str(traceback.print_exc())
            }
        finally:
            if conn:
                conn.close()






if __name__ == "__main__":
    MethodCalls = MethodCalls()
    MethodCalls.DBConnectionChanges()
    # MethodCalls.createUser('sumit','sumit@gmail.com')
