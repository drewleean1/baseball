from flask import Flask, render_template, json, redirect, current_app
from flask import request
from flask_mysqldb import MySQL
import os
import psycopg2


app = Flask(__name__)
app.secret_key = 'super secret key'

# Set secret key for session management necessary for flashing messages
db = psycopg2.connect("dbname='d8su3fb57frup7' user='ua795rtba736ua' host='c9pbiquf6p6pfn.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com' port='5432' password='p02e624ad0babd80df2cdb4357ac18f150eb1bee6b9598913ab7511501a3d1653'")
    
from views import views
app.register_blueprint(views, url_prefix='/')



if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)






"""
        Much of the bootstrap framework was sourced from a video from Tech With Tim 
        As well as the Bootstrap website.
        https://www.youtube.com/watch?v=dam0GPOAvVI&t=369s

"""
