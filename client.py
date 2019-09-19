# Name: Manohar Rajaram
# Student ID: 1001544414

# Code References
# 1. https://medium.com/swlh/lets-write-a-chat-app-in-python-f6783a9ac170
# 2. https://stackoverflow.com/questions/225086/rfc-1123-date-representation-in-python
# 3. https://www.jmarshall.com/easy/http/

from email.utils import formatdate      #required for formating date & time
from datetime import datetime           #required to get current datetime for HTTP
from time import mktime                 #required for timestamp with zone
import tkinter                          #required for GUI
from tkinter import messagebox          #required for alert box
from socket import AF_INET, socket, SOCK_STREAM     #required for socket programming
from threading import Thread            #required for multitherading

def parseHTTPresponse(Httpmsg):
# Description
    # The function parses the incoming HTTP response message from server
    # and returns the payload;
# Input:
#     Httpmsg-> HTTP encoded response message
# Output:
#     status-> HTTP response message status
#     query-> parsed payload in dictonary format

    crlf = "\r\n"           # Carriage return & Line feed for HTTP request message
    status = 0              # Status of HTTP response message initialize
    query = {}              # dictionary to hold the payload of the HTTP response
    ss = Httpmsg.split(crlf)    # split the message based on the CRLF and store into a list
    first_line = ss[0].split(" ")       # read the first line of the HTTP response (to get status)
    try:
        if first_line[1] == '200':      # if the status is 200 (OK)
            status = 200                # store the status to return

            # split the last line of payload based on delimiter && to
            # fetch all elements of the payload and store into a list
            # Ex: payload may contain: name=john&&message=hello
            # so payload will have => [name=john, message=hello]
            payload = ss[len(ss) - 1].split("&&")

            # split each element of the list payload based on '='
            # from the above example, the below dictionary query will have
            # query={'name':'john','message':'hello'}
            # Please note that if the original message contains =, blank will be sent
            for item in payload:
                left,right = item.split("=")       # split based on '='
                query.update({left:right})         # add new pair to dictionary
        else:
            status = 400        # update status (400= Bad request
    except IndexError:          # Check for Index error
        pass;                   # This exception wont occur since HTTP message is coded by us

    return status,query         # return the status and dictionary payload

def encodeHTTP(method,query):
# Description:
    # Given a dictionary of values and HTTP method(GET or POST),
    # this function encodes the query into HTTP request
# Input:
#    method-> HTTP method (POST or GET)
#    query-> dictioanry pairs of data to be sent to the server
# Output
#    HTTPmsg-> HTTP encoded message
    space = " "                     # space to delimit HTTP request
    url = "/"                       # start of the url (for POST its empty)
    host1 = "127.0.0.1:5001"        # host address (here its localhost)
    version = "HTTP/1.1"            #HTTP version
    crlf = "\r\n"                   #carriage return and line feed used for line seperator for http request
    user_agent = "python-client 1.0"     # user agent, usign python client here
    content_type = "text/plain"     # content type is plain text (no file transfer supported)

    now = datetime.now()            # get current date and time
    stamp = mktime(now.timetuple()) # convert local time to seconds since the Epoch
    # formats the above time into HTTP timestamp format
    date =  (formatdate( timeval = stamp, localtime = False, usegmt = True ))

    payload=""          #initialize payload

    # the following code converts dictionary(query) into string format as follows:
    # query={'name':'john','message':'hello'}
    # payload will have => name=john&&message=hello
    for idx, item in enumerate(query):
        if idx < len(query) - 1:
            payload = payload+item+"="+query[item]+"&&"     #add && as delimiter
        else:
            payload = payload+item+"="+query[item]      #no need of delimiter && for last line

    content_len = len(payload)      # payload length
    if method == 'GET':             # if the method is GET,
        url = url+'?'+payload       # store payload in URL

    # concatenate all HTTP headers stored above
    HTTPmsg = method + space + url + space + version + crlf
    HTTPmsg = HTTPmsg + "Host: " + host1 + crlf
    HTTPmsg = HTTPmsg + "User-Agent: " + user_agent + crlf
    HTTPmsg = HTTPmsg + "Content-Type: " + content_type + crlf
    if method == 'GET':
        # Content length is zero for GET request
        HTTPmsg = HTTPmsg + "Content-Length: " + "0" + crlf
    else:
        # payload length is the content length for POST request
        HTTPmsg = HTTPmsg + "Content-Length: " + str(content_len) + crlf
    HTTPmsg = HTTPmsg + "Date: " + date + crlf + crlf
    if method == 'POST':                #if payload is POST
        HTTPmsg = HTTPmsg + payload     # store the payload in HTTP body
    return HTTPmsg                      # return the HTTP encoded message


def receive():
# Description:
#     This function is called as new thread which cotinously listens to server
#     and receives messaged from it untill either server quits or client quits.
#     Here, the HTTP response from the server can be any of the following:
#     1. 'Invalid client selected' message from the server
#     2. List of active clients stored in the server
#     3. Server disconnection notification
#     4. Message, delivery preference and destination of the message
#     5. Client disconnection acknowledgment from server
#     Based on the above criteria, suitable actions are taken.
# Input: NA
# Output: NA
    while True:         # continously receive data from server
        try:        # 1. 'Invalid client selected' message from the server
            msg = sock.recv(buffer).decode("utf8")      #receive HTTP response from server
            status,payload = parseHTTPresponse(msg)     # parse the HTTP response message
            if status == 400:       # in this program, server response will be 400(Bad request)
                                    # if user selects invalid client

            # display the same message
                msg_list.insert(tkinter.END, "Invalid client selected")
                msg_list.see(tkinter.END)
            # display prompt for new message entry
                msg_list.insert(tkinter.END, "Enter new message:")
                msg_list.see(tkinter.END)   # scroll the display till the latest message
            else:
                try:    # 2. List of active clients stored in the server
                    if payload['clist']:
                        # display the list for client to select the destination client
                        msg_list.insert(tkinter.END,payload['clist'])
                        # scroll the display till the latest message
                        msg_list.see(tkinter.END)
                except KeyError:
                    try:        # 3. Server disconnection notification
                        if payload['serv_quit'] == 'True':
                            msg_list.insert(tkinter.END,"Server disconnected; Communication not possible!")
                            msg_list.see(tkinter.END)      #scroll to latest line
                            # disable input and send buttons on the client
                            send_button.config(state="disabled")
                            entry_field.config(state="disabled")
                    except KeyError:
                        try:    # 4. Message, delivery preference and destination of the message
                            if payload['delv'] == '1':
                                delv_pref = "1-1"   # delivery method 1-1
                            else:
                                delv_pref = "1-N"   # delivery method 1-N (broadcast)
                        # form the message to be displayed along with source of the message
                        # and delivery method
                            disp_msg = "["+delv_pref+"] "
                            disp_msg = disp_msg + "Message from "+payload['source']+": "
                            disp_msg = disp_msg + payload['message']
                        # display the messages
                            msg_list.insert(tkinter.END,disp_msg)
                            msg_list.see(tkinter.END)   # scroll the display till the latest message
                        # prompt for next message
                        except KeyError:
                            try:    # 5. Client disconnection acknowledgment from server
                                if payload['quit_ack'] == 'True':
                                    sock.close()    #close the client socket once acknowledged from server
                                    break
                            except KeyError:
                                break               #stop listening on any other Key error
        except OSError:  # Possible socket connection issue
            break

def send_msg(msg):
# Description:
#   Sends the message to the server
# Input:
#     msg-> HTTP Request message
# Output: NA
    try:
        sock.send(bytes(msg, "utf8"))   # send the message to server
    except ConnectionResetError:
        # This error occurs on server disconnection
        msg_list.insert(tkinter.END,"Server Disconnected")
        msg_list.see(tkinter.END)      #scrolls to the latest message

def send(event=None):
# Description:
    #This event handler is called on the click of submit button on the UI.
    # This function works on 4 different stages:
    # 1. stage=0: Getting name from the UI and parse into HTTP,
    #    and sending it to server; executes only once per client
    # 2. stage=1: Getting the message to be sent from the UI
    # 3. stage=2: Getting the delivery method (1-1 or 1-N) from the UI
    # 4. stage=3: If 1-1 is selected, get the destination client from UI
    #    and send the message, delivery method and destinaton to server
    # 5. stage=4: Notifying server that this client will be disconnected
# Input: NA
# Output: NA

    #declare global variables used here; these are declared global because we need to remember
    # the data accrss multiple calls to this event
    global stage, message, delv_method, dest

# 1. stage=0: Getting name from the UI and
# parse into HTTP, and sending it to server; executes only once per client
    if stage == 0:
        stage = 1             # set to next stage
        name = my_msg.get()   # read user input
        my_msg.set("")        # Clears input field.
        top.title(name)       # change the client window title
        HTTPmsg = encodeHTTP("POST",{'name':name})      #parse name into HTTP request
        send_msg(HTTPmsg)               # register the client name onto server
        msg_list.insert(tkinter.END,"Your name is stored in server as "+name+". You can send messages now.")       #display info to user
        msg_list.see(tkinter.END)
# 2. stage=1: Getting the message to be sent from the UI
    elif stage == 1:
        stage = 2                   # set to next stage
        message = my_msg.get()      # read user input
        my_msg.set("")              # Clears input field.

        # display prompt to select delivery method prefernce in the next stage=2
        msg_list.insert(tkinter.END, "Choose Delivery method")
        msg_list.insert(tkinter.END, "(1) 1-1 (2) 1-N ----> Enter 1 or 2: ")
        msg_list.see(tkinter.END)   # scroll to latest text
# 3. stage=2: Getting the delivery method (1-1 or 1-N) from the UI
    elif stage == 2:
        delv_method = my_msg.get()      # read user input
        my_msg.set("")                  # Clears input field.
        if delv_method == '1':          # if user has chosen 1-1 deliver method at stage 1
            stage = 3                   # set next stage to 3 (

            # encode and send HTTP request to server to fetch active clients list
            # to display to the user to select from
            HTTPmsg = encodeHTTP("GET",{'clients':'True'})
            send_msg(HTTPmsg)

            # display prompt to choose destination client
            msg_list.insert(tkinter.END, "Enter name of the Destination Client from the list below:")
            msg_list.see(tkinter.END)
        elif delv_method == '2':    # if delivery method is broadcast (1-N)
            stage = 1               # set next stage to 1(back to listening for new msg)

            # encode message and delivery prefernce into HTTP message
            HTTPmsg = encodeHTTP("POST",{'message':message,'delv':delv_method})
            send_msg(HTTPmsg)       #send the message to server for broadcast
            msg_list.insert(tkinter.END,"Your message '"+message+"' was broadcast; You can send next message")       #display info to user
            msg_list.see(tkinter.END)
        else:   # if user inputs anything other than 1 or 2 (1-1 or 1-N)
                #display error message
            msg_list.insert(tkinter.END, "Invalid input: ")
            msg_list.see(tkinter.END)
            stage = 2       #set the stage back to getting delivery method
            delv_method = ""    #clear delivery method entered
# 4. stage=3: If 1-1 is selected, get the destination client
# from UI and send the message, delivery method and destination to server
    elif stage == 3:
        stage = 1       # set the stage back to listening messages
        dest = my_msg.get()     # read the destination from UI
        my_msg.set("")          # Clears input field.
        # msg_list.insert(tkinter.END,"Enter your message")
        # encode message, delivery method preference and destination into HTTP request
        # the server then sends the message to the destination.
        HTTPmsg = encodeHTTP("POST",{'message':message,'delv':delv_method,'destination':dest})
        send_msg(HTTPmsg)       # send the request to server
        msg_list.insert(tkinter.END,"Your message '"+message+"' was sent to "+dest)       #display info to user
        msg_list.see(tkinter.END)
    # 5. stage=4: Notifying server that this client will be disconnected
    elif stage == 4:
        # encode the quit message into HTttp
        HTTPmsg = encodeHTTP("POST",{'quit':'True'})
        send_msg(HTTPmsg)   #send the request message
        top.quit()          # stop the main loop of tkinter GUI

def disconnect():
# Description:
#     Event handler called when user clicks on the 'Quit' button
# Input:NA
# Output:NA

# global variables declared to change the stage
    global stage
    stage = 4               # set the stage in the receive() method to 4
    send()                  # call the send() method to notify server abt the disconnection

def win_close(event=None):
# Description:
#     Event handler called on the closing of window
# Input: NA
# Output: NA
    global stage    # required to update the 'stage' of the receive() method
    stage = 4       # set the stage in the receive() method to 4
    send()          # call the send() method to notify server abt the disconnection
    top.quit()      # stop the main loop of tkinter GUI

if __name__ == "__main__":
# Description:
#     Execution starts from here; All globals are declared here;
#     The Tkinter GUI is initialized here
#     The concurrent thread for listening to server is also started here
# Input:
# Output:

    stage = 0           # initialize the stage variable; explained in detail above in receive() method
    message = ""        # global variable to store the user input message
    delv_method = ""    # delivery method preference of the user for a message
    dest = ""           # destination client for the message

    top = tkinter.Tk()      # create a root window handler
    top.title("Client")     # set the window titlw as client; updated once the user enters name
    messages_frame = tkinter.Frame(top)         #message frame to display text on the window

    my_msg = tkinter.StringVar()  # to set and get text from tkinter.Entry (input box)
    my_msg.set("")                # set it to blank at first

    scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
    # creates listbox to display the text entered by the user
    msg_list = tkinter.Listbox(messages_frame, height=15, width=70, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)      #set the scrol bar for first view

    # configure list box geometry
    msg_list.pack(side=tkinter.LEFT,expand=tkinter.YES, fill=tkinter.BOTH)
    msg_list.pack()

    # configures the frame geometry allowing it to expand
    messages_frame.pack(expand=tkinter.YES,fill=tkinter.BOTH)

    #Label for input box
    button_label = tkinter.Label(top, text="Enter Message:")
    button_label.pack()

    # Input box for user input: we can set the input and read value off it using
    # variable 'my_msg'; also the input font color is set to red
    entry_field = tkinter.Entry(top, textvariable=my_msg, foreground="Red")

    # calls the send() method on pressing enter
    entry_field.bind("<Return>", send)
    entry_field.pack()

    # button to send the message; calls send() method
    send_button = tkinter.Button(top, text="Send", command=send)
    send_button.pack()

    # button to quit; calls win
    quit_button = tkinter.Button(top, text="Quit", command=disconnect)
    quit_button.pack()

    # on closing the window; call the win_close() function
    top.protocol("WM_DELETE_WINDOW", win_close)

    # prompt to the user to register the client name on the server
    msg_list.insert(tkinter.END, "Enter your name:")
    msg_list.see(tkinter.END)       #srcoll tp the latest message


    host = "127.0.0.1"          # server IP address; here its localhost
    port = 5002                 # port number of the server (hardcoded)
    buffer = 1024               # buffer size
    addr = (host, port)         # IP address-port tuple
    sock = socket(AF_INET, SOCK_STREAM)     # creates a socket for TCP connection
    try:
        sock.connect(addr)                  # connects to the localhost server with its port
        # starts new thread to listen to the server for messages contnously
        receive_thread = Thread(target=receive)
        receive_thread.start()
        # start the GUI main loop
        tkinter.mainloop()
    except ConnectionRefusedError:      # if server connection failed
        top.destroy()                   # destroy the UI

        # display message that no server is active
        serv_msg = "Server not listening. Please run 'server.py' first and try again"
        tkinter.messagebox.showinfo("Message",serv_msg)     #alert box
        print(serv_msg)
