import base64
from socket import *
import ssl
import threading
import sqlite3
import json
import datetime
import random
import os
clients = {}

def handle_client(client,addr,chatsocket):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    #cursor.execute("CREATE TABLE Customers(customerUsername text, customerMail text, customerPassword text, customerName text)")
    #cursor.execute("CREATE TABLE Products(owner_name text, product_name text, price real, decription text, image text, quantity int, buyer text)")
    #db.commit()
    
    try:
        while True:
            message=client.recv(1024).decode()
            if message:
                print(f"Recieved this message: {message}")
                if(message=="Register"):
                    username=register(client)
                    clients[username] = chatsocket
                    while True:
                        view_products(client)
                        message=client.recv(1024).decode()
                        print("this is message :",message)
                        if message:
                            if message=="Add product":
                                add_product(client,username)
                            elif message== "Remove product":
                                remove_product(client,username)
                            elif message=="View products of":
                                product_of(client)
                            elif message=="View my customers":
                                my_Customers(username,client)
                            elif message=="Buy product":
                                buy_product(username,client)
                            elif message=="View picture of a specific product of a buyer":
                                picture(client)
                            elif message == "Chat":
                                print(f"[NEW CONNECTION] {addr}: {username} connected.")
                                handlemsg(chatsocket,username,client)
                            elif message=="Logout":
                                 break                
                elif(message=="Login"):
                    username=login(client)
                    clients[username] = chatsocket
                    while True:
                        view_products(client)
                        message=client.recv(1024).decode()
                        print("this is message :",message)
                        if message:
                            if message=="Add product":
                                add_product(client,username)
                            elif message== "Remove product":
                                remove_product(client,username)
                            elif message=="View products of":
                                product_of(client)
                            elif message=="View my customers":
                                my_Customers(username,client)
                            elif message=="View picture of a specific product of a buyer":
                                picture(client)
                            elif message=="Buy product":
                                buy_product(username,client)
                            elif message == "Chat":
                                 print(f"[NEW CONNECTION] {addr}: {username} connected.")
                                 handlemsg(chatsocket,username,client)
                            elif message=="Logout":
                                break
    except Exception as e:
        print(f"Error:{e}")

    finally:

        try:
            if username in clients:
                del clients[username]
            client.close()
            print(f"[DISCONNECTED] {addr} ({username})")
        except Exception as e:
            print(f"Error during cleanup: {e}")
            
def picture(client):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    username=client.recv(1024).decode()
    cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\"")
    x=cursor.fetchone()
    if(x==None):
        client.send("Invalid username".encode())
        while(x==None): 
            username=client.recv(1024).decode()
            cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\"")
            x=cursor.fetchone()
            if(x==None):
                client.send("Invalid username".encode())
            else:
                client.send("Good".encode())
                break
    else:
        client.send("Good".encode())
    
    name=client.recv(1024).decode()
    cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\" and product_name = \"{name}\"")
    x=cursor.fetchone()
    if(x==None):
        client.send("Invalid product".encode())
        while(x==None): 
            name=client.recv(1024).decode()
            cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\" and product_name = \"{name}\"")
            x=cursor.fetchone()
            if(x==None):
                client.send("Invalid product".encode())
            else:
                client.send("Good".encode())  
                break
    else:
        client.send("Good".encode())
    cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\" and product_name=\"{name}\"") 
    image=cursor.fetchone()[4]
    print(image)
    file=open(image,"rb")
    data=file.read()
    size=os.stat(image).st_size
    client.send(str(size).encode())
    client.send(data)
    file.close()

def view_certain_product(username,name):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    cursor.execute(f"SELECT * FROM Products WHERE  product_name = \"{name}\" and quantity > 0")
    x=cursor.fetchone()
    if (x!=None):
        D={}
        i=0
        if(x[0]!=username):
            D["1"]=[(x[0],x[1],x[2],x[3],x[5])]
            i=1;
        while True:
            try:
                x=cursor.fetchone()
                if(x[0]!=username):
                    i+=1
                    D[str(i)]=[(x[0],x[1],x[2],x[3],x[5])]
            except:
                break
        if(D=={}):
            return "No such product"
        d1=json.dumps(D)
        return d1
        
    else:
        return "No such product"

def buy_product(username,client):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
    emaill=cursor.fetchone()[1]
    x="1"
    b=0
    while x=="1":
        client.send("Enter the product you want to buy: ".encode())
        name=client.recv(1024).decode()
        d1=view_certain_product(username,name)
        client.send(d1.encode())
        print(d1)
        if(d1!="No such product"):
            b+=1
            choice=client.recv(1024).decode()
            d1=json.loads(d1)
            z=username
            q=d1[choice][0][4]-1
            n=d1[choice][0][0]
            cursor.execute(f"UPDATE Products SET quantity=\"{q}\", buyer=\"{username}\" WHERE owner_name = \"{n}\" and product_name=\"{name}\"")
            db.commit()
            client.send("Purchased successfully".encode())
            client.send("Do you want to purchase more products? [1: Yes, 2: No]".encode())
            x=client.recv(1024).decode()
        else:
            client.send("Do you want to retry? [1:Yes, 2:No]".encode())
            l=client.recv(1024).decode()
            if(l!="1"):
                break

    email(emaill)   
  
def my_Customers(username,client):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\"")
    x=cursor.fetchone()
    
    if (x!=None):
        cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\"")
        D={}
        while True:
            try:
                u=cursor.fetchone()
                D[u[1]]=u[6]
            except:
                break
        d1=json.dumps(D)
        client.send(d1.encode())
        client.send("Your clients are: ".encode())
    else:
        client.send("You have no products.".encode())
        print("hi")

def product_of(client):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    client.send("Enter the owner name: ".encode())
    username=client.recv(1024).decode()
    cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
    x=cursor.fetchone()
    if (x!=None):
        cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\"")
        x=cursor.fetchone()
        if (x!=None):
            D={}
            D[x[1]]=(str(x[2]),x[3],x[5])
            while True:
                try:
                    u=cursor.fetchone()
                    D[u[1]]=(u[2],u[3],u[5])
                except:
                    break
            d1=json.dumps(D)
            client.send(d1.encode())
        else:
            client.send("This user has no products for sale.".encode())
    else:
        client.send("There is no such user".encode())
        
def view_products(client):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    cursor.execute(f"SELECT * FROM Products Where quantity>0")
    x=cursor.fetchone()
    if (x!=None):
        D={}
        D[x[0]]=[(x[1],x[2],x[3],x[5])]
        while True:
            try:
                u=cursor.fetchone()
                if u[0] in D:
                    D[u[0]].append((u[1],u[2],u[3],u[5]))
                else:
                    D[u[0]]=[(u[1],u[2],u[3],u[5])]
            except:
                break
        d1=json.dumps(D)
        client.send(d1.encode())
    else:
        client.send("No products on the server.".encode())
    
def add_product(client,username):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    client.send("Ready to add".encode())
    product_name1=client.recv(1024).decode()
    cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\" and product_name = \"{product_name1}\"")
    try:
        x=cursor.fetchone()
        if (x[0]==username):
            q=x[5]+1
            cursor.execute(f"UPDATE Products SET quantity=\"{q}\" WHERE owner_name = \"{username}\" and product_name=\"{product_name1}\"")
            db.commit()
            client.send("Quantity was increased successfully".encode())
    except:
        client.send("Insert the price: ".encode())
        price1=client.recv(1024).decode()
        client.send("Add description: ".encode())
        description=client.recv(1024).decode()
        client.send("Add image".encode())
        image=client.recv(1024).decode()
        cursor.execute("INSERT INTO Products values(?,?,?,?,?,?,?)", (username,product_name1,price1,description,"server_"+image,1,"Not bought yet"))
        db.commit()
        cursor.execute("SELECT * FROM Products")
        image_server(client,image)
        print(cursor.fetchall())
        client.send("Product was added successfully".encode())

def image_server(client,image):
    file=open("server_"+image,'wb')
    image_data=client.recv(8000000)
    file.write(image_data)
    file.close()
    

def remove_product(cleint,username):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    client.send("Ready to remove".encode())
    p=client.recv(1024).decode()
    cursor.execute(f"SELECT * FROM Products WHERE owner_name = \"{username}\" and product_name = \"{p}\"")
    db.commit()
    print(p)
    try:
        u=cursor.fetchone()[0]
        if (u==username):
            cursor.execute("DELETE FROM Products WHERE owner_name=username and product_name=p")
            db.commmit()
            client.send("Product removed".encode())
    except:
        client.send("Product not found".encode())

def register(client):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    client.send("Ready to register".encode())
    name=client.recv(1024).decode()
    username=client.recv(1024).decode()
    cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
    try:
        if(cursor.fetchone()[0]==username):
            client.send("Change username".encode())
            x=False
            while(x==False):
                username=client.recv(1024).decode()
                try:
                    cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
                    if(cursor.fetchone()[0]==username):
                        x=False
                        client.send("Change username".encode())
                except:
                    x=True
                    client.send("Okay deal".encode())
    except:
        client.send("All good".encode())
    email=client.recv(1024).decode()
    cursor.execute(f"SELECT * FROM Customers WHERE customerMail = \"{email}\"")
    try:
        if(cursor.fetchone()[1]==email):
            client.send("Another mail".encode())
            p=False
            while(p==False):
                email=client.recv(1024).decode()
                try:
                    cursor.execute(f"SELECT * FROM Customers WHERE customerMail = \"{email}\"")
                    if(cursor.fetchone()[1]==email):
                        client.send("Another mail".encode())
                        p=False
                except:
                    p=True
                    client.send("Okay deal2".encode())
    except:
        client.send("All good".encode())
    password=client.recv(1024).decode()
    cursor.execute("INSERT INTO Customers values(?,?,?,?)", (username,email,password,name))
    db.commit()
    print(username+" is registered")
    client.send("Registration complete".encode())
    cursor.execute(f"SELECT * FROM Customers WHERE customerMail = \"{email}\"")
    return (cursor.fetchone()[0])
    
def login(client):
    db=sqlite3.connect('Customers.db')
    cursor=db.cursor()
    client.send("Ready to login".encode())
    username=client.recv(1024).decode()
    try:
        cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
        if(cursor.fetchone()[0]==username):
            client.send("Correct Username".encode())
    except:
        client.send("Username isnt found".encode())
        x=False
        while(x==False):
            username=client.recv(1024).decode()
            try:
                cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
                if(cursor.fetchone()[0]==username):
                    client.send("Correct Username".encode())
                    x=True
            except:
                client.send("Username isnt found".encode())
                x=False
    password=client.recv(1024).decode()
    try:
        cursor.execute(f"SELECT * FROM Customers WHERE customerPassword = \"{password}\" and customerUsername=\"{username}\"")
        if(cursor.fetchone()[2]==password):
            client.send("Correct Password".encode())
    except:
        client.send("Incorrect Password".encode())
        x=False
        while(x==False):
            password=client.recv(1024).decode()
            try:
                cursor.execute(f"SELECT * FROM Customers WHERE customerPassword = \"{password}\" and customerUsername=\"{username}\"")
                if(cursor.fetchone()[2]==password):
                    client.send("Correct Password".encode())
                    x=True
            except:
                client.send("Incorrect Password".encode())
                x=False
    client.send("Login complete".encode())
    cursor.execute(f"SELECT * FROM Customers WHERE customerUsername = \"{username}\"")
    return (cursor.fetchone()[0])

def cleanup_client(client, username, addr):
    """Clean up client resources"""
    try:
        if username and username in clients:
            del clients[username]
        client.close()
        print(f"[DISCONNECTED] {addr} ({username})")
    except Exception as e:
        print(f"Error during cleanup: {e}")













def handlemsg(chatsocket, name,client):
    print("fetna 3l server")
    client.send("Enter the username you want to chat with: ".encode("utf-8"))
    target_username =client.recv(1024).decode()
    
    if target_username in clients:
        client.send(f"{target_username} is online. Start chatting!".encode("utf-8"))
        target_socket = clients[target_username]
        
        threading.Thread(target=send_messages, args=(chatsocket, target_socket,name)).start()
    else:
        client.send(f"{target_username} is not online.".encode())


def send_messages(sender_socket, receiver_socket,username):
    while True:
        try:
            message = sender_socket.recv(1024).decode()
            if message.lower() == "exit chat":
                sender_socket.send("Ending chat session.".encode())
                receiver_socket.send("Chat ended by the other user.".encode())
                break
            receiver_socket.send(f"Message from {username}: {message+"\n"}".encode())
        except Exception as e:
            print(f"Chat error in sending messages: {e}")
            break
















def email(recemail):
    print("fenta 3al email try")
    mailserver = ("smtp.gmail.com")
    mailport = 587
    clientsocket = socket(AF_INET,SOCK_STREAM)
    clientsocket.connect((mailserver, mailport))
    t = datetime.datetime.today()+datetime.timedelta(10)
    j=t.strftime("%x")
    subject= "purchase of items from AUB bouquet"
    msg =f"\r\n Please collect your items from the AUB Post Office on {j}"
    endmsg = "\r\n.\r\n"
    # Choose a mail server (e.g. Google mail server) and call it mailserver
    fromaddress = "aubpostoffice@gmail.com"  
    toaddress = recemail   
    username = "aubpostoffice@gmail.com" 
    password = "afrn nlcj yelv porf"    



    recv = clientsocket.recv(1024).decode()
    print(recv)
    if recv[:3] != '220':
        print('220 reply not received from server.')

    # Send HELO command and print server response.
    heloCommand = 'HELO Alice\r\n'
    clientsocket.send(heloCommand.encode())
    recv1 = clientsocket.recv(1024).decode()
    print(recv1)
    if recv1[:3] != '250':
        print('250 reply not received from server.')


    clientsocket.send('STARTTLS\r\n'.encode())
    recv = clientsocket.recv(1024).decode()
    print(recv)
    if recv[:3] != '220':
        print('220 reply not received from server.')


    context = ssl.create_default_context()
    secureclientsocket = context.wrap_socket(clientsocket, server_hostname=mailserver)

    authCommand = 'AUTH LOGIN\r\n'
    secureclientsocket.send(authCommand.encode())
    recv = secureclientsocket.recv(1024).decode()
    print(recv)

    secureclientsocket.send(base64.b64encode(username.encode()) + '\r\n'.encode())
    recv = secureclientsocket.recv(1024).decode()
    print(recv)

    secureclientsocket.send(base64.b64encode(password.encode()) + '\r\n'.encode())
    recv = secureclientsocket.recv(1024).decode()
    print(recv)

    # Send MAIL FROM command and print server response.
    mailFromCommand = f'MAIL FROM: <{fromaddress}>\r\n'
    secureclientsocket.send(mailFromCommand.encode())
    recv3 = secureclientsocket.recv(1024).decode()
    print(recv3)
    if recv3[:3] != '250':
        print('250 reply not received from server.')

    # Send RCPT TO command and print server response.
    rcptToCommand = f'RCPT TO: <{toaddress}>\r\n'
    secureclientsocket.send(rcptToCommand.encode())
    recv4 = secureclientsocket.recv(1024).decode()
    print(recv4)
    if recv4[:3] != '250':
        print('250 reply not received from server.')

    # Send DATA command and print server response.
    dataCommand = 'DATA\r\n'
    secureclientsocket.send(dataCommand.encode())
    recv5 = secureclientsocket.recv(1024).decode()
    print(recv5)
    if recv5[:3] != '354':
        print('354 reply not received from server.')

    # Send message data.
    message = f'Subject: {subject}\r\n\r\n{msg}'
    secureclientsocket.send(message.encode())

    # Message ends with a single period.
    secureclientsocket.send(endmsg.encode())
    recv6 = secureclientsocket.recv(1024).decode()
    print(recv6)
    if recv6[:3] != '250':
        print('250 reply not received from server.')

    # Send QUIT command and get server response.
    quitCommand = 'QUIT\r\n'
    secureclientsocket.send(quitCommand.encode())
    recv7 = secureclientsocket.recv(1024).decode()
    print(recv7)
    if recv7[:3] != '221':
        print('221 reply not received from server.')

    secureclientsocket.close()

    













port=int(input("Please enter a Port Number: "))
server=socket(AF_INET,SOCK_STREAM)
server.bind(("127.0.0.1",port))
server.listen(5)
print("Server started listening...")
while True:
    client,addr=server.accept()
    chatsocket,address = server.accept()
    print(f"Accepted connection from {addr}")
    client_thread=threading.Thread(target=handle_client,args=(client,addr,chatsocket))
    client_thread.start()

server.close()

