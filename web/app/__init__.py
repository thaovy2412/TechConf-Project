import os
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from azure.servicebus import ServiceBusClient


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

app.secret_key = app.config.get('SECRET_KEY')

service_bus_client = ServiceBusClient.from_connection_string(
    app.config.get('SERVICE_BUS_CONNECTION_STRING'))

queue_client = service_bus_client.get_queue_sender(
    app.config.get('SERVICE_BUS_QUEUE_NAME'))

db = SQLAlchemy(app)

from . import routes