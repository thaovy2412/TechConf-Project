from datetime import datetime
import os
import psycopg2
import azure.functions as func
import logging

app = func.FunctionApp()


@app.service_bus_queue_trigger(arg_name="azservicebus", queue_name="notificationqueue",
                               connection="vytt1sb_SERVICEBUS")
def servicebus_queue_trigger(azservicebus: func.ServiceBusMessage):
    notification_id = int(azservicebus.get_body().decode('utf-8'))
    logging.info(
        'Python ServiceBus queue trigger processed message: %s', notification_id)

    # TODO: Get connection to database
    connection = psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PWD"]
    )
    cursor = connection.cursor()
    try:
        # TODO: Get notification message and subject from database using the notification_id
        select_notification_query = "SELECT message, subject FROM notification WHERE id = %s"
        cursor.execute(select_notification_query, [notification_id])
        notification = cursor.fetchone()
        connection.commit()

        # TODO: Get attendees email and name
        select_attendees_query = "SELECT first_name, last_name, email FROM attendee"
        cursor.execute(select_attendees_query)
        attendees = cursor.fetchall()
        connection.commit()

        # TODO: Loop through each attendee and send an email with a personalized subject
        # REASON: I tried to register a SendGrid Account to do the send notification function. However, I always get the error at the login step at all attempts (attached a screenshot in the Evidences/Exception folder). I also had the idea to switch to another service like Gmail but it needs to access Google Cloud to get the API key. I can start on the free trial for this service, and a credit or debit card is required but I don't have it. But I'm sure I can do this function/task for sending emails if I have all the conditions.

        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        update_notification_query = """UPDATE notification SET completed_date = %s, status = %s WHERE id = %s"""
        cursor.execute(update_notification_query, (datetime.utcnow(
        ), 'Notified {} attendees'.format(len(attendees)), notification_id))
        connection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        cursor.close()
        connection.close
