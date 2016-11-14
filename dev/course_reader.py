#Nathan Nayda - ntn4jg@virginia.edu
import psycopg2
import csv

PG_USER = "postgres"
PG_USER_PASS = "jfkdls;a"
PG_HOST_INFO = "" # use "" for OS X or Windows





def load_course_database(db_name,csv_filename):
    with open(csv_filename, 'rU') as csvfile:
        # Connect to an existing database
        conn = psycopg2.connect("dbname=" + db_name + " user=" + PG_USER + " password=" + PG_USER_PASS + PG_HOST_INFO)
        # Open a cursor to perform database operations
        cur = conn.cursor()
        reader = csv.reader(csvfile)
        for row in reader:
            cur.execute("INSERT INTO coursedata (deptid,coursenum,semester,meetingtype,seatstaken,seatsoffered,instructor) VALUES (%s, %s,%s,%s,%s,%s,%s)", tuple(row))
            # Make the changes to the database persistent
            conn.commit()
        # Close communication with the database
        cur.close()
        conn.close()


load_course_database("course1","seas-courses-5years.csv")